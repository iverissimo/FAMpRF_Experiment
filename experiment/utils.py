
import numpy as np
import os, sys
import math
from psychopy import visual, tools
import itertools


def jitter(arr,max_val=1,min_val=0.5):

    """ Add random jitter to an array
    
    Parameters
    ----------
    arr : array
        List/array (N,) or (N,2) of values to add jitter to
    max_val : int/float
        maximun amount to add/subtract
    min_val: int/float
        minimum amount to add/subtract
        
    """

    # element positions (#elements,(x,y))
    size_arr = len(arr)

    # add some randomly uniform jitter 
    jit = np.concatenate((np.random.uniform(-max_val,-min_val,math.floor(size_arr * .5)),
                          np.random.uniform(min_val,max_val,math.ceil(size_arr * .5))))
    np.random.shuffle(jit)

    arr += jit

    return(arr)


def near_power_of_2(x,near='previous'):
    """ Get nearest power of 2
    
    Parameters
    ----------
    x : int/float
        value for which we want to find the nearest power of 2
    near : str
        'previous' or 'next' to indicate if floor or ceiling power of 2        
    """
    if x == 0:
        val = 1
    else:
        if near == 'previous':
            val = 2**math.floor(math.log2(x))
        elif near == 'next':
            val = 2**math.ceil(math.log2(x))

    return val


def get_object_positions(grid_pos,bar_midpoint_at_TR, bar_direction_at_TR,
                      bar_width_pix, screen=np.array([1680,1050]), num_bar=1):
    
    """ function to subselect bar positions and
    return bar and background element positions (and number of elements for each object)
    
    Parameters
    ----------
    grid_pos : arr
        numpy array with all possible grid positions (N,2) -> (number of positions, [x,y])
    bar_midpoint_at_TR: arr
        numpy array with mid point position of bar(s) (B,[x,y]) with B=number of bars on screen
    bar_direction_at_TR: arr
        numpy array of strings with bar direction(s) at that TR
    bar_width_pix: arr
        width of bar(s) in pixels for each resolution. 
        If float or array (1,) then same width used for all bars
    num_bar: int
        number of bars to be displayed
                
    """

    # define dictionary to save positions and number of elements
    # of all objects (bar(s) and background)
    output_dict = {}

    if np.isnan(bar_midpoint_at_TR).any():# or np.isnan(bar_direction_at_TR).any(): # when nan, position is whole background

        output_dict['background'] = {'xys': grid_pos, 
                                    'nElements': grid_pos.shape[0]}
    else:

        # make sure "all" inputs are 2d arrays, if not make them. avoids crashing. 
        bar_midpoint_at_TR = np.array(bar_midpoint_at_TR) if len(np.array(bar_midpoint_at_TR).shape)>1 else np.array([bar_midpoint_at_TR])
        bar_direction_at_TR = np.array(bar_direction_at_TR) if len(np.array(bar_direction_at_TR).shape)>0 else np.array([bar_direction_at_TR])
        bar_width_pix = np.array(bar_width_pix)
        
        all_bar_ind = [] # append all bar position indices to later remove from background
 
        if all(x == num_bar for x in [bar_midpoint_at_TR.shape[0], bar_direction_at_TR.shape[0]]):
        
  
            # iterate for number of bars on screen
            for ind in range(num_bar): 

                # first define bar width in pixels (might depend if vertical or horizontal bar pass)
                # and bounds for x and y positions

                if bar_direction_at_TR[ind] in np.array(['L-R','R-L','horizontal']): # if horizontal bar pass

                    x_bounds = np.array([bar_midpoint_at_TR[ind][0] - bar_width_pix[0]/2,
                                         bar_midpoint_at_TR[ind][0] + bar_width_pix[0]/2])
                    y_bounds = np.array([-screen[1]/2,
                                         screen[1]/2])

                elif bar_direction_at_TR[ind] in np.array(['U-D','D-U','vertical']): # if vertical bar pass

                    x_bounds = np.array([-screen[0]/2,
                                         screen[0]/2])
                    y_bounds = np.array([bar_midpoint_at_TR[ind][1] - bar_width_pix[1]/2, 
                                         bar_midpoint_at_TR[ind][1] + bar_width_pix[1]/2])


                # check which grid positions are within bounds for this conditions
                bar_ind = np.where(((grid_pos[...,0]>=min(x_bounds))&
                                    (grid_pos[...,0]<=max(x_bounds))&
                                    (grid_pos[...,1]>=min(y_bounds))&
                                    (grid_pos[...,1]<=max(y_bounds))
                                    ))[0]

                # append to dictionary 
                output_dict['bar%i'%ind] = {'xys': grid_pos[bar_ind], 
                                            'nElements': grid_pos[bar_ind].shape[0]}
                
                for _,p in enumerate(bar_ind):
                    all_bar_ind.append(p)
                
            # make mask to get background positions
            mask = np.ones(len(grid_pos), np.bool)
            mask[all_bar_ind] = 0
            
            output_dict['background'] = {'xys': grid_pos[mask], 
                                         'nElements': grid_pos[mask].shape[0]}

        else:
            raise ValueError('Number of bars different from shape of input arrays')
        

    return(output_dict)


def update_elements(ElementArrayStim, condition_settings, this_phase, elem_positions, grid_pos,
                   	monitor, screen=np.array([1680,1050])):
    
    """ update element array settings
    
    Parameters
    ----------
    ElementArrayStim: Psychopy object
    	ElementArrayStim to be updated 
    condition_settings: dict
        dictionary with all condition settings
    this_phase: str
        string with name of condition to be displayed
    elem_positions: arr
         numpy array with element positions to be updated and shown (N,2) -> (number of positions, [x,y])
         to be used for opacity update
    grid_pos: arr
        numpy array with element positions (N,2) of whole grid -> (number of positions, [x,y])
    monitor: object
        monitor object (to get monitor references for deg2pix transformation)
    screen: arr
        array with display resolution
        
    """
    
    # set number of elements
    nElements = grid_pos.shape[0]

        
    # update element texture
    if this_phase in ('color_green','color_red'):

        # to make colored gabor, need to do it a bit differently (psychopy forces colors to be opposite)
        grat_res = near_power_of_2(ElementArrayStim.sizes[0][0],near='previous') # use power of 2 as grating res, to avoid error
        grating = visual.filters.makeGrating(res=grat_res)

        # initialise a 'black' texture 
        colored_grating = np.ones((grat_res, grat_res, 3)) #* -1.0

        # replace the red/green channel with the grating
        if this_phase == 'color_red': 
            colored_grating[..., 0] = grating 
        else:
            colored_grating[..., 1] = grating 

        elementTex = colored_grating
    else:
        elementTex = 'sin'
    
    
    # update element spatial frequency
    element_sfs = np.ones((nElements)) * condition_settings[this_phase]['element_sf'] # in cycles/gabor width

    # update element orientation (half ori1, half ori2)
    ori_arr = np.concatenate((np.ones((math.floor(nElements * .5))) * condition_settings[this_phase]['element_ori'][0], 
                              np.ones((math.ceil(nElements * .5))) * condition_settings[this_phase]['element_ori'][1]))

    # add some jitter to the orientations
    element_ori = jitter(ori_arr,
                     max_val = condition_settings[this_phase]['ori_jitter_max'],
                     min_val = condition_settings[this_phase]['ori_jitter_min']) 

    np.random.shuffle(element_ori) # shuffle the orientations

    # update element colors 
    element_color = np.ones((int(np.round(nElements)),3)) * np.array(condition_settings[this_phase]['element_color'])

    # update element opacities

    # make grid and element position lists of lists
    list_grid_pos = [list(val) for _,val in enumerate(grid_pos)]
    list_elem_pos = [list(val) for _,val in enumerate(elem_positions)]

    # get indices of where one is in other
    list_indices = [list_grid_pos.index(list_elem_pos[i]) for i in range(len(list_elem_pos))]

    # set element contrasts
    element_contrast =  np.zeros(len(grid_pos))
    element_contrast[list_indices] = condition_settings[this_phase]['element_contrast']
    
    # set opacities
    element_opacities = np.zeros(len(grid_pos))
    element_opacities[list_indices] = 1

    # set all of the above settings
    ElementArrayStim.setTex(elementTex)
    ElementArrayStim.setContrs(element_contrast)
    ElementArrayStim.setSfs(element_sfs)
    ElementArrayStim.setOris(element_ori)
    ElementArrayStim.setColors(element_color)
    ElementArrayStim.setOpacities(element_opacities)


    return(ElementArrayStim)


def get_non_overlapping_indices(arr_shape=[2,8]):
    
    """ get array of indices, that don't overlap
    useful to make sure two bars with same orientation 
    don't overlap spatially
    
    Parameters
    ----------
    arr_shape : list/arr
        shape of indice arr -> [number of bars, number of positions]
        
    """ 
    # initialize empty array
    ind = np.empty((arr_shape[0],), dtype=list)
    
    # get indices for all possible horizontal bar positions
    for w in range(arr_shape[0]):
        ind[w] = np.arange(arr_shape[1])
        np.random.shuffle(ind[w])

        if w>0:
            while any(ind[w-1] == ind[w]): # shuffle until sure that bars in different positions
                np.random.shuffle(ind[w])


    return ind


def set_bar_positions(attend_block_conditions,horizontal_pos,vertical_pos,
                         mini_blocks = 4, num_bars = 4, num_ver_bars = 2, num_hor_bars = 2):
    
    """ set bar positions for all feature trials
    
    Parameters
    ----------
    attend_block_conditions : arr
        array of strings with attended condition for each block (will then be the first condition of each block
        of the return dictionary)
    horizontal_pos: arr
        array of shape (H,2) -> (number of possible horizontal positions, [x,y])
        with midpoint coordinates for horizontal bars
    vertical_pos: arr
        array of shape (V,2) -> (number of possible vertical positions, [x,y])
        with midpoint coordinates for vertical bars
    mini_blocks: int
        number of mini blocks in run
    num_bars: int
        number of bars to be displayed simultaneously
    num_ver_bars: int
        number of vertical bars to be displayed simultaneously
    num_hor_bars:
        number of horizontal bars to be displayed simultaneously
        
    """
    
    # make list of bar conditon names per mini block
    # to associate names to position
    bar_list = np.empty([mini_blocks, num_bars], dtype=list)

    for b in range(mini_blocks):
        # get name of non attended positions for that block
        non_attend_cond = [x for x in attend_block_conditions if x != attend_block_conditions[b]]

        for c in range(num_bars):
            if c == 0:
                bar_list[b][c] = attend_block_conditions[b]
            else:
                bar_list[b][c] = non_attend_cond[c-1]

    # define dictionary to save positions and directions
    # of all bars
    output_dict = {}
    for blk in range(mini_blocks):
        output_dict['mini_block_%i'%blk] = {}
    
    # actually store positions
    for blk in range(mini_blocks):

        # get indices for all possible horizontal and vertical bar positions
        ind_hor = get_non_overlapping_indices(arr_shape=[num_hor_bars,horizontal_pos.shape[0]])
        ind_ver = get_non_overlapping_indices(arr_shape=[num_ver_bars,vertical_pos.shape[0]])

        # define direction of bar (randomly alternate between horizontal and vertical)
        direction = np.concatenate([np.repeat('vertical',horizontal_pos.shape[0]),
                                    np.repeat('horizontal',vertical_pos.shape[0])])
        np.random.shuffle(direction)

        # set opposite direction (to balance conditions)
        opposite_direction = np.array(['vertical' if d=='horizontal' else 'horizontal' for _,d in enumerate(direction)])

        # vertically stack, getting half of bars horizontal, other half vertical
        for j in range(int(len(bar_list[blk])/2)-1):

            direction = np.vstack((direction, direction))
            opposite_direction = np.vstack((opposite_direction, opposite_direction))

        cond_direction = np.vstack((direction,opposite_direction))

        # shuffle columns of direction, to guarantee that each trial has half horizontal, half vertical
        # but without bias of conditions always being one or the other
        [np.random.shuffle(cond_direction[:,j]) for j in range(cond_direction.shape[-1])]

        # first define for all conditions in block, which will be 
        # vertical, which will be horizontal
        for k,cond in enumerate(bar_list[blk]):

            cond_position = []

            # append to dictionary 
            output_dict['mini_block_%i'%blk][cond] = {'bar_midpoint_at_TR': cond_position, 
                                                     'bar_direction_at_TR': cond_direction[k]}  

        # now according to bar direction (horizontal vs vertical)
        # set x,y coordinates for bar midpoint

        for trl in range(cond_direction.shape[-1]): # for each trial
            
            vert_counter = np.repeat(False,num_ver_bars) # set boolean counter, to keep track of positions 
            hor_counter = np.repeat(False,num_hor_bars) 

            for k,cond in enumerate(bar_list[blk]): # iterate per condition
                
                ## if indice arrays empty, get new non-overlapping indices
                if (len(ind_ver[0])==0) and (len(ind_ver[1])==0):
                    ind_ver = get_non_overlapping_indices(arr_shape=[num_ver_bars,vertical_pos.shape[0]])
                elif (len(ind_hor[0])==0) and (len(ind_hor[1])==0):
                    ind_hor = get_non_overlapping_indices(arr_shape=[num_hor_bars,horizontal_pos.shape[0]])
                ##

                # get coordinates for vertical bars
                if output_dict['mini_block_%i'%blk][cond]['bar_direction_at_TR'][trl] == 'vertical':
                    
                    if vert_counter[0] == False: 
                        coord = vertical_pos[ind_ver[0][0]]
                        ind_ver[0] = ind_ver[0][1:] # removed used indice, to not repeat position
                        vert_counter[0] = True
                        
                    elif vert_counter[1] == False: 
                        coord = vertical_pos[ind_ver[1][0]]
                        ind_ver[1] = ind_ver[1][1:] # removed used indice, to not repeat position
                        vert_counter[1] = True
                
                # get coordinates for horizontal bars
                elif output_dict['mini_block_%i'%blk][cond]['bar_direction_at_TR'][trl] == 'horizontal':
                    
                    if hor_counter[0] == False: 
                        coord = horizontal_pos[ind_hor[0][0]]
                        ind_hor[0] = ind_hor[0][1:] # removed used indice, to not repeat position
                        hor_counter[0] = True
                        
                    elif hor_counter[1] == False: 
                        coord = horizontal_pos[ind_hor[1][0]]
                        ind_hor[1] = ind_hor[1][1:] # removed used indice, to not repeat position
                        hor_counter[1] = True
                        
                # now append coordinates to corresponding condition list
                output_dict['mini_block_%i'%blk][cond]['bar_midpoint_at_TR'].append(coord)



    return(output_dict)
    
    




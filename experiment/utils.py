
import numpy as np
import os, sys
import math
import random

from psychopy import visual, tools, colors, event
import itertools

import time


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

    if arr.shape[-1] == 2:
        output = arr + jit[:,None]
    else:
        output = arr + jit
    
    return(output)


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
                   	monitor, screen = np.array([1680,1050]), position_jitter = None, orientation_ind = None, background_contrast = None):
    
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

    # to make colored gabor, need to do it a bit differently (psychopy forces colors to be opposite)
    grat_res = near_power_of_2(ElementArrayStim.sizes[0][0],near='previous') # use power of 2 as grating res, to avoid error
    
    # initialise grating
    grating = visual.filters.makeGrating(res=grat_res)
    grating_norm = (grating - np.min(grating))/(np.max(grating) - np.min(grating)) # normalize between 0 and 1
    
    # initialise a base texture 
    colored_grating = np.ones((grat_res, grat_res, 3)) 

    # replace the base texture red/green channel with the element color value, and the value channel with the grating

    colored_grating[..., 0] = condition_settings[this_phase]['element_color'][0]
    colored_grating[..., 1] = condition_settings[this_phase]['element_color'][1]
    colored_grating[..., 2] = grating_norm * condition_settings[this_phase]['element_color'][2]

    elementTex = colors.hsv2rgb(colored_grating) 

    # update element colors to color of the patch 
    element_color = np.ones((int(np.round(nElements)),3)) 
    
    # update element spatial frequency
    element_sfs = np.ones((nElements)) * condition_settings[this_phase]['element_sf'] # in cycles/gabor width

    # update element orientation (half ori1, half ori2)
    ori_ind = np.array([orientation_ind,orientation_ind]) if orientation_ind != None else np.array([0,1])

    ori_arr = np.concatenate((np.ones((math.floor(nElements * .5))) * condition_settings[this_phase]['element_ori'][ori_ind[0]], 
                              np.ones((math.ceil(nElements * .5))) * condition_settings[this_phase]['element_ori'][ori_ind[1]]))

    # add some jitter to the orientations
    element_ori = jitter(ori_arr,
                     max_val = condition_settings[this_phase]['ori_jitter_max'],
                     min_val = condition_settings[this_phase]['ori_jitter_min']) 

    np.random.shuffle(element_ori) # shuffle the orientations

    # update element opacities

    # make grid and element position lists of lists
    list_grid_pos = [list(val) for _,val in enumerate(grid_pos)]
    list_elem_pos = [list(val) for _,val in enumerate(elem_positions)]

    # get indices of where one is in other
    list_indices = [list_grid_pos.index(list_elem_pos[i]) for i in range(len(list_elem_pos))]

    # set element contrasts
    element_contrast =  np.zeros(len(grid_pos))
    element_contrast[list_indices] = background_contrast if background_contrast != None else condition_settings[this_phase]['element_contrast']
    
    # set opacities
    element_opacities = np.zeros(len(grid_pos))
    element_opacities[list_indices] = 1

    if position_jitter != None: # if we want to add jitter to (x,y) center of elements
        element_pos = jitter(grid_pos,
                            max_val = position_jitter,
                            min_val = 0)

        ElementArrayStim.setXYs(element_pos)

    # set all of the above settings
    ElementArrayStim.setTex(elementTex)
    ElementArrayStim.setContrs(element_contrast)
    ElementArrayStim.setSfs(element_sfs)
    ElementArrayStim.setOris(element_ori)
    ElementArrayStim.setColors(element_color)#, colorSpace='hsv')
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


def repeat_random_lists(arr,num_rep):
    
    """ repeat array, shuffled and stacked horizontally
    
    Parameters
    ----------
    arr : list/arr 
        array to repeat
    num_rep: int
        number of repetions
        
    """ 
    # initialize empty array
    new_arr = np.empty((num_rep,), dtype=list)
    
    # get indices for all possible horizontal bar positions
    for w in range(num_rep):
        random.shuffle(arr)
        new_arr[w] = arr.copy()

    return new_arr


def transform_direction_2_position(direction_array,num_hor_trials=8,num_vert_trials=8, 
                                   num_ver_bars = 2, num_hor_bars = 2):

    """ given a direction array (horizontal/vertical)
    transform it into a position array, guaranteeing that positions
    do not overlap.
    returns 2 arrays with indices, vertical and horizontal
    or empty arrays if non-overlapping requirement not met 
    
    Parameters
    ----------
    direction_array : arr 
        array of arrays, with directions for all conditions and trials (num_cond,trials) -> (4,16)
    num_hor_trials: int
        number of horizontal trials, per condition
    num_vert_trials: int
        number of vertical trials, per condition
    num_ver_bars: int
        number of vertical bars, per trial
    num_hor_bars: int
        number of horizontal bars, per trial
    """ 
    
    # get initial index lists
    cond_ind_hor = get_non_overlapping_indices(arr_shape=[direction_array.shape[0],num_hor_trials])
    cond_ind_ver  = get_non_overlapping_indices(arr_shape=[direction_array.shape[0],num_vert_trials])
    
    # create output arrays, to save indices
    out_ind_hor = np.empty(direction_array.shape, dtype=object) # (4,16)
    out_ind_ver = np.empty(direction_array.shape, dtype=object) # (4,16)

    # counters, for sanity check
    cond_vert_counter = [0, 0, 0, 0]
    cond_hor_counter = [0, 0, 0, 0]
    
    # empty flag
    empty_arr = False
    
    for trl in range(direction_array.shape[1]): # for each trial
        
        vert_counter = np.repeat(False,num_ver_bars) # set boolean counter, to keep track of positions 
        hor_counter = np.repeat(False,num_hor_bars) # for this trial

        for k in range(direction_array.shape[0]): # iterate per condition
            
            if direction_array[k][trl] == 'vertical':
                
                if vert_counter[0] == False: # first condition to be vertical

                    vert_used_index = cond_ind_ver[k][0] # pick index, save in variable because need to compare later
                    vert_counter[0] = True #set counter as true

                elif vert_counter[1] == False: # second condition to be vertical

                    while cond_ind_ver[k][0] == vert_used_index:
                        np.random.shuffle(cond_ind_ver[k]) # shuffle vertical position indexes for that condition, to avoid overlap

                        if len(cond_ind_ver[k]) <= 1:
                            empty_arr = True # return empty array, non-overlapping index condition not met
                            break
                    
                        
                    vert_counter[1] = True
                
                
                out_ind_ver[k][trl] = cond_ind_ver[k][0] # save index
                cond_ind_ver[k] = cond_ind_ver[k][1:] #remove that first position of array, to not repeat
                
                cond_vert_counter[k] += 1 # increment sanity counter
                
            # get coordinates for horizontal bars
            elif direction_array[k][trl] == 'horizontal':

                if hor_counter[0] == False: # first condition to be horizontal

                    hor_used_index = cond_ind_hor[k][0] # pick index, save in variable because need to compare later
                    hor_counter[0] = True

                elif hor_counter[1] == False: # second condition to be horizontal

                    while cond_ind_hor[k][0] == hor_used_index:
                        np.random.shuffle(cond_ind_hor[k]) # shuffle horizontal position indexes for that condition, to avoid overlap

                        if len(cond_ind_hor[k]) <= 1:
                            empty_arr = True # return empty array, non-overlapping index condition not met
                            break

                    hor_counter[1] = True
                
                out_ind_hor[k][trl] = cond_ind_hor[k][0] # save index
                cond_ind_hor[k] = cond_ind_hor[k][1:] # remove that first position of array, to not repeat
                
                cond_hor_counter[k] += 1 # increment sanity counter

    if empty_arr == False:
        # remove Nones
        output_horizontal = np.empty((direction_array.shape[0],), dtype=list)
        output_vertical = np.empty((direction_array.shape[0],), dtype=list)

        for w in range(direction_array.shape[0]):
            output_vertical[w] = np.array([i for _,i in enumerate(out_ind_ver[w]) if i != None])
            output_horizontal[w] = np.array([i for _,i in enumerate(out_ind_hor[w]) if i != None])
    else:
        output_vertical = []
        output_horizontal = []

    return output_vertical,output_horizontal



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

    num_trials = horizontal_pos.shape[0] * vertical_pos.shape[0] # all trials
    num_conditions = horizontal_pos.shape[1] + vertical_pos.shape[1] # all conditions
    
    # actually store positions
    for blk in range(mini_blocks):

        # first define for all conditions in block, which will be 
        # vertical, which will be horizontal
        for k,cond in enumerate(bar_list[blk]):

            cond_position = []

            if 'vertical' in cond:
                cond_direction = np.repeat('vertical',num_trials)
            elif 'horizontal' in cond:
                cond_direction = np.repeat('horizontal',num_trials)

            # append to dictionary 
            output_dict['mini_block_%i'%blk][cond] = {'bar_midpoint_at_TR': cond_position, 
                                                     'bar_direction_at_TR': cond_direction}  

        # now according to bar direction (horizontal vs vertical)
        # set x,y coordinates for bar midpoint

        ## get non overlapping indices for vertical and horizontal bar positions
        # initialize empty lists for indices
        cond_ind_ver = np.empty([num_ver_bars, vertical_pos.shape[0]], dtype=list)
        cond_ind_hor = np.empty([num_hor_bars, horizontal_pos.shape[0]], dtype=list)

        # get non-overlapping indices for vertical, throughout trials
        for v in range(vertical_pos.shape[0]):

            cond_ind_ver[0][v], cond_ind_ver[1][v] = get_non_overlapping_indices(arr_shape=[num_ver_bars,vertical_pos.shape[0]])

        # get non-overlapping indices for horizontal, throughout trials
        hor1, hor2 = get_non_overlapping_indices(arr_shape=[num_hor_bars,horizontal_pos.shape[0]])

        for h in range(len(hor1)):

            cond_ind_hor[0][h] = np.repeat(hor1[h],horizontal_pos.shape[0])
            cond_ind_hor[1][h] = np.repeat(hor2[h],horizontal_pos.shape[0])

        # reshape the indice arrays, and put in new arrays
        ind_ver = np.empty([num_ver_bars, ], dtype=list)
        ind_hor = np.empty([num_hor_bars, ], dtype=list)

        ind_hor[0] = np.concatenate(cond_ind_hor[0]).ravel()
        ind_hor[1] = np.concatenate(cond_ind_hor[1]).ravel()
        ind_ver[0] = np.concatenate(cond_ind_ver[0]).ravel()
        ind_ver[1] = np.concatenate(cond_ind_ver[1]).ravel()

        # make indice array, that is shuffled, to randomly draw positions
        random_ind = np.arange(num_trials)
        np.random.shuffle(random_ind)

        for trl in range(num_trials): # for each trial
    
            vert_bool = False # boolean markers to keep track of conditions
            hor_bool = False

            for k,cond in enumerate(bar_list[blk]): # iterate per condition

                # get coordinates for vertical bars
                if output_dict['mini_block_%i'%blk][cond]['bar_direction_at_TR'][trl] == 'vertical':

                    m = 0 if vert_bool == False else 1
                    coord = vertical_pos[ind_ver[m][random_ind[trl]]] # save coordinates
                    vert_bool = True # update bool marker

                # get coordinates for horizontal bars
                elif output_dict['mini_block_%i'%blk][cond]['bar_direction_at_TR'][trl] == 'horizontal':

                    m = 0 if hor_bool == False else 1
                    coord = horizontal_pos[ind_hor[m][random_ind[trl]]] # save coordinates
                    hor_bool = True # update bool marker

                # now append coordinates to corresponding condition list
                output_dict['mini_block_%i'%blk][cond]['bar_midpoint_at_TR'].append(coord)


    return(output_dict)
    
    
    
def leave_one_out_lists(input_list):

    """ make list of lists, leaving one item out in each iteration
    
    Parameters
    ----------
    input_list : list/arr
        list with all items
            
    """

    out_lists = []
    for x in input_list:
        out_lists.append([y for y in input_list if y != x])

    return out_lists


def get_crossing_positions(position_dictionary,condition_keys,bar_direction_at_TR):

    """ finds positions of crossings between bars and update position dictionary
    
    Parameters
    ----------
    position_dictionary : dict
        dictionary with positions of all bars and background
    condition_keys: arr
        array with names of bar conditions for that miniblock
    bar_direction_at_TR: arr
        bar directions (which are vertical and which are horizontal)
            
    """
    
    # make direction list an array (avoids crashing)
    bar_direction_at_TR = np.array(bar_direction_at_TR)

    # make condition keys in numpy array 
    condition_keys = np.array([cond for _,cond in enumerate(condition_keys)])

    # create new position dictionary, but copying structure of old
    new_position_dictionary = position_dictionary.copy() 

    # get bar key name 
    bar_keys = position_dictionary.keys(); bar_keys = np.array([key for _,key in enumerate(bar_keys) if key != 'background'])

    # get indices for vertical and horizontal bars
    ind_ver = np.where(bar_direction_at_TR=='vertical')[0]
    ind_hor = np.where(bar_direction_at_TR=='horizontal')[0]
    
    # set counter for dictionary key names
    key_counter = 0

    for v in range(len(ind_ver)): # for all vertical bars

        for h in range(len(ind_hor)): # for all horizontal bars

            # get indices where the 2 bars cross, for V and H bar
            # (because also used to mask H and V bars)
            cross_ind_ver = []
            cross_ind_hor = []

            for _,val in enumerate(new_position_dictionary[bar_keys[ind_hor[h]]]['xys']): # get vertical indices

                ind = np.where(np.all(new_position_dictionary[bar_keys[ind_ver[v]]]['xys'] == val, axis=1)==True)[0]

                if ind.size!=0: #if ind list not empty
                    cross_ind_ver.append(ind[0])

            new_position_dictionary['crossing%i'%key_counter] = {'xys': new_position_dictionary[bar_keys[ind_ver[v]]]['xys'][cross_ind_ver], 
                                                                'nElements': len(cross_ind_ver),
                                                                'conditions': np.array([condition_keys[int(bar_keys[ind_hor[h]][-1])],
                                                                                        condition_keys[int(bar_keys[ind_ver[v]][-1])]])}        
            key_counter += 1 # update key name counter

            for _,val in enumerate(new_position_dictionary[bar_keys[ind_ver[v]]]['xys'][cross_ind_ver]): # get horizontal indices

                ind = np.where(np.all(new_position_dictionary[bar_keys[ind_hor[h]]]['xys'] == val, axis=1)==True)[0]

                if ind.size!=0: #if ind list not empty
                    cross_ind_hor.append(ind[0])

            # make bar position masks 
            # for vertical
            mask_ver = np.ones(len(new_position_dictionary[bar_keys[ind_ver[v]]]['xys']), np.bool)
            mask_ver[cross_ind_ver] = 0

            new_position_dictionary[bar_keys[ind_ver[v]]] = {'xys': new_position_dictionary[bar_keys[ind_ver[v]]]['xys'][mask_ver], 
                                                             'nElements': new_position_dictionary[bar_keys[ind_ver[v]]]['xys'][mask_ver].shape[0]}

            # and for horizontal
            mask_hor = np.ones(len(new_position_dictionary[bar_keys[ind_hor[h]]]['xys']), np.bool)
            mask_hor[cross_ind_hor] = 0

            new_position_dictionary[bar_keys[ind_hor[h]]] = {'xys': new_position_dictionary[bar_keys[ind_hor[h]]]['xys'][mask_hor], 
                                                             'nElements': new_position_dictionary[bar_keys[ind_hor[h]]]['xys'][mask_hor].shape[0]}


    return(new_position_dictionary)


def update_crossing_elements(ElementArrayStim, condition_settings, elem_positions,elem_condition_names, nElements,
                            monitor, screen=np.array([1680,1050])):
    
    """ update crossing element array settings
    will be misture of the two conditions that are crossing
    
    Parameters
    ----------
    ElementArrayStim: Psychopy object
        ElementArrayStim to be updated 
    condition_settings: dict
        dictionary with all condition settings
    elem_positions: arr
         numpy array with element positions to be updated and shown (N,2) -> (number of positions, [x,y])
         to be used for opacity update
    elem_condition_names: arr
        array with strings of names of conditions in crossings
    nElements: int
        total number of elements
    monitor: object
        monitor object (to get monitor references for deg2pix transformation)
    screen: arr
        array with display resolution
        
    """
    
    # set texture
    elementTex = 'sin'

    # check how many colors present in crossing
    num_colors = len([True for _,key in enumerate(elem_condition_names) if 'color' in key])
    color_ind = [i for i,s in enumerate(elem_condition_names) if 'color' in s] # find index for color condition

    if num_colors == 1: # if one color, then also change texture

        # to make colored gabor, need to do it a bit differently (psychopy forces colors to be opposite)
        grat_res = near_power_of_2(ElementArrayStim.sizes[0][0],near='previous') # use power of 2 as grating res, to avoid error
        
        # initialise grating
        grating = visual.filters.makeGrating(res=grat_res)
        grating_norm = (grating - np.min(grating))/(np.max(grating) - np.min(grating)) # normalize between 0 and 1
        
        # initialise a base texture 
        colored_grating = np.ones((grat_res, grat_res, 3)) 

        # replace the base texture red/green channel with the element color value, and the value channel with the grating

        colored_grating[..., 0] = condition_settings[elem_condition_names[color_ind[0]]]['element_color'][0]
        colored_grating[..., 1] = condition_settings[elem_condition_names[color_ind[0]]]['element_color'][1]
        colored_grating[..., 2] = grating_norm * condition_settings[elem_condition_names[color_ind[0]]]['element_color'][2]

        elementTex = colors.hsv2rgb(colored_grating) 

        # update element colors to color of the patch 
        element_color = np.ones((int(np.round(nElements)),3)) 

    else: # if 2 colors (or "no" color), mix them 
        element_color = np.concatenate((np.ones((math.floor(nElements * .5),3)) * np.array(colors.hsv2rgb(condition_settings[elem_condition_names[0]]['element_color'])) ,  # red/green
                                        np.ones((math.ceil(nElements * .5),3)) * np.array(colors.hsv2rgb(condition_settings[elem_condition_names[1]]['element_color']))
                                       ))  # red/green


    np.random.shuffle(element_color) # shuffle the colors    

    # update element spatial frequency
    element_sfs = np.concatenate((np.ones((math.floor(nElements * .5))) * condition_settings[elem_condition_names[0]]['element_sf'], 
                                np.ones((math.ceil(nElements * .5))) * condition_settings[elem_condition_names[1]]['element_sf'])) # in cycles/gabor width

    np.random.shuffle(element_sfs) # shuffle the sfs  

    # update element orientation
    if any('color' in s for s in elem_condition_names): # if color, we use orientations of other condition
        ori_ind = np.array([color_ind[0],color_ind[0]])
    else:
        ori_ind = np.array([0,1])

    ori_arr = np.concatenate((np.ones((math.floor(nElements * .5))) * condition_settings[elem_condition_names[ori_ind[0]-1]]['element_ori'][0], 
                              np.ones((math.ceil(nElements * .5))) * condition_settings[elem_condition_names[ori_ind[1]-1]]['element_ori'][1]))

    # add some jitter to the orientations
    element_ori = jitter(ori_arr, max_val = condition_settings[elem_condition_names[ori_ind[0]-1]]['ori_jitter_max'],
                                min_val = condition_settings[elem_condition_names[ori_ind[1]-1]]['ori_jitter_min'])
                                 
    np.random.shuffle(element_ori) # shuffle the orientations

    # set element contrasts
    element_contrast =  np.concatenate((np.ones((math.floor(nElements * .5))) * condition_settings[elem_condition_names[0]]['element_contrast'], 
                                    np.ones((math.ceil(nElements * .5))) * condition_settings[elem_condition_names[1]]['element_contrast']))

    np.random.shuffle(element_contrast) # shuffle the contrasts

    # set all of the above settings
    ElementArrayStim.setTex(elementTex)
    ElementArrayStim.setContrs(element_contrast)
    ElementArrayStim.setSfs(element_sfs)
    ElementArrayStim.setOris(element_ori)
    ElementArrayStim.setColors(element_color)#, colorSpace='hsv')
    ElementArrayStim.setXYs(elem_positions) 


    return(ElementArrayStim)

def gradual_shift(curr_point,
                  end_point = [12, 0.3], intersect = 0,
                  x_step = .5, slope = None, L = 0.3, function = 'logistic'):
    
    """ gradual increase/decrease values according to distribution
    
    Parameters
    ----------
    curr_point : list/array
        [x,y] for the current point to be updated
    end_point : list/array
        [x,y] for the ending point of the function
    intersect : int/float
        point where function intersects y-axis
    x_step : int/float
        time step (granularity) for function
    slope : int/float
        steepness of curve/line
    L : int/float
        curve's maximum value
    function : str
        name of mathematical function to be used (ex: 'linear', 'logistic')
        
    """
    # define x coordinate for next point, given step
    x_next = curr_point[0] + x_step
    
    if function == 'linear':
        
        # define slope for function
        # if not given, calculate the slope of function, given the end point
        k = end_point[1]/end_point[0] if slope == None else slope
        
        # define y coordinates for next point
        y_next = k * x_next + intersect
        
        
    elif function == 'logistic':
        
        # define slope for function
        # if not given, calculate the slope of function, given the end point
        k = 1 if slope == None else slope
        
        # define y coordinates for next point
        y_next = L / (1 + np.exp(-k*(x_next-end_point[0]/2)))
        
    
    # define next point array
    if (x_next >= end_point[0]) or (k > 0 and y_next >= end_point[1]) or (k < 0 and y_next <= end_point[1]): # if endpoint reached             
        # ensure saturation 
        x_next = end_point[0]
        y_next = end_point[1]         
    
        
    return x_next, y_next
    

def draw_instructions(win, instructions, keys = ['b'], visual_obj = [], 
                      color = (1, 1, 1), font = 'Helvetica Neue', pos = (0, 0), height = .65,
                        italic = True, alignHoriz = 'center', alignVert = 'center'):
    
    """ draw instructions on screen
    
    Parameters
    ----------
    win : object
        window object to draw on
    instructions : str
        instruction string to draw 
    key: list
        list of keys to skip instructions
    visual_obj: list
        if not empty, should have psychopy visual objects (to add to the display ex: side rectangles to limit display)
        
    """
    
    text = visual.TextStim(win = win,
                        text = instructions,
                        color = color, 
                        font = font, 
                        pos = pos, 
                        height = height,
                        italic = italic, 
                        alignHoriz = alignHoriz, 
                        alignVert = alignVert
                        )
    
    # draw text again
    text.draw()

    if len(visual_obj)>0:
        for w in range(len(visual_obj)):
            visual_obj[w].draw()
            
    win.flip()

    key_pressed = event.waitKeys(keyList = keys)

    return(key_pressed)





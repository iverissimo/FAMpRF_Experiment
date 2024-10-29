# FAMpRF_Experiment

FAM project pRF mapping experiment stimulus.

## Setting up Environment

This project was developed with Python 3.10 and requires certain packages, such as [exptools2](https://github.com/VU-Cog-Sci/exptools2) (for communication with the eyetracker) and [Psychopy](https://www.psychopy.org/download.html).

To install the necessary dependencies, start by creating a dedicated conda environment from the `environment.yml` file located in the root folder. The first line of the `yml` file sets the new environment's name (default is *FAMexperiment*). 

```
conda env create -f environment.yml
conda activate FAMexperiment
```

If you do not have the `exptools` folder installed in your local machine, clone the repository and manually install the package. 

**WARNING**: do not install `exptools` within this project repository! Choose a different location to avoid conflicts.


```
conda activate FAMexperiment
git clone https://github.com/VU-Cog-Sci/exptools2.git
cd exptools2
python setup.py install
```

After following these steps, you should be set to go!

## Running Experiments

To run a session, you need to call the `main.py` script located in the `experiment` folder:

```
conda activate FAMexperiment
cd experiment
python main.py <sub_num> <run_num>
```

Where `<sub_num>` is the participant ID and `<run_num>` is the fMRI task run ID. Both values should be integers (e.g.: `python main.py 1 1`).

After running the above code lines, you will be prompted to choose which of the 3 available tasks you would like to run in this session: `flicker`, `standard` or `feature`. For more details on the different tasks, please check the subsequent sections.

After running the experiment, the task files (like log files, events, etc) will be stored in the newly created `output` folder, located in the root folder. The files will be named according to the [BIDS](https://bids.neuroimaging.io/) convention (e.g.: `output/sourcedata/sub-001/sub-001_ses-1_task-pRF_run-1_events.tsv`).

*Note* - If you want to store the output files in a different directory, you can do so by replacing `base_dir = '/new/output/path'` in `FAMpRF_Experiment/experiment/main.py`.


### Flicker Task

When selecting the `flicker` task, the code will run a [flicker fusion threshold](https://en.wikipedia.org/wiki/Flicker_fusion_threshold) paradigm. This is a color luminance matching task, where participants are asked to fixate the center of the screen while adjusting the color luminance value of a flickering concentric square ring. The stimuli colors are matched (isoluminant) when the ring does not appear to flicker anymore.

<p align="center">
  <video autoplay loop muted src="https://github.com/user-attachments/assets/4dde1113-759a-4eb1-bd42-33d59042379c" width="500px"></video>
</p>

After running a `flicker` session, several `yml` files will be stored in the `output` folder. These contain the isoluminant stimuli color values which will then be averaged per participant, replacing the default color settings in the main experimental tasks (`standard` and `feature`). 

### pRF Mapping Task

When selecting the `standard` task, the code will run a [population receptive field (pRF) mapping](https://pmc.ncbi.nlm.nih.gov/articles/PMC3073038/) task. In this task, a flickering bar stimulus moves across the display in different cardinal directions. Participants are asked to fixate the center of the screen, and indicate the bar color (green/red) at every step via button-press.

<p align="center">
  <video autoplay loop muted src="https://github.com/user-attachments/assets/a1ce43f9-1c5a-410e-b90e-af029553b6be" width="500px"></video>
</p>

After running a `standard` session, different files will be stored in the `output` folder:

- `sub-<sub_num>_ses-1_task-pRF_run-<run_num>_expsettings.yml` with the main experimental settings used (e.g.: stimuli color values, screen resolution, number of trials, etc)
- `sub-<sub_num>_ses-1_task-pRF_run-<run_num>_events.tsv` events dataframe with information on stimulus timing and participant response
- `sub-<sub_num>_ses-1_task-pRF_run-<run_num>_log.txt` logfile with extra information for bookeeping

### Feature Attention Task

When selecting the `feature` task, the code will run a feature-based attention mapping task. In this task, participants are asked to detect and respond to a target bar stimulus, whilst ignoring the competing distractor bar. The two stimuli differ in color (red vs green), and the target-defining color is cued at the start of each run. The goal is to indicate the exact hue of the target bar (pink/orange for red bars or blue/yellow for green bars) as quickly as possible via button-press, while keeping fixation at the center of the screen.

<p align="center">
  <video autoplay loop muted src="https://github.com/user-attachments/assets/169eb9cc-8c4e-440e-8991-621cad9eaf79" width="500px"></video>
</p>

After running a `feature` session, different files will be stored in the `output` folder:

- `sub-<sub_num>_ses-1_task-FA_run-<run_num>_expsettings.yml` with the main experimental settings used (e.g.: stimuli color values, screen resolution, number of trials, etc)
- `sub-<sub_num>_ses-1_task-FA_run-<run_num>_events.tsv` events dataframe with information on stimulus timing and participant response
- `sub-<sub_num>_ses-1_task-FA_run-<run_num>_trial_info.csv` task specific information on the trial order, and identity of each bar stimulus
- `sub-<sub_num>_ses-1_task-FA_run-<run_num>_bar_positions.pkl` pickle file with the screen coordinates (in pix) for the different stimuli and their relative spatial configurations
- `sub-<sub_num>_ses-1_task-FA_run-<run_num>_log.txt` logfile with extra information for bookeeping



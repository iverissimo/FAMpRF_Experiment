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

After running the experiment, the task files (like log files, events, etc) will be stored in the newly created `output` folder, located in the root folder. The files will be named according to the BIDS convention (e.g.: `output/sourcedata/sub-001/sub-001_ses-1_task-pRF_run-1_events.tsv`).

*Note* - If you want to store the output files in a different directory, you can do so by replacing `base_dir = '/new/output/path'` in `FAMpRF_Experiment/experiment/main.py`.


### Flicker Task

<p align="center">
  <video src="https://github.com/user-attachments/assets/4dde1113-759a-4eb1-bd42-33d59042379c" width="500px"></video>
</p>

### pRF Mapping Task

### Feature Attention Task



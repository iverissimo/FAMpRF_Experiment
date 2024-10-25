# FAMpRF_Experiment

FAM project pRF mapping experiment stimulus.

## Setting up Environment

This project was developed with Python 3.10 and requires certain packages, such as [exptools2](https://github.com/VU-Cog-Sci/exptools2) (for communication with the eyetracker) and Psychopy.

First, start by creating a dedicated conda environment from the `environment.yml` file located in the root folder. The first line of the `yml` file sets the new environment's name (default is *FAMexperiment*). 

```
conda env create -f environment.yml
conda activate FAMexperiment

```

If you do not have the `exptools` folder installed in your local machine, clone the repository and manually install the package. **WARNING**: do not install `exptools` within this project repository! Chose a different location to avoid conflicts.


```
conda activate FAMexperiment
git clone https://github.com/VU-Cog-Sci/exptools2.git
cd exptools2
python setup.py install

```

After following these steps, you should be set to go!

## Project Structure

## Running Experiments

### Flicker Task

### pRF Mapping Task

### Feature Attention Task



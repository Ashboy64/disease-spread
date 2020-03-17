# disease-spread

Repo to simulate spread of disease through a neighborhood.

## Usage

`configurator.py` provides functionality to configure the initial state of the simulation, `main.py` allows you to run it, and `plot.py` allows you to plot and analyze results. Before going forwards, ensure that you have python 3 and the required libraries installed.

Recommended steps:
- Install Anaconda (python 3) and create a virtualenv (optional)
- Inside virtualenv, run command `pip install -r requirements.txt`

### Configure Initial State of Simulation

Run `python configurator.py`. Clicking on a square cycles through its state, and the gray button in the bottom toolbar saves and closes. Run `python main.py -h` to see more options like where to save configuration.

### Run Simulation

Run `python main.py --render`. If want to specify directory to log results to, `python main.py --log_path=[INSERT_PATH] --render`. Run `python main.py -h` for more options

### Plot Results

To plot results: `python plot.py --log_path=[INSERT_PATH]`

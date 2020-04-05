# disease-spread

Repo to simulate spread of disease through a population. Based on: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6926909/

Note that I am not an epidemiologist! Also, the parameters for the simulation are not yet tuned to simulate the spread of any specific disease, but I'm working on getting the simulation to match data seen on the spread of COVID-19.

## Usage

`configurator.py` provides functionality to configure the initial state of the simulation, `main.py` allows you to run it, and `plot.py` allows you to plot and analyze results. Before going forward, ensure that you have python 3 and the required libraries installed.

Recommended steps:
- Install Anaconda (python 3) and create a virtualenv
- Inside virtualenv, run command `pip install -r requirements.txt`

### Configure Initial State of Simulation (Optional)

If you want, you can run `python configurator.py` to set and save initial parameters for the simulation. Note that the 'num_samples' option allows you to set the number of cells that will initially be infected, and the program will randomly sample that number of cells. If set to zero, you can manually specify which cells will be in what states.

When you are specifying the states of specific cells, you can click on cells to cycle through their possible states. When done setting the initial configuration here, hit the gray button on the bottom left of the window to save the config.

![Image](assets/configurator.gif?raw=true)

### Run Simulation

Run `python main.py`. You can specify a configuration to load from (input the name of the directory that the config was saved to), in which case the simulation will load all the parameters from the specified config. You can select render in order to see the simulation in real time. You can also specify a specific directory to log to.

![Image](assets/main.gif?raw=true)

### Plot Results

To plot results, run `python plot.py --log_path=[DIR_NAME]` where `[DIR_NAME]` specifies the directory where the log files of the simulation are located. Sample plot:

![Image](assets/plot.gif?raw=true)

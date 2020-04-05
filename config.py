import ruamel.yaml
import os
from datetime import datetime

class ConfigLogger(object):
    """Save and load configurations for simulation."""

    def __init__(self, sim):
        super(ConfigLogger, self).__init__()

        self.yaml = ruamel.yaml.YAML()
        self.yaml.version = (1,2)
        self.yaml.default_flow_style = None
        self.sim = sim

    def save_curr_config(self, path):
        states_list = []
        for row in range(len(self.sim.cell_list)):
            states_list.append([cell.state for cell in self.sim.cell_list[row]])

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            to_dump = self.sim.get_config_no_grid()
            to_dump["grid"] = states_list
            data = self.yaml.dump(to_dump, f)

    def load_config(self, path):
        f = open(path, 'r')
        data = self.yaml.load(f)

        self.sim.set_params_from_config(data['params'])
        self.sim.set_props_from_config(data['props'])
        self.sim.set_settings_from_config(data['settings'])
        self.sim.init_cells()

        grid = data["grid"]

        for row in range(len(self.sim.cell_list)):
            for col in range(len(self.sim.cell_list[row])):
                try:
                    self.sim.cell_list[row][col].state = grid[row][col]
                except:
                    print(str(row) + ", " + str(col))

if __name__ == '__main__':
    from main import SimulationWindow
    window = SimulationWindow(os.path.join("logs", datetime.now().strftime("%d_%m_%Y_%H_%M_%S")), 1500)
    c = ConfigLogger(window)
    c.save_curr_config("configs/example_config.yml")
    c.load_config("configs/example_config.yml")

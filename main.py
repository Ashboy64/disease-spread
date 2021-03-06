import pyglet
import numpy as np
import argparse
import os
from pyglet.window import mouse
from datetime import datetime
from config import ConfigLogger
from gooey import Gooey

class Cell(object):
    """Cell representing a human in the simulation"""

    def __init__(self, x, y, cell_size, resistance, ratio=0.85):
        super(Cell, self).__init__()
        self.state = 1 # {1: susceptible, 2: Latent, 3: Infected, 4: Recovered, 0: Dead/inactive}
        self.cell_size = cell_size
        self.size = cell_size*ratio
        self.pos = (x, y) # Lower left
        self.resistance = resistance # The T_C(i,j) parameter
        self.color = 255
        self.time_counter = 0

    def get_color(self):
        if self.state == 1:
            return [self.color for i in range(12)]
        elif self.state == 3:
            return [255,0,0 , 255,0,0 , 255,0,0 , 255,0,0]
        elif self.state == 2:
            return [240,240,0 , 240,240,0 , 240,240,0 , 240,240,0]
        elif self.state == 4:
            return [0,255,0 , 0,255,0 , 0,255,0 , 0,255,0]
        return [0 for i in range(12)]

    def set_state(self, state):
        self.state = state
        self.time_counter = 0

    def draw(self):
        x, y = self.pos
        offset = (self.cell_size - self.size)/2
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
            [x + offset, y + offset, x + self.cell_size - offset, y + offset, x + self.cell_size - offset, y + self.cell_size - offset,
            x + offset, y + self.cell_size - offset]), ('c3B', self.get_color()))

    def add_to_batch(self, batch):
        x, y = self.pos
        offset = (self.cell_size - self.size)/2
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f',
            [x + offset, y + offset, x + self.cell_size - offset, y + offset, x + self.cell_size - offset, y + self.cell_size - offset,
            x + offset, y + self.cell_size - offset]), ('c3B', self.get_color()))

class SimulationWindow(pyglet.window.Window):
    """The window displaying the simulation"""

    def __init__(self, log_path, run_time, render, toolbar_size=40, cell_size=20, width=640, height=640, load_path=""):
        super(SimulationWindow, self).__init__(width, height)

        self.run_time = run_time
        self.render = render

        if not render:
            super(SimulationWindow, self).close()

        self.config_logger = ConfigLogger(self)
        if load_path != "":
            self.config_logger.load_config(os.path.join(load_path, "config.yml"))
        else:
            self.width = width
            self.height = height + toolbar_size
            self.modified_height = height

            self.toolbar_size = toolbar_size

            self.pause_bl_x = 20
            self.pause_bl_y = toolbar_size*(1/5)

            self.init_props()
            self.init_time_params()

            self.cell_size = cell_size
            self.cell_list = []
            self.init_cells()

        self.running = True
        os.makedirs(log_path, exist_ok=True)
        self.f = open(os.path.join(log_path, "log.csv"), "w")
        self.f.write("susceptible,latent,infected,recovered,dead\n")

    def add_toolbar_to_batch(self, batch):
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f',
            [0, 0, self.width, 0, self.width, self.toolbar_size,
            0, self.toolbar_size]), ('c3B', [130 for i in range(12)]))

        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f',
            [self.pause_bl_x, self.pause_bl_y, 5*self.pause_bl_x, self.pause_bl_y, 5*self.pause_bl_x, self.pause_bl_y + (self.toolbar_size*3/5),
            self.pause_bl_x, self.pause_bl_y + (self.toolbar_size*3/5)]), ('c3B', [200 for i in range(12)]))

    def init_time_params(self):
        self.max_latent = 5
        self.max_infected = 22
        self.prob_death = 0.01/22
        self.max_immune = 5
        self.max_movement_radius = 2
        self.movement_prob = 0.05

    def init_props(self):
        self.mf_prop = [0.5, 0.5] # Proportion of males and females in the population
        self.mf_influence = [0.5, 0.5] # Influence coefficent for males and females

        self.age_prop = [1/5 for i in range(5)]
        self.age_influence = [1/5 for i in range(5)]

        self.expected_resistance = np.array(self.mf_prop).dot(self.mf_influence) * np.array(self.age_prop).dot(self.age_influence)

    def get_config_no_grid(self):
        params = {"max_latent" : self.max_latent, "max_infected" : self.max_infected, "prob_death" : self.prob_death, "max_immune" : self.max_immune,
            "max_movement_radius" : self.max_movement_radius, "movement_prob" : self.movement_prob}
        props = {"mf_prop" : self.mf_prop, "mf_influence" : self.mf_influence, "age_prop" : self.age_prop, "age_influence" : self.age_influence,
            "expected_resistance" : self.expected_resistance}
        settings = {"cell_size" : self.cell_size, "width" : self.width, "height" : self.height, "modified_height" : self.modified_height,
            "toolbar_size" : self.toolbar_size, "pause_bl_x" : self.pause_bl_x, "pause_bl_y" : self.pause_bl_y}
        props = {k: str(v) for k,v in props.items()}
        return {"params" : params, "props" : props, "settings" : settings}

    def set_params_from_config(self, params):
        self.max_latent = params["max_latent"]
        self.max_infected = params["max_infected"]
        self.prob_death = params["prob_death"]
        self.max_immune = params["max_immune"]
        self.max_movement_radius = params["max_movement_radius"]
        self.movement_prob = params["movement_prob"]

    def set_props_from_config(self, props):
        self.mf_prop = props["mf_prop"][1:-1].split(", ")
        self.mf_prop = [float(s) for s in self.mf_prop]

        self.mf_influence = props["mf_influence"][1:-1].split(", ")
        self.mf_influence = [float(s) for s in self.mf_influence]

        self.age_prop = props["age_prop"][1:-1].split(", ")
        self.age_prop = [float(s) for s in self.age_prop]

        self.age_influence = props["age_influence"][1:-1].split(", ")
        self.age_influence = [float(s) for s in self.age_influence]

        self.expected_resistance = float(props["expected_resistance"])

    def set_settings_from_config(self, settings):
        self.cell_size = settings["cell_size"]
        self.width = settings["width"]
        self.height = settings["height"]
        self.modified_height = settings["modified_height"]
        self.toolbar_size = settings["toolbar_size"]
        self.pause_bl_x = settings["pause_bl_x"]
        self.pause_bl_y = settings["pause_bl_y"]

    def init_cells(self):
        self.cell_list = []
        for row in range(int(self.modified_height/self.cell_size)):
            self.cell_list.append([Cell(self.cell_size*col, self.cell_size*row + self.toolbar_size, self.cell_size, self.expected_resistance*np.random.uniform())
                for col in range(int(self.width/self.cell_size))])

        for i in range(1):
            r = np.random.randint(len(self.cell_list))
            c = np.random.randint(len(self.cell_list[0]))
            self.cell_list[r][c].set_state(3) # For testing purposes; the one person that is infected in the population at the start

    def prob_infection(self, row, col):
        a = 1.625 # Infection through diagonal
        b = 1.625 # Infection through vertical/horizontal

        diag_sum = 0
        adj_sum = 0

        above_exists = (row < (len(self.cell_list) - 1)) # Can address (r+1, .)
        below_exists = (row > 0) # Can address (r-1, .)

        right_exists = (col < (len(self.cell_list[0]) - 1)) # Can address (., c+1)
        left_exists = (col > 0) # Can address (., c-1)

        if above_exists:
            # (r+1, col-1), (r+1, col), (r+1, col+1)
            if self.cell_list[row+1][col].state == 3:
                adj_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r+1, col)

            if left_exists:
                if self.cell_list[row+1][col-1].state == 3:
                    diag_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r+1, col-1)
            if right_exists:
                if self.cell_list[row+1][col+1].state == 3:
                    diag_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r+1, col+1)

        if below_exists:
            # (r-1, col-1), (r-1, col), (r-1, col+1)
            if self.cell_list[row-1][col].state == 3:
                adj_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r-1, col)

            if left_exists:
                if self.cell_list[row-1][col-1].state == 3:
                    diag_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r-1, col-1)
            if right_exists:
                if self.cell_list[row-1][col+1].state == 3:
                    diag_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r-1, col+1)

        if right_exists:
            if self.cell_list[row][col+1].state == 3:
                adj_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r, col+1)
        if left_exists:
            if self.cell_list[row][col-1].state == 3:
                adj_sum += np.sqrt(np.random.uniform()*(1-self.cell_list[row][col].resistance)) # (r, col-1)

        return (a/4)*diag_sum + (b/4)*adj_sum

    def infection_step(self):
        n_sus = 0
        n_latent = 0
        n_infected = 0
        n_dead = 0
        n_recovered = 0

        to_move = [] # Keeps track of cells that will move in the movement step

        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                if np.random.uniform() < self.movement_prob:
                    to_move.append((row, col))
                if (self.cell_list[row][col].state == 1) and (np.random.uniform() < self.prob_infection(row, col)):
                    self.cell_list[row][col].set_state(2)
                    n_latent+=1
                elif (self.cell_list[row][col].state == 1):
                    n_sus+=1
                elif self.cell_list[row][col].state == 2:
                    if self.cell_list[row][col].time_counter > self.max_latent:
                        self.cell_list[row][col].set_state(3)
                        n_infected+=1
                    else:
                        self.cell_list[row][col].time_counter += 1
                        n_latent+=1
                elif self.cell_list[row][col].state == 3:
                    if self.cell_list[row][col].time_counter > self.max_infected:
                        self.cell_list[row][col].set_state(4)
                        n_recovered+=1
                    else:
                        if np.random.uniform() < self.prob_death:
                            self.cell_list[row][col].set_state(0)
                            n_dead+=1
                        else:
                            self.cell_list[row][col].time_counter += 1
                            n_infected+=1
                elif self.cell_list[row][col].state == 4:
                    if self.cell_list[row][col].time_counter > self.max_immune:
                        self.cell_list[row][col].set_state(1)
                        n_sus+=1
                    else:
                        self.cell_list[row][col].time_counter += 1
                        n_recovered+=1
                elif self.cell_list[row][col].state == 0:
                    n_dead+=1

        self.f.write(",".join([str(n_sus), str(n_latent), str(n_infected), str(n_recovered), str(n_dead)]))
        self.f.write("\n")

        return to_move

    def movement_step(self, to_move):
        for cell_pos in to_move:
            r, c = cell_pos
            new_r, new_c = list(np.random.randint(low=-self.max_movement_radius, high=self.max_movement_radius, size=2))

            new_r += r
            new_c += c
            new_r = min(max(0, new_r), len(self.cell_list)-1)
            new_c = min(max(0, new_c), len(self.cell_list)-1)

            cell = self.cell_list[r][c]
            self.cell_list[r][c] = self.cell_list[new_r][new_c]
            self.cell_list[new_r][new_c] = cell

    def on_draw(self):
        self.clear()
        if self.render:
            batch = pyglet.graphics.Batch()
            for row in range(len(self.cell_list)):
                for col in range(len(self.cell_list[row])):
                    self.cell_list[row][col].add_to_batch(batch)

            self.add_toolbar_to_batch(batch)

            batch.draw()

    def update(self, dt):
        if self.running:
            if self.run_time == 0:
                self.close()
            else:
                to_move = self.infection_step()
                self.movement_step(to_move)
                self.run_time-=1

    def on_mouse_press(self, x, y, button, modifiers):
        if (self.pause_bl_x <= x) and (x <= 5*self.pause_bl_x) and (self.pause_bl_y <= y) and (y <= self.pause_bl_y + (self.toolbar_size*3/5)):
            self.running = not self.running

    def callback(self, dt):
        print(f"{dt} seconds since last callback")

    def close(self):
        super(SimulationWindow, self).close()
        self.f.close()

def main():
    parser = argparse.ArgumentParser(description='Simulate disease spread.')
    parser.add_argument("--log_path", type=str, help='path to log simulation results', default=os.path.join("logs", datetime.now().strftime("log_%d_%m_%Y_%H_%M_%S")))
    parser.add_argument("--timesteps", type=int, help='timesteps to run simulation', default=1500)
    parser.add_argument("--init_config", type=str, help='path to init config file', default="")
    parser.add_argument("--render", help='render simulation', default=False, action="store_true")
    parser.add_argument("--width", type=int, help='width of simulation window', default=32*20)
    parser.add_argument("--height", type=int, help='height of simulation window', default=32*20)

    args = parser.parse_args()
    print("Logging to: " + args.log_path)

    # 549*20 = 10980 for Italy simulation
    window = SimulationWindow(args.log_path, args.timesteps, args.render, width=args.width, height=args.height, load_path=args.init_config)
    if args.render:
        pyglet.clock.schedule_interval(window.update, 1/60)
        pyglet.app.run()
    else:
        for i in range(args.timesteps):
            window.update(0)
        window.f.close()

if __name__ == '__main__':
    Gooey(main)()

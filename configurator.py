import pyglet
import argparse
import os
import numpy as np
from main import Cell
from datetime import datetime
from config import ConfigLogger

class Configurator(pyglet.window.Window):
    """Window to create the starting point for the simulation"""

    def __init__(self, save_path, width=640, height=640, toolbar_size=40, cell_size=20):
        super(Configurator, self).__init__(width, height + toolbar_size)

        self.save_path = save_path
        self.config_logger = ConfigLogger(save_path)
        self.modified_height = height

        self.toolbar_size = toolbar_size

        self.pause_bl_x = 20
        self.pause_bl_y = toolbar_size*(1/5)

        self.init_props()
        self.init_time_params()

        self.cell_size = cell_size
        self.cell_list = []
        self.init_cells()

    def init_time_params(self):
        self.max_latent = 10
        self.max_infected = 20
        self.prob_death = 0.01/20
        self.max_immune = 5

    def init_props(self):
        self.mf_prop = [0.5, 0.5] # Proportion of males and females in the population
        self.mf_influence = [0.5, 0.5] # Influence coefficent for males and females

        self.age_prop = [1/5 for i in range(5)]
        self.age_influence = [1/5 for i in range(5)]

        self.expected_resistance = np.array(self.mf_prop).dot(self.mf_influence) * np.array(self.age_prop).dot(self.age_influence)

    def init_cells(self):
        self.cell_list = []
        for row in range(int(self.modified_height/self.cell_size)):
            self.cell_list.append([Cell(self.cell_size*col, self.cell_size*row + self.toolbar_size, self.cell_size, self.expected_resistance*np.random.uniform())
                for col in range(int(self.width/self.cell_size))])

        self.cell_list[np.random.randint(len(self.cell_list))][np.random.randint(len(self.cell_list[0]))].set_state(3)

    def add_toolbar_to_batch(self, batch):
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f',
            [0, 0, self.width, 0, self.width, self.toolbar_size,
            0, self.toolbar_size]), ('c3B', [130 for i in range(12)]))

        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f',
            [self.pause_bl_x, self.pause_bl_y, 5*self.pause_bl_x, self.pause_bl_y, 5*self.pause_bl_x, self.pause_bl_y + (self.toolbar_size*3/5),
            self.pause_bl_x, self.pause_bl_y + (self.toolbar_size*3/5)]), ('c3B', [200 for i in range(12)]))

    def on_draw(self):
        self.clear()
        batch = pyglet.graphics.Batch()
        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                self.cell_list[row][col].add_to_batch(batch)

        self.add_toolbar_to_batch(batch)

        batch.draw()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create initial config for a simulation.')
    parser.add_argument("--save_path", type=str, help='path to save config', default=os.path.join("configs", datetime.now().strftime("config_%d_%m_%Y_%H_%M_%S")))

    args = parser.parse_args()
    print("Saving to: " + args.save_path)

    c = Configurator(args.save_path)
    pyglet.app.run()

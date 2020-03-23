import pyglet
import argparse
import os
import numpy as np
from main import Cell
from datetime import datetime
from config import ConfigLogger
from gooey import Gooey

class Configurator(pyglet.window.Window):
    """Window to create the starting point for the simulation"""

    def __init__(self, save_path, width=640, height=640, toolbar_size=40, cell_size=20):
        super(Configurator, self).__init__(width, height + toolbar_size)

        self.save_path = save_path
        self.config_logger = ConfigLogger(self)
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
        self.max_movement_radius = 2
        self.movement_prob = 0.05

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

    def get_config_no_grid(self):
        params = {"max_latent" : self.max_latent, "max_infected" : self.max_infected, "prob_death" : self.prob_death, "max_immune" : self.max_immune,
            "max_movement_radius" : self.max_movement_radius, "movement_prob" : self.movement_prob}
        props = {"mf_prop" : self.mf_prop, "mf_influence" : self.mf_influence, "age_prop" : self.age_prop, "age_influence" : self.age_influence,
            "expected_resistance" : self.expected_resistance}
        settings = {"cell_size" : self.cell_size, "width" : self.width, "height" : self.height, "modified_height" : self.modified_height,
            "toolbar_size" : self.toolbar_size, "pause_bl_x" : self.pause_bl_x, "pause_bl_y" : self.pause_bl_y}
        props = {k: str(v) for k,v in props.items()}
        return {"params" : params, "props" : props, "settings" : settings}

    def add_toolbar_to_batch(self, batch):
        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f',
            [0, 0, self.width, 0, self.width, self.toolbar_size,
            0, self.toolbar_size]), ('c3B', [130 for i in range(12)]))

        batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f',
            [self.pause_bl_x, self.pause_bl_y, 5*self.pause_bl_x, self.pause_bl_y, 5*self.pause_bl_x, self.pause_bl_y + (self.toolbar_size*3/5),
            self.pause_bl_x, self.pause_bl_y + (self.toolbar_size*3/5)]), ('c3B', [200 for i in range(12)]))

        label = pyglet.text.Label('Save',
                          font_name='Arial',
                          font_size=36,
                          x=self.pause_bl_x, y=self.pause_bl_y,
                          anchor_x='left', anchor_y='bottom', batch=batch, color=(0, 0, 0, 255))
        while label.content_width > 4*self.pause_bl_x or label.content_height > self.toolbar_size*3/5:
            label.font_size-=1

    def on_mouse_press(self, x, y, button, modifiers):
        # Get the cell that was clicked
        col = x // self.cell_size
        row = (y - self.toolbar_size) // self.cell_size

        if (row >= 0) and (row < int(self.modified_height/self.cell_size)) and (col >= 0) and (col < int(self.width/self.cell_size)):
            self.cell_list[row][col].state += 1
            self.cell_list[row][col].state %= 5

        if (self.pause_bl_x <= x) and (x <= 5*self.pause_bl_x) and (self.pause_bl_y <= y) and (y <= self.pause_bl_y + (self.toolbar_size*3/5)):
            self.config_logger.save_curr_config(os.path.join(self.save_path, "config.yml"))
            super(Configurator, self).close()

    def on_draw(self):
        self.clear()
        batch = pyglet.graphics.Batch()
        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                self.cell_list[row][col].add_to_batch(batch)

        self.add_toolbar_to_batch(batch)

        batch.draw()

@Gooey
def main():
    parser = argparse.ArgumentParser(description='Create initial config for a simulation.')
    parser.add_argument("--save_path", type=str, help='path to save config', default=os.path.join("configs", datetime.now().strftime("config_%d_%m_%Y_%H_%M_%S")))
    parser.add_argument("--cell_size", type=int, help='size of each cell', default=20)
    parser.add_argument("--num_cells_height", type=int, help='number of cells per column', default=32)
    parser.add_argument("--num_cells_width", type=int, help='number of cells per row', default=32)

    args = parser.parse_args()
    print("Saving to: " + args.save_path)

    c = Configurator(args.save_path, cell_size=args.cell_size, width=args.num_cells_width*args.cell_size, height=args.num_cells_height*args.cell_size)
    pyglet.app.run()

if __name__ == '__main__':
    main()

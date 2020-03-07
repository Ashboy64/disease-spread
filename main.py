import pyglet
import numpy as np

class Cell(object):
    """Cell representing a human in the simulation"""

    def __init__(self, x, y, cell_size, resistance, ratio=0.85):
        super(Cell, self).__init__()
        self.state = 1 # {1: susceptible, 2: Latent, 3: Infected, 4: Recovered, 5: Dead/inactive}
        self.cell_size = cell_size
        self.size = cell_size*ratio
        self.pos = (x, y) # Lower left
        self.resistance = resistance # The T_C(i,j) parameter
        self.color = 255

    def get_color(self):
        if self.state == 1:
            return [self.color for i in range(12)]
        else:
            return [255,0,0 , 255,0,0 , 255,0,0 , 255,0,0]

    def draw(self):
        x, y = self.pos
        offset = (self.cell_size - self.size)/2
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
            [x + offset, y + offset, x + self.cell_size - offset, y + offset, x + self.cell_size - offset, y + self.cell_size - offset,
            x + offset, y + self.cell_size - offset]), ('c3B', self.get_color()))

class SimulationWindow(pyglet.window.Window):
    """The window displaying the simulation"""

    def __init__(self, cell_size=20, width=640, height=640):
        super(SimulationWindow, self).__init__(width, height)
        self.width = width
        self.height = height

        self.init_props()

        self.cell_size = 20
        self.cell_list = []
        self.init_cells()

    def init_props(self):
        self.mf_prop = [0.5, 0.5] # Proportion of males and females in the population
        self.mf_influence = [0.5, 0.5] # Influence coefficent for males and females

        self.age_prop = [1/5 for i in range(5)]
        self.age_influence = [1/5 for i in range(5)]

        self.expected_resistance = np.array(self.mf_prop).dot(self.mf_influence) * np.array(self.age_prop).dot(self.age_influence)

    def init_cells(self):
        for row in range(int(self.height/self.cell_size)):
            self.cell_list.append([Cell(self.cell_size*col, self.cell_size*row, self.cell_size, self.expected_resistance*np.random.uniform())
                for col in range(int(self.width/self.cell_size))])

    def prob_infection(self, cell_1_pos, cell_2_pos):
        x1, y1 = cell_1_pos
        x2, y2 = cell_2_pos

    def step(self):
        pass

    def on_draw(self):
        self.clear()
        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                self.cell_list[row][col].draw()

    def update(self, dt):
        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                self.cell_list[row][col].color = max(0, self.cell_list[row][col].color - 1)

def callback(dt):
    print(f"{dt} seconds since last callback")

if __name__ == '__main__':
    window = SimulationWindow()
    pyglet.clock.schedule_interval(window.update, 1/30)
    pyglet.app.run()

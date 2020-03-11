import pyglet
import numpy as np

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

    def __init__(self, cell_size=20, width=640, height=640):
        super(SimulationWindow, self).__init__(width, height)
        self.width = width
        self.height = height

        self.init_props()
        self.init_time_params()

        self.cell_size = cell_size
        self.cell_list = []
        self.init_cells()

    def init_time_params(self):
        self.max_latent = 10
        self.max_infected = 20
        self.prob_death = 0.01/20

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

        self.cell_list[np.random.randint(len(self.cell_list))][np.random.randint(len(self.cell_list[0]))].set_state(3) # For testing purposes; the one person that is infected in the population at the start

    def prob_infection(self, row, col):
        a = 0.5 # Infection through diagonal
        b = 0.5 # Infection through vertical/horizontal

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
        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                # print(self.prob_infection(row, col))
                if (self.cell_list[row][col].state == 1) and (np.random.uniform() < self.prob_infection(row, col)):
                    self.cell_list[row][col].set_state(2)
                elif self.cell_list[row][col].state == 2:
                    if self.cell_list[row][col].time_counter > self.max_latent:
                        self.cell_list[row][col].set_state(3)
                    else:
                        self.cell_list[row][col].time_counter += 1
                elif self.cell_list[row][col].state == 3:
                    if self.cell_list[row][col].time_counter > self.max_infected:
                        self.cell_list[row][col].set_state(1)
                    else:
                        if np.random.uniform() < self.prob_death:
                            self.cell_list[row][col].set_state(0)
                            print(self.cell_list[row][col].state)
                        else:
                            self.cell_list[row][col].time_counter += 1

    def movement_step(self):
        pass

    def on_draw(self):
        self.clear()
        batch = pyglet.graphics.Batch()
        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                self.cell_list[row][col].add_to_batch(batch)

        batch.draw()

    def update(self, dt):
        self.infection_step()

    def callback(self, dt):
        print(f"{dt} seconds since last callback")

if __name__ == '__main__':
    window = SimulationWindow(cell_size=20)
    pyglet.clock.schedule_interval(window.update, 1/30)
    pyglet.app.run()

import pyglet

class Cell(object):
    """Cell representing a human in the simulation"""

    def __init__(self, x, y, cell_size, ratio=0.85):
        super(Cell, self).__init__()
        self.state = 0
        self.cell_size = cell_size
        self.size = cell_size*ratio
        self.pos = (x, y) # Lower left

    def get_color(self):
        if self.state == 0:
            return [255,255,255 , 255,255,255 , 255,255,255 , 255,255,255]
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

        self.cell_size = 20
        self.cell_list = []
        self.init_cells()

    def init_cells(self):
        for row in range(int(self.height/self.cell_size)):
            self.cell_list.append([Cell(self.cell_size*col, self.cell_size*row, self.cell_size) for col in range(int(self.width/self.cell_size))])

    def step(self):
        pass

    def on_draw(self):
        for row in range(len(self.cell_list)):
            for col in range(len(self.cell_list[row])):
                self.cell_list[row][col].draw()

if __name__ == '__main__':
    window = SimulationWindow()
    pyglet.app.run()

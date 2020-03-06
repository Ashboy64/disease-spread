import pyglet

cell_size = 20
width, height = (640, 640)

window = pyglet.window.Window(width, height)
image = pyglet.resource.image('assets/square.png')

def draw_cell(x, y, size, ratio, color):
    new_size = size*ratio
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
        [x + (size-new_size)/2, y + (size-new_size)/2, x + size - (size-new_size)/2, y + (size-new_size)/2, x + size - (size-new_size)/2, y + size - (size-new_size)/2,
        x + (size-new_size)/2, y + size - (size-new_size)/2]), ('c3B', color))

@window.event
def on_draw():
    window.clear()

    for i in range(int(width/cell_size)):
        for j in range(int(height/cell_size)):
            draw_cell(cell_size*i, cell_size*j, cell_size, 0.85, [255 for i in range(12)])

pyglet.app.run()

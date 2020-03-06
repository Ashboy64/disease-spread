import pyglet

cell_size = 20
width, height = (640, 640)

window = pyglet.window.Window(width, height)
image = pyglet.resource.image('assets/square.png')

def draw_cell(x, y, size, ratio):
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
        [x, y, x+size, y, x+size, y+size, x, y+size]), ('c3B', 0, 0, 0))
    new_size = size*ratio
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
        [x + (size-new_size)/2, y + (size-new_size)/2, x + size - (size-new_size)/2, y + (size-new_size)/2, x + size - (size-new_size)/2, y + size - (size-new_size)/2,
        x + (size-new_size)/2, y + size - (size-new_size)/2]))

@window.event
def on_draw():
    window.clear()

    for i in range(int(width/cell_size)):
        for j in range(int(height/cell_size)):
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                [cell_size*i, cell_size*j, cell_size*(i+1), cell_size*j, cell_size*(i+1), cell_size*(j+1), cell_size*(i), cell_size*(j+1)]))

    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [0, 0, 10, 0, 10, 10, 0, 10]))

pyglet.app.run()

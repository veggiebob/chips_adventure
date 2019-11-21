import pygame
from pygame.locals import *
import numpy

from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
pygame.init()

RED = (255, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((400, 400), OPENGL | DOUBLEBUF)

vertex_shader = """
#version 330
in vec4 position;
varying vec2 uv;
void main()
{
    gl_Position = position;
    uv = position.xy;
}
"""

fragment_shader = """
#version 330
varying vec2 uv;
uniform float time;
void main()
{
    gl_FragColor = vec4(sin(uv.x*10.), sin(uv.y*10. + time * 0.01), 0.0, 1.0);
}
"""

shader = shaders.compileProgram(
    shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)
# glViewport(-5, -5, 10, 10)
vertex_data = numpy.array([
    0.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 1.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    1.0, 1.0, 0.0
], dtype=numpy.float32)

# vetex buffer object

vertex_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
glBufferData(GL_ARRAY_BUFFER, 36 * 2, vertex_data, GL_STATIC_DRAW)

# vertex array object

vertex_array_object = glGenVertexArrays(1)
glBindVertexArray(vertex_array_object)
time_uniform_loc = glGetUniformLocation(shader, "time")
# shaders

position = glGetAttribLocation(shader, 'position')
glEnableVertexAttribArray(position)
glVertexAttribPointer(position, 3, GL_FLOAT, False, 0, None)

#textures
image = open("rgb.bmp")
ix = image.size[0]
iy = image.size[1]
image = image.tostring("raw", "RGBX", 0, -1)
glActiveTexture(GL_TEXTURE1)
# generate a new texture
my_texture1 = glGenTextures(1)
# put the texture in the program
glBindTexture(GL_TEXTURE_2D, my_texture1)
glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
# set the width and height of the texture
glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glGenerateMipmap(GL_TEXTURE_2D)

done = False
time = 0.0
glClearColor(0.5, 1.0, 0.5, 1.0)
clock = pygame.time.Clock()
while not done:
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True
        if event.type == KEYUP and event.key == K_ESCAPE:
            done = True
    
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shader)
    glUniform1f(time_uniform_loc, time)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    pygame.display.flip()
    time += 1
    clock.tick(60)
from numpy import array

import pygame, sys
from pygame.locals import *

from OpenGL.GL import shaders
from OpenGL.arrays import vbo
from OpenGL.GL import *
from OpenGL.GLU import *
from ctypes import sizeof, c_float, c_void_p, c_uint

pygame.init()

screen_size = [400, 400]
screen = pygame.display.set_mode(screen_size, OPENGL | DOUBLEBUF)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0.5,0.5,0.5,1)
glClearDepth(1.0)
glDepthFunc(GL_LESS)
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)

glViewport(-2, -2, 2, 2)
def create_shader(shader_type, source):
	# compile a shader
	shader = glCreateShader(shader_type)
	glShaderSource(shader, source)
	glCompileShader(shader)
	if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
		raise RuntimeError(glGetShaderInfoLog(shader))
	return shader
vert_shader = create_shader(GL_VERTEX_SHADER, """#version 120
attribute vec4 position;
void main() {
	gl_Position = position;
}
""")
print(vert_shader)
frag_shader = create_shader(GL_FRAGMENT_SHADER, """#version 120
void main() {
	gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
""")
prgm = glCreateProgram()
glAttachShader(prgm, vert_shader)
glAttachShader(prgm, frag_shader)
glLinkProgram(prgm)
# prgm = shaders.compileProgram(vert_shader, frag_shader)
# model = vbo.VBO(
# 	array([
# 		[0, 0, 0],
# 		[1, 1, 0],
# 		[0, 1, 0],
# 		[0, 0, 0],
# 		[1, 0, 0],
# 		[1, 1, 1]
# 	], 'f')
# )
# model.bind()

#vertex data
points = [
	(0, 0, 0),
	(1, 0, 0),
	(0, 1, 0),
	(1, 1, 0)
]

faces  = [
	[0, 3, 1],
	[0, 2, 3]
]

sizes = []
verticies = []

for indexes in faces:
	sizes.append(len(indexes))
	for index in indexes:
		vertex = points[index]
		verticies.append(vertex)

indicies = list(range(sum(sizes)))

###

##buffer stuff
def flatten(*lll):
	return [u for ll in lll for l in ll for u in l]
data = flatten(*zip(verticies))

posidx = glGetAttribLocation(prgm, "position")

# loading buffers
indices_buffer = (c_uint * len(indicies))(*indicies)
data_buffer = (c_float * len(data))(*data)

vbuf = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbuf)
glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
###


glUseProgram(prgm)

#vertex setup
glEnableVertexAttribArray(posidx)
glBindBuffer(GL_ARRAY_BUFFER, vbuf)
glVertexAttribPointer( posidx, 4, GL_FLOAT, GL_FALSE, 4*4, 0)

glEnableClientState(GL_VERTEX_ARRAY)
glEnableClientState(GL_TEXTURE_COORD_ARRAY)
glEnableClientState(GL_NORMAL_ARRAY)
glEnableClientState(GL_COLOR_ARRAY)
# glDrawArrays(GL_TRIANGLES, 0, 6)
###draw stuff

# raw data stuff
uint_size  = sizeof(c_uint)
float_size = sizeof(c_float)
vertex_offset    = c_void_p(0 * float_size)
record_len       =         0 * float_size
# glMatrixMode(GL_MODELVIEW)
# glPushMatrix()
# glScale(scale, scale, scale)
# glMultMatrixf(m.column_major(q.matrix(rotation)))

offset = 0
glClearColor(1.0, 1.0, 0.0, 1.0)
glEnableVertexAttribArray(posidx)
glVertexAttribPointer( posidx, 4, GL_FLOAT, GL_FALSE, 4*4, 0)
glDrawElements(GL_TRIANGLES,
			   sizes[0], GL_UNSIGNED_INT,
			   c_void_p(offset))
# offset += size * uint_size
# glPopMatrix()
# glFlush()
pygame.display.flip()
while True:
	for e in pygame.event.get():
		if e.type == QUIT:
			pygame.quit()
			sys.exit()

"""
#https://bitbucket.org/rndblnch/opengl-programmable/src/default/05-shader.py
#notes
glEnableClientState(GL_VERTEX_ARRAY);
glEnableClientState(GL_COLOR_ARRAY);
glVertexPointerf(model)
glDrawArrays(GL_TRIANGLES, 0, 9)
glUseProgram
glCreateShader(shader_type) # return shader
glShaderSource(shader, source)
glCompileShader(shader)

#something I stole:
def create_shader(shader_type, source):
	# compile a shader
	shader = glCreateShader(shader_type)
	glShaderSource(shader, source)
	glCompileShader(shader)
	if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
		raise RuntimeError(glGetShaderInfoLog(shader))
	return shader

vert_shader = create_shader(GL_VERTEX_SHADER, ###shader source###)
frag_shader = create_shader(GL_FRAGMENT_SHADER, ###shader source###)

#textures
# access texture in frag with
# texture2D(texture, vec2 position)
def init_texture():
	glActiveTexture(GL_TEXTURE0+0)
	glBindTexture(GL_TEXTURE_3D, glGenTextures(1))
	glUniform1i(locations[b"texture_3d"], 0)
	
	glTexParameter(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameter(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	
	def pixel(i, j, k, opaque=b'\xff\xff\xff\xff',
	                   transparent=b'\xff\xff\xff\x00'):
		return opaque if (i+j+k)%2 == 0 else transparent
	
	width = height = depth = 2
	glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA,
	             width, height, depth,
	             0, GL_RGBA, GL_UNSIGNED_BYTE,
	             b"".join(pixel(i, j, k) for i in range(width)
	                                     for j in range(height)
	                                     for k in range(depth)))

# vertex shader:
void main() {
	in gl_Position
	in gl_TexCoord
	out gl_FrontColor
# frag shader:
uniform sampler2D texture_2d;
void main() {
	in varying / gl_Position / gl_Color?
	out gl_FragColor
"""

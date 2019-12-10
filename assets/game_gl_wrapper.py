import pygame
from pygame.locals import *
import numpy

from OpenGL.GL import *
import OpenGL.GL.shaders as shaders

#useful functions
from assets.world_generation import Room
import math
def to_shader_from_tile_loc (levl, v): # this works
    return [
        -v[0] / (Room.ROOM_SIZE * levl.size),
        -(1 - v[1] / (Room.ROOM_SIZE * levl.size))
    ]
def from_shader_to_tile_loc (levl, v, floored=False): # this works
    a = [
        -v[0] * levl.size * Room.ROOM_SIZE,
        (1+v[1]) * levl.size * Room.ROOM_SIZE
    ]
    if floored:
        return [math.floor(a[0]), math.floor(a[1])]
    else:
        return a
class ImageData:
    def __init__(self):
        self.image_data = None
        self.byte_array_image_data = None
        self.width = None
        self.height = None

    def get_image_data(self, surf):
        self.image_data = b""
        self.width = surf.get_width()
        self.height = surf.get_height()
        blist = []
        for i in range(self.height):
            for j in range(self.width):
                p = surf.get_at([j, self.height - i - 1])
                blist.append(p.r)
                blist.append(p.g)
                blist.append(p.b)
        self.image_data = bytes(blist)
        self.byte_array_image_data = bytearray(self.image_data)
        return self.image_data

    def erase (self, surf, pos):
        width = surf.get_width()
        height = surf.get_height()
        # self.image_data = bytearray(self.image_data)
        for i in range(min(max(pos[1], 0), self.height - 1), min(max(pos[1] + height, 0), self.height - 1)):
            for j in range(min(max(pos[0], 0), self.width - 1), min(max(pos[0] + width, 0), self.width - 1)):
                ind = (i * self.width + j) * 3
                self.byte_array_image_data[ind + 0] = 0
                self.byte_array_image_data[ind + 1] = 0
                self.byte_array_image_data[ind + 2] = 0
        self.image_data = bytes(self.byte_array_image_data)
    def blit (self, surf, pos, flipY=False, channels=3): # todo: use python slicing for this to make it much faster
        # todo: first convert the surface into an array of lines, then loop through and replace each bit with the surface as bytes
        width = surf.get_width()
        height = surf.get_height()
        # self.image_data = bytearray(self.image_data)
        for i in range(min(max(pos[1], 0), self.height-1), min(max(pos[1]+height, 0), self.height-1)):
            for j in range(min(max(pos[0], 0), self.width-1), min(max(pos[0]+width, 0), self.width-1)):
                ind = (i * self.width + j) * 3
                p = surf.get_at([j-pos[0], (i-pos[1]) if not flipY else max(height-i+pos[1]-1, 0)])
                # if p.r + p.g + p.b < 5: continue # todo: yes / no?
                self.byte_array_image_data[ind+0] = p.r
                if channels > 1:
                    self.byte_array_image_data[ind+1] = p.g
                    self.byte_array_image_data[ind+2] = p.b
        self.image_data = bytes(self.byte_array_image_data)

class GLWrapper:
    def __init__ (self):
        self.uniforms = {}
        self.gl_textures = [None for i in range(20)]
        self.fragment_shader = """#version 330
        void main() {
            gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }"""
        self.vertex_shader = """
                #version 330
                in vec4 position;
                varying vec2 pixel;
                void main()
                {
                    gl_Position = position;
                    pixel = position.xy;
                }
                """
    def set_uniform (self, name, type):
        self.uniforms[name] = {}
        self.uniforms[name]['type'] = type
    def update_uniform (self, name, value):
        self.uniforms[name]["value"] = value
    def gl_init(self):
        ## global gl_textures
        ## global vertex_shader
        ## global fragment_shader
        ## global shader
        self.shader = shaders.compileProgram(
            shaders.compileShader(self.vertex_shader, GL_VERTEX_SHADER),
            shaders.compileShader(self.fragment_shader, GL_FRAGMENT_SHADER)
        )
        # glViewport(-5, -5, 10, 10)
        vertex_data = numpy.array([
            -1.0, -1.0, 0.0,
            1.0, -1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0
        ], dtype=numpy.float32)

        # vetex buffer object
        vertex_buffer_object = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, 36 * 2, vertex_data, GL_STATIC_DRAW)

        # vertex array object
        vertex_array_object = glGenVertexArrays(1)
        glBindVertexArray(vertex_array_object)

        # uniforms
        # self.uniforms['time']['loc'] = glGetUniformLocation(self.shader, "time")
        # self.uniforms['mouse']['loc'] = glGetUniformLocation(self.shader, "mouse")
        # self.uniforms['camera']['loc'] = glGetUniformLocation(self.shader, "camera")
        for u in self.uniforms:
            self.uniforms[u]['loc'] = glGetUniformLocation(self.shader, u)

        # shaders
        position = glGetAttribLocation(self.shader, 'position')
        glEnableVertexAttribArray(position)
        glVertexAttribPointer(position, 3, GL_FLOAT, False, 0, None)

        glClearColor(0.5, 1.0, 0.5, 1.0)
        glEnable(GL_TEXTURE_2D)
        glFlush()

    def set_gl_texture(self, surface, name, index, **kwargs):
        # https://www.khronos.org/registry/OpenGL-Refpages/es2.0/xhtml/glTexParameter.xml
        args = {
            'sample_mode': GL_NEAREST,
            'clamp_mode': GL_REPEAT
        }
        for k, v in kwargs.items():
            args[k] = v
        ID = ImageData()
        ID.get_image_data(surface)
        glActiveTexture(GL_TEXTURE0 + index)
        tex = glGenTextures(1)
        self.gl_textures[index] = [tex, index, name, ID]
        glBindTexture(GL_TEXTURE_2D, tex)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        #                offset, size, width, height, 0, GL_RGB*, GL_UNSIGNED_BYTE, image_data
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ID.width, ID.height, 0, GL_RGB, GL_UNSIGNED_BYTE, ID.image_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, args['sample_mode'])
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, args['sample_mode'])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, args['clamp_mode'])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, args['clamp_mode'])
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glGenerateMipmap(GL_TEXTURE_2D)
    def update_gl_texture (self, index):
        texp = self.gl_textures[index]
        tex = texp[0]
        imgdata = texp[3]
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, imgdata.width, imgdata.height, 0, GL_RGB, GL_UNSIGNED_BYTE, imgdata.image_data)
    def draw_gl(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader)
        # uniform textures
        for t in self.gl_textures:
            if t is None:
                continue
            glActiveTexture(GL_TEXTURE0 + t[1])
            glBindTexture(GL_TEXTURE_2D, t[0])
            glUniform1i(
                glGetUniformLocation(self.shader, t[2]),
                t[1]
            )

        # game uniform variables
        # glUniform1f(self.time_uniform_loc, self.time)
        # glUniform2f(self.mouse_loc, self.mouse_pos[0], self.mouse_pos[1])
        # glUniform2f(self.camera_loc, self.camera[0], self.camera[1])
        for u in self.uniforms:
            uu = self.uniforms[u]
            v = uu['value']
            l = uu['loc']
            ty = uu['type']
            if ty=='1f':
                glUniform1f(l, v)
            elif ty=='2f':
                glUniform2f(l, v[0], v[1])
            elif ty=='3f':
                glUniform3f(l, v[0], v[1], v[2])
            elif ty=='1i':
                glUniform1i(l, int(v))
            elif ty=='2i':
                glUniform2i(l, int(v[0]), int(v[1]))
            elif ty=='3i':
                glUniform3i(l, int(v[0]), int(v[1]), int(v[2]))

        glDrawArrays(GL_TRIANGLES, 0, 6)
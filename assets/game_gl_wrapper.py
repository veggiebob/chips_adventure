import pygame
from pygame.locals import *
import numpy

from OpenGL.GL import *
import OpenGL.GL.shaders as shaders

class ImageData:
    def __init__(self):
        self.image_data = None
        self.width = None
        self.height = None

    def get_image_data(self, surf):
        self.image_data = b""
        self.width = surf.get_width()
        self.height = surf.get_height()
        for i in range(self.height):
            for j in range(self.width):
                p = surf.get_at([j, self.height - i - 1])
                self.image_data += bytes([p.r, p.g, p.b])
        return self.image_data

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

    def set_gl_texture(self, surface, name, index):
        ID = ImageData()
        ID.get_image_data(surface)
        glActiveTexture(GL_TEXTURE0 + index)
        tex = glGenTextures(1)
        self.gl_textures[index] = [tex, index, name]
        glBindTexture(GL_TEXTURE_2D, tex)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        #                offset, size, width, height, 0, GL_RGB*, GL_UNSIGNED_BYTE, image_data
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ID.width, ID.height, 0, GL_RGB, GL_UNSIGNED_BYTE, ID.image_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glGenerateMipmap(GL_TEXTURE_2D)

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

        glDrawArrays(GL_TRIANGLES, 0, 6)
import pygame
from pygame.locals import *
import numpy

from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
pygame.init()

#stolen from https://stackoverflow.com/questions/53487526/pyopengl-passing-variable-to-the-vertex-shader
WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), OPENGL | DOUBLEBUF)

mouse_pos = [0, 0]
camera = [0, 0]
mouse_down = False

fragment_shader = """
    #version 330
    varying vec2 pixel;
    uniform float time;
    uniform vec2 mouse;
    uniform vec2 camera;
    uniform sampler2D test_texture;
    //uniform sampler2D noise_texture;
    float rangle (vec2 v) {
        return atan(v.y, v.x);
    }
    float dangle (float a, float b) {
        float d = abs(a-b);
        return d > 3.14159 ? d - 3.14159 * 2. : d;
    }
    float sq (float x) {
        return x * x;
    }
    float march (vec2 o) {
        float br = 1.0;
        float step_size = length(o)/128.;
        vec2 d = -normalize(o)*step_size;
        for (int i = 0; i<128; i++) {
            br -= texture2D(test_texture, (o+0.5) - camera).r*0.2;
            o += d;
        }
        return br;
    }
    void main()
    {
        vec2 uv = (pixel + 1.)/2.-0.5;
        vec2 m = mouse-0.5;
        float mangle = rangle(m);
        float pangle = rangle(uv);

        float fov = 0.5;
        float range = 0.8;
        //get static light value from texture here
        float static_light = 0.0;
        float inAngle = smoothstep(fov, 0.0, sq(
            dangle(pangle, mangle)
        )) * sq(smoothstep(range, 0.0, length(uv)));

        float op = march(uv);

        vec3 fcolor = vec3(1.0, 1.0, 0.5);
        vec3 col = fcolor * op * max(inAngle, static_light);

        // Output to screen
        gl_FragColor = vec4(col,1.0);
    }
"""

def gl_init ():
    global gl_textures
    global time_uniform_loc
    global mouse_loc
    global camera_loc
    global vertex_shader
    global fragment_shader
    global shader
    vertex_shader = """
    #version 330
    in vec4 position;
    varying vec2 pixel;
    void main()
    {
        gl_Position = position;
        pixel = position.xy;
    }
    """
    gl_textures = [None for i in range(5)]
    shader = shaders.compileProgram(
        shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
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

    #uniforms
    time_uniform_loc = glGetUniformLocation(shader, "time")
    mouse_loc = glGetUniformLocation(shader, "mouse")
    camera_loc = glGetUniformLocation(shader, "camera")

    # shaders
    position = glGetAttribLocation(shader, 'position')
    glEnableVertexAttribArray(position)
    glVertexAttribPointer(position, 3, GL_FLOAT, False, 0, None)

    glClearColor(0.5, 1.0, 0.5, 1.0)
    glEnable(GL_TEXTURE_2D)
    glFlush()
# initialize all the gl stuff
gl_init()
#textures
class ImageData:
    def __init__ (self):
        self.image_data = None
        self.width = None
        self.height = None
    def get_image_data (self, surf):
        self.image_data = b""
        self.width = surf.get_width()
        self.height = surf.get_height()
        for i in range(self.height):
            for j in range(self.width):
                p = surf.get_at([j, self.height-i-1])
                self.image_data += bytes([p.r, p.g, p.b])
        return self.image_data

def set_gl_texture (surface, name, index):
    ID = ImageData()
    ID.get_image_data(surface)
    glActiveTexture(GL_TEXTURE0 + index)
    tex = glGenTextures(1)
    gl_textures[index] = [tex, index, name]
    glBindTexture(GL_TEXTURE_2D, tex)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    #                offset, size, width, height, 0, GL_RGB*, GL_UNSIGNED_BYTE, image_data
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ID.width, ID.height, 0, GL_RGB, GL_UNSIGNED_BYTE, ID.image_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glGenerateMipmap(GL_TEXTURE_2D)


image = pygame.image.load("assets/test_lighting.bmp")
image2 = pygame.image.load("assets/noise_512.jpg")
set_gl_texture(image, "test_texture", 0)
# set_gl_texture(image2, "noise_texture", 1)

def draw_gl ():
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shader)
    #uniform textures
    for t in gl_textures:
        if t is None:
            continue
        glActiveTexture(GL_TEXTURE0 + t[1])
        glBindTexture(GL_TEXTURE_2D, t[0])
        glUniform1i(
            glGetUniformLocation(shader, t[2]),
            t[1]
        )

    #game uniform variables
    glUniform1f(time_uniform_loc, time)
    glUniform2f(mouse_loc, mouse_pos[0], mouse_pos[1])
    glUniform2f(camera_loc, camera[0], camera[1])
    glDrawArrays(GL_TRIANGLES, 0, 6)

done = False
time = 0.0
clock = pygame.time.Clock()
while not done:
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True
        if event.type == MOUSEMOTION:
            mouse_pos = [
                event.pos[0]/WIDTH,
                1-event.pos[1]/HEIGHT
            ]
        if event.type == MOUSEBUTTONDOWN:
            mouse_down = True
        if event.type == MOUSEBUTTONUP:
            mouse_down = False

    if mouse_down:
        camera[0] -= (mouse_pos[0] - 0.5) * 0.01
        camera[1] -= (mouse_pos[1] - 0.5) * 0.01

    draw_gl()
    pygame.display.flip()
    time += 1
    clock.tick(60)
import pygame, sys, os
from pygame.locals import *
from level_handling import *
from worldhandling import *
from assets.game_gl_wrapper import *
pygame.init()

WIDTH = 576 * 2
HEIGHT = 576
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), OPENGL | DOUBLEBUF)
yeet = WorldHandler()
test_level = LevelHandler(1)
test_level.create_layers(yeet)

epic_gl = GLWrapper()
epic_gl.set_uniform('time', '1f')
epic_gl.set_uniform('mouse', '2f')
epic_gl.set_uniform('camera', '2f')

back = pygame.image.load('assets/ground.jpg')
lvl = test_level.draw_color()
lwidth = lvl.get_width()
lheight = lvl.get_height()
back = pygame.transform.scale(back, (lwidth, lheight))
for i in range(lheight):
    for j in range(lwidth):
        p = lvl.get_at([j, i])
        if p.r+p.b+p.g<4:
            lvl.set_at([j, i], back.get_at([j, i]))
epic_gl.set_gl_texture(test_level.draw_color(), 'color_layer', 0)
epic_gl.set_gl_texture(test_level.draw_opacity(), 'opacity_layer', 1)

epic_gl.fragment_shader = """#version 330
varying vec2 pixel;
uniform float time;
uniform vec2 mouse;
uniform vec2 camera;
uniform sampler2D color_layer;
uniform sampler2D opacity_layer;
//uniform sampler2D test_texture;
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
        br -= texture2D(opacity_layer, (o+0.5) - camera).r*0.05;
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
    vec3 mcolor = texture2D(color_layer, (uv+0.5)-camera).rgb;
    vec3 col = 
        fcolor 
        * op 
        * max(inAngle, static_light) 
        * mcolor
    ;

    // Output to screen
    gl_FragColor = vec4(col,1.0);
}"""

epic_gl.gl_init()

clock = pygame.time.Clock()
mouse_pos = [0, 0]
camera = [0, 0]
mouse_down = False
time = 0.0
while True:
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
        if e.type == MOUSEMOTION:
            mouse_pos = [
                e.pos[0] / WIDTH,
                1 - e.pos[1] / HEIGHT
            ]
        if e.type == MOUSEBUTTONDOWN:
            mouse_down = True
        if e.type == MOUSEBUTTONUP:
            mouse_down = False

    if mouse_down:
        camera[0] -= (mouse_pos[0] - 0.5) * 0.01
        camera[1] -= (mouse_pos[1] - 0.5) * 0.01

    # SCREEN.blit(test_level.draw_opacity(), (0, 0))
    # SCREEN.blit(test_level.draw_color(), (576, 0))
    # test_level.update_tiles(yeet)
    # pygame.display.update()

    epic_gl.update_uniform('time', time)
    epic_gl.update_uniform('mouse', mouse_pos)
    epic_gl.update_uniform('camera', camera)
    epic_gl.draw_gl()
    pygame.display.flip()
    time += 1
    clock.tick(60)


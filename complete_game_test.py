import pygame, sys, os
from pygame.locals import *
from level_handling import *
from worldhandling import *
from assets.game_gl_wrapper import *
from enemy_control import *
pygame.init()

# goals:
# >>>>> treasures with lamp fluid
# add in HIDDEN doors, ONE_WAY doors
# player sprite through ui frame :)))

# touchup:
# static lighting
# enemy movement / collision
# water, lava, boots etc.


epic_gl = GLWrapper()
LEVEL_SIZE_PROGRESSION = 1
time = 0.0 # global
def reset_game():
    print('starting . . .')
    global camera, spawn, ZOOM, mouse_down, keys, LEVEL_SIZE, LEVEL_TILE_SIZE, Player, portal_time, portal_gut, c_update_pos, lamplight, health, in_menu, dead, player_dead, bullets, won, gameTime, LAMP_TIME
    global yeet, test_level, LEVEL_SIZE_PROGRESSION
    global back, enemy_image_layer, bullet, aa_scari
    LAMP_TIME = 30 * LEVEL_SIZE_PROGRESSION  # in seconds
    yeet = WorldHandler()
    print("finished world constants")
    test_level = LevelHandler(LEVEL_SIZE_PROGRESSION)  # LEVEL SIZE
    print("generated level")
    test_level.create_layers(yeet)
    print('created level of size %d'%LEVEL_SIZE_PROGRESSION)

    spawn = to_shader_from_tile_loc(test_level, test_level.r_world[0][random.randint(0, test_level.size - 1)].spawnpoint)
    camera = [spawn[0], spawn[1]]

    mouse_down = False
    gameTime = 0.0 # in seconds, stops when won
    keys = [None for i in range(1000)]
    LEVEL_SIZE = test_level.get_size()
    LEVEL_TILE_SIZE = [LEVEL_SIZE[0] / 16, LEVEL_SIZE[1] / 16]
    print('level tile size is %s'%LEVEL_TILE_SIZE)
    Player = {
        'speed': 0.005,
    }
    portal_time = 0
    portal_gut = 0  # 0 - 1
    c_update_pos = [0, 0]
    lamplight = 1.0
    health = 1.0
    bullets = [] # in [x, y, vx, vy] shader coords
    in_menu = False
    dead = 0.0  # 0 - 1
    player_dead = False
    ZOOM = 1.0 / test_level.size
    won = False

    print('loading assets')
    enemy_spritesheet = pygame.image.load('assets/enemy_spritesheet_3.png')
    aa_scari = EnemyHandler(test_level, enemy_spritesheet)
    noise = pygame.image.load('assets/noise_512.jpg')
    back = pygame.image.load('assets/brick_ground.jpg')
    text_texture = pygame.image.load('assets/texter.png')
    ui_background = pygame.image.load('assets/ui_background.png')
    white_noise = pygame.image.load('assets/shadertoy_actual_gray_noise.png')
    bullet = pygame.image.load('assets/bullet.png')
    lvl = test_level.draw_color()
    lwidth = lvl.get_width()
    lheight = lvl.get_height()
    enemy_image_layer = pygame.Surface((lwidth, lheight))
    enemy_image_layer.fill((0, 0, 0, 0))

    blurred_opacity = test_level.draw_opacity()
    # for i in range(3):
    #     blurred_opacity = gaussianBlur(blurred_opacity)
    print('loaded all assets!')
    print('setting textures . . .')
    epic_gl.set_gl_texture(lvl, 'color_layer', 0, clamp_mode=GL_CLAMP_TO_EDGE)
    epic_gl.set_gl_texture(blurred_opacity, 'opacity_layer', 1, clamp_mode=GL_CLAMP_TO_EDGE, sample_mode=GL_LINEAR)
    epic_gl.set_gl_texture(noise, 'noise_texture', 2, clamp_mode=GL_REPEAT)
    epic_gl.set_gl_texture(back, 'background', 3, clamp_mode=GL_REPEAT, sample_mode=GL_LINEAR)
    epic_gl.set_gl_texture(enemy_image_layer, 'enemy_layer', 4, clamp_mode=GL_CLAMP_TO_EDGE, sample_mode=GL_NEAREST)
    epic_gl.set_gl_texture(ui_background, 'ui_background', 5, clamp_mode=GL_REPEAT, sample_mode=GL_NEAREST)
    epic_gl.set_gl_texture(text_texture, 'texter', 6, clamp_mode=GL_CLAMP_TO_EDGE, sample_mode=GL_LINEAR)
    epic_gl.set_gl_texture(white_noise, 'white_noise', 7, clamp_mode=GL_REPEAT, sample_mode=GL_LINEAR)
    print('set all textures')
    print('done!')


WIDTH = 500
HEIGHT = 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), OPENGL | DOUBLEBUF)
display_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = display_info.current_w, display_info.current_h
SCREEN_MARGIN = (SCREEN_WIDTH - WIDTH) / 2

reset_game()

epic_gl.set_uniform('time', '1f')
epic_gl.set_uniform('game_time', '1f')
epic_gl.set_uniform('mouse', '2f')
epic_gl.set_uniform('camera', '2f')
epic_gl.set_uniform('portal_gut', '1f')
epic_gl.set_uniform('zoom', '1f')
epic_gl.set_uniform('TELEPORT_DISTANCE', '1f')
epic_gl.set_uniform('lamplight', '1f')
epic_gl.set_uniform('health', '1f')
epic_gl.set_uniform('in_menu', '1i')
epic_gl.set_uniform('dead', '1f')
epic_gl.set_uniform('won', '1i')

epic_gl.update_uniform('TELEPORT_DISTANCE', test_level.teleport_distance) # i no it bad but eh

epic_gl.fragment_shader = open('world_fragment.glsl', 'r').read()

epic_gl.gl_init()

# for some reason I thought I might need this function:
# y = max(x^2-x, 0.1)+x

length = lambda a: math.sqrt(a[0]*a[0]+a[1]*a[1])
clamp = lambda v,a,b: min(max(v,a),b)
mix = lambda a,b,t:a+t*(b-a)
smooth = lambda v:3*clamp(v,0,1)**2-2*clamp(v,0,1)**3
smoothstep = lambda a,b,v:smooth((v-a)/(b-a))
sign = lambda a:int(bool(a))*2-1

empty_black = pygame.Surface((8, 8))
empty_black.fill((0, 0, 0))
small_empty_black = pygame.Surface((5, 5))
small_empty_black.fill((0, 0, 0))
def tile_from_shader_loc (levl, v):
    c = from_shader_to_tile_loc(levl, v)
    c[0] = clamp(math.floor(c[0]), 0, levl.tile_dim - 1)
    c[1] = clamp(math.floor(c[1]), 0, levl.tile_dim - 1)
    return test_level.master_tiles[c[1]][c[0]]
def update_color_layer (iters=1): # deprecated
    global c_update_pos
    test_level.update_tiles(yeet)
    nlvl = test_level.draw_color()
    h = nlvl.get_height()
    for i in range(iters):
        update_tex = pygame.Surface((1, 1))
        col = nlvl.get_at(c_update_pos)
        if col.r+col.g+col.b < 5:
            col = back.get_at(c_update_pos)
        update_tex.set_at([0, 0], col)
        epic_gl.gl_textures[0][3].blit(update_tex, [c_update_pos[0]-1, h-c_update_pos[1]-1])
        c_update_pos[0] += 1
        if c_update_pos[0] >= test_level.draw_color().get_width():
            c_update_pos[0] = 0
            c_update_pos[1] += 1
        if c_update_pos[1] >= test_level.draw_color().get_height():
            c_update_pos = [0, 0]
    epic_gl.update_gl_texture(0)
def update_color_layer_tiles ():
    global c_update_pos
    global LEVEL_SIZE
    nlvl = test_level.draw_color()
    tile = test_level.master_tiles[c_update_pos[1]-1][c_update_pos[0]]
    pos = [c_update_pos[0] * Tilemap.TILE_SIZE, LEVEL_SIZE[1] - c_update_pos[1] * Tilemap.TILE_SIZE]
    # print('updating tile at position ' + str(pos))
    epic_gl.gl_textures[0][3].blit(tile.image, pos, True)
    epic_gl.update_gl_texture(0)
    c_update_pos[0] += 1
    if c_update_pos[0] >= test_level.tile_dim:
        c_update_pos[0] = 0
        c_update_pos[1] += 1
    if c_update_pos[1] > test_level.tile_dim:
        c_update_pos = [0, 0]

def update_opacity_layer_tiles ():
    global c_update_pos
    global LEVEL_SIZE
    nlvl = test_level.draw_opacity()
    tile = test_level.master_tiles[c_update_pos[1]-1][c_update_pos[0]]
    pos = [c_update_pos[0] * Tilemap.TILE_SIZE, LEVEL_SIZE[1] - c_update_pos[1] * Tilemap.TILE_SIZE]
    try:
        from_level = nlvl.subsurface((pos[0], LEVEL_SIZE[1] - pos[1] - Tilemap.TILE_SIZE, Tilemap.TILE_SIZE, Tilemap.TILE_SIZE))
        epic_gl.gl_textures[1][3].blit(from_level, pos, True, 1)
    except:
        pass
    epic_gl.update_gl_texture(1)

def update_enemy_layer (enemy_handler):
    global camera, ZOOM
    global mouse_down
    global LEVEL_SIZE
    global health
    global ALIVE_TIME
    iw = enemy_image_layer.get_width()
    ih = enemy_image_layer.get_height()
    # for e in enemy_handler.enemies:# todo: make this faster, or the one down there v
    #     # it's texture 4
    #     # first, convert to a tile location
    #     tloc = from_shader_to_tile_loc(test_level, [e.x, e.y])
    #     epic_gl.gl_textures[4][3].erase(empty_black, (int(tloc[0] * Tilemap.TILE_SIZE)-4, int(LEVEL_SIZE[1] - tloc[1] * Tilemap.TILE_SIZE)-4))
    health -= enemy_handler.update(camera) / (ALIVE_TIME * 60)
    for e in enemy_handler.enemies:
        # first, convert to a tile location
        tloc = from_shader_to_tile_loc(test_level, [e.x, e.y])
        epic_gl.gl_textures[4][3].blit(e.get_image(), (int(tloc[0] * Tilemap.TILE_SIZE)-4, int(LEVEL_SIZE[1] - tloc[1] * Tilemap.TILE_SIZE)-4), True)
    for b in bullets:
        tloc = from_shader_to_tile_loc(test_level, [b[0], b[1]])
        x = int(tloc[0] * Tilemap.TILE_SIZE)
        y = int(LEVEL_SIZE[1] - tloc[1] * Tilemap.TILE_SIZE)
        epic_gl.gl_textures[4][3].erase(bullet, (x-2, y-2))
        b[0] += b[2] * ZOOM
        b[1] += b[3] * ZOOM
        tloc = from_shader_to_tile_loc(test_level, [b[0], b[1]])
        x = int(tloc[0] * Tilemap.TILE_SIZE)
        y = int(LEVEL_SIZE[1] - tloc[1] * Tilemap.TILE_SIZE)
        b[4] += 1
        epic_gl.gl_textures[4][3].blit(bullet, (x-2, y-2), True)
        if b[4] > 1500:
            bullets.remove(b)
            continue
        for e in enemy_handler.enemies:
            if length([b[0]-e.x, b[1]-e.y]) < EnemyHandler.WORLD_CLOSE:
                e.hit(10)
                bullets.remove(b)
                if e.dead:
                    enemy_handler.enemies.remove(e)
                break

    epic_gl.update_gl_texture(4)


clock = pygame.time.Clock()
mouse_pos = [0, 0]
ALIVE_TIME = 3 # in seconds
ENEMY_SPAWN_TIME = 10 # in seconds
BULLET_SPEED = 0.008
while True:
    reset_the_game = False
    mouse_pressed = False
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
        if e.type == MOUSEMOTION:
            mouse_pos = [
                (e.pos[0]-SCREEN_MARGIN) / SCREEN_WIDTH,
                1 - e.pos[1] / SCREEN_HEIGHT
            ]
        if e.type == MOUSEBUTTONDOWN:
            mouse_down = True
            mouse_pressed = True
            # print(camera)
            # print(from_shader_to_tile_loc(test_level, camera))
            # t_pos = from_shader_to_tile_loc(test_level, camera, True)
            # r_pos = [math.floor(t_pos[0]/Room.ROOM_SIZE), math.floor(t_pos[1]/Room.ROOM_SIZE)]
            # print('tpos: %s'%t_pos)
            # print('room_pos: %s'%r_pos)
        if e.type == MOUSEBUTTONUP:
            mouse_down = False
        if e.type == KEYDOWN:
            keys[e.key] = True
            if e.key == K_BACKSPACE:
                print('resetting . . .')
                in_menu = True
                won = False
                reset_the_game = True
                dead = 2.0
            elif e.key == K_SPACE:
                print("timestamp: " + str(int(time/60)))
        if e.type == KEYUP:
            keys[e.key] = False

    if in_menu:
        dead = max(dead - 1 / 60 / 3, 0.0)
        if mouse_down and dead == 0:
            reset_the_game = True
            dead = 2

    else:

        # shooting bullets
        if mouse_pressed:
            mangle = -math.atan2(mouse_pos[0]-0.5, mouse_pos[1]-0.5) - 3.14159 / 2
            bullets.append([camera[0], camera[1], math.cos(mangle) * BULLET_SPEED, math.sin(mangle) * BULLET_SPEED, 0])

        # player movement / collisions
        ctile = tile_from_shader_loc(test_level, camera)
        if ctile.name == 'gol':
            won = True
            in_menu = True
            dead = 1.0
            continue
        # np = [
        #     clamp(math.floor(-camera[0]*LEVEL_SIZE[0]), 0, LEVEL_SIZE[0]-1),
        #     clamp(math.floor(LEVEL_SIZE[1]+camera[1]*LEVEL_SIZE[1]), 0, LEVEL_SIZE[1]-1)
        # ]
        np = from_shader_to_tile_loc(test_level, camera, True)
        p_room_pos = [math.floor(np[0]/Room.ROOM_SIZE), math.floor(np[1]/Room.ROOM_SIZE)]
        p_room = test_level.r_world[p_room_pos[0]][p_room_pos[1]]

        np = from_shader_to_tile_loc(test_level, camera)
        np[0] *= Tilemap.TILE_SIZE
        np[1] *= Tilemap.TILE_SIZE
        np[0] = math.floor(np[0])
        np[1] = math.floor(np[1])

        op = test_level.draw_opacity().get_at(np)
        portal_t = [(op.g-128)/128, (op.b-128)/128]
        portal_intensity = smoothstep(0, 0.001, length(portal_t))
        if portal_intensity > 0.1:
            portal_time += 1
        else:
            portal_time = 0

        if portal_intensity >= 0.2 and portal_time > 60 and length([chx, chy]) * pspeed < 0.001:
            # do the teleport (teleport_distance DOES work)
            camera[0] -= portal_t[0] * test_level.teleport_distance * ZOOM
            camera[1] -= portal_t[1] * test_level.teleport_distance * ZOOM
            portal_gut = 1.0
            portal_time = 0

        #MOVEMENT
        # if mouse_down: # only for debugging
        #     camera[0] -= (mouse_pos[0] - 0.5) * 0.01
        #     camera[1] -= (mouse_pos[1] - 0.5) * 0.01

        pspeed = Player['speed'] * ZOOM - max(portal_intensity, portal_gut) * 0.004
        chx = 0
        chy = 0
        if keys[K_COMMA] or keys[K_w] or keys[K_UP]:
            chy += 1
        if keys[K_o] or keys[K_s] or keys[K_DOWN]:
            chy -= 1
        if keys[K_e] or keys[K_d] or keys[K_RIGHT]:
            chx += 1
        if keys[K_a] or keys[K_LEFT]:
            chx -= 1

        if chx != 0 or chy != 0:
            # if moving . . .
            portal_time -= 1
            chl = math.sqrt(chx * chx + chy * chy)
            chx /= chl
            chy /= chl
            camera[0] -= chx * pspeed
            camera[1] -= chy * pspeed
        else:
            portal_gut = min(portal_gut + portal_intensity / 60, 1)

        # collisions v.2.0
        if not tile_from_shader_loc(test_level, camera).walkable:
            look_distance = 2.0
            stuck = True
            if tile_from_shader_loc(test_level, [camera[0] + pspeed * chx * look_distance, camera[1]]).walkable:
                camera[0] += pspeed * chx
                stuck = False
            if stuck and tile_from_shader_loc(test_level, [camera[0], camera[1] + pspeed * chy * look_distance]).walkable:
                camera[1] += pspeed * chy
                stuck = False
            if stuck: # ugh
                done = False
                for look_distance in range(4, 50): # just in case
                    for a in range(0, 360, 45):
                        d = [math.cos(a / 180 * 3.14159), math.sin(a / 180 * 3.14159)]
                        if tile_from_shader_loc(test_level, [camera[0] + pspeed * look_distance * d[0], camera[1] + pspeed * look_distance * d[1]]).walkable:
                            camera[0] += d[0] * pspeed
                            camera[1] += d[1] * pspeed
                            done = True
                            break
                    if done: break

                if not done: # worst case scenario (probably only happens in missed teleportation (to be resolved down there vvv)
                    camera[1] -= pspeed

        # experimental portal correction -- easier to use >rooms< or gradient?
        # place = from_shader_to_tile_loc(test_level, camera)
        # chunk = [math.floor(place[0]/Room.ROOM_SIZE), math.floor(place[1]/Room.ROOM_SIZE)]
        # rum = test_level.r_world[chunk[0]][chunk[1]]
        # portal_loc = [rum.portal[0], rum.portal[1]]
        # splace = to_shader_from_tile_loc(test_level, place)
        # correction = [splace[0]-camera[0], splace[1]-camera[1]]
        # correction[0] *= 0.1*portal_gut/length(correction)
        # correction[1] *= 0.1*portal_gut/length(correction)
        # camera[0] -= correction[0]
        # camera[1] -= correction[1]

        # continually changing stuff
        portal_gut *= 0.98
        lamplight = max(lamplight - 1 / (LAMP_TIME * 60), 0.0)


        # update luh land
        test_level.update_tiles(yeet)
        update_color_layer_tiles()
        update_opacity_layer_tiles()
        update_enemy_layer(aa_scari)

        if health < 0.0:
            player_dead = True
            dead = 1.0
            in_menu = True

        if time % (60 * ENEMY_SPAWN_TIME) == 0 and time != 0: # todo: random enemy spawning
            rEn = random.randint(0, 4)
            rm = [random.randint(0, test_level.size-1), random.randint(0, test_level.size-1)]
            tries = 100
            while rm[0] == p_room_pos[0] and rm[1] == p_room_pos[1] and tries > 0:
                rm = [random.randint(0, test_level.size - 1), random.randint(0, test_level.size - 1)]
                tries -= 1
            spawnpoint = test_level.r_world[rm[0]][rm[1]].spawnpoint
            spawnpoint[0] += rm[0] * Room.ROOM_SIZE
            spawnpoint[1] += rm[1] * Room.ROOM_SIZE
            aa_scari.add_enemy(rEn, spawnpoint)
            print('added an enemy')
        gameTime += 1/60




    # gl stuff

    epic_gl.update_uniform('time', time)
    epic_gl.update_uniform('game_time', gameTime)
    epic_gl.update_uniform('mouse', mouse_pos)
    epic_gl.update_uniform('camera', camera)
    epic_gl.update_uniform('portal_gut', portal_gut)
    epic_gl.update_uniform('zoom', ZOOM)
    epic_gl.update_uniform('lamplight', lamplight)
    epic_gl.update_uniform('health', health)
    epic_gl.update_uniform('in_menu', in_menu)
    epic_gl.update_uniform('dead', dead)
    epic_gl.update_uniform('won', won)

    epic_gl.draw_gl()
    pygame.display.flip()
    clock.tick(60)
    time += 1
    if reset_the_game:
        if won:
            LEVEL_SIZE_PROGRESSION += 1 # if won, go to the next level
        reset_game()



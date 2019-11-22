import pygame, sys, os
from pygame.locals import *
from assets.tile_control import *
from assets.tilesnfriends import *
from assets.world_generation import *
pygame.init()

WIDTH = 800
HEIGHT = 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
ZOOM = 1.0 # how much to scale tiles
#todo: camera containing position & zoom that gives position and scale of looking-at image
#todo: make a world handler class that makes this file a lot shorter
#todo: also what if it was a dark exploration game with most things obscured -- light raycasting
#TILEMAPS
testtmp = Tilemap('assets/tilemaps/testing_tilemap.png')
grasstmp = Tilemap('assets/tilemaps/grass_tilemap.png')
metaltmp = Tilemap('assets/tilemaps/metal_tilemap.png')
woodtmp = Tilemap('assets/tilemaps/wood_tilemap.png')
#more go here

emptytmp = Tilemap('assets/tilemaps/testing_tilemap.png')
emptytmp.image = pygame.Surface((80, 80))
emptytmp.load_images()
#instances of tiles subclasses
empty = TileCreator(
    emptytmp,
    id=0,
    name='empty'
)
tester = TileCreator(
    testtmp,
    name='test',
    id=-1
)
grass = TileCreator(
    grasstmp,
    name='grass',
    id=1,
    walkable=False
)
metal = TileCreator(
    metaltmp,
    name='metal',
    id=2
)
wood = TileCreator(
    woodtmp,
    name='wood',
    walkable=False,
    id=3
)
TILE_ENCODER = {
    ' ': empty,
    'g': grass,
    'm': metal,
    't': tester,
    'w': wood
}
# up here because rooms
def read_output (filepath):
    arr = []
    try:
        file = open('assets/output/' + filepath + '.txt', 'r')
    except:
        # if it doesn't contain
        print("couldn't open %s, executing the parse levels script"%filepath)
        os.chdir('assets')
        exec(open('parse_levels.py').read())
        os.chdir('..')
        try:
            file = open('assets/output/' + filepath + '.txt', 'r')
        except:
            print('could not find file %s'%filepath)
            return
    for line in file:
        lin = []
        txtline = line
        if line[len(line)-1]=="\n":
            txtline = line[:-1:]
        for ch in txtline:
            lin.append(ch)
        arr.append(lin)
    return arr
def level_to_tiles (level):
    x = -1
    y = -1
    tiles = []
    for l in level:
        y += 1
        x = -1
        line = []
        for t in l:
            x += 1
            PID = 0 # not what you think it is (positional identification number)
            if y>0 and level[y-1][x] == t:
                PID += 1
            if x<len(l)-1 and level[y][x+1] == t:
                PID += 2
            if y<len(level)-1 and level[y+1][x] == t:
                PID += 4
            if x>0 and level[y][x-1] == t:
                PID += 8
            try:
                te = TILE_ENCODER[t]
            except:
                te = TILE_ENCODER[' ']
            tile = te.generateTile(PID, [x*Tilemap.TILE_SIZE, y*Tilemap.TILE_SIZE])
            line.append(tile)
        tiles.append(line)
    return tiles
def get_room (roomname):
    return level_to_tiles(read_output(roomname))
def string_number (num, digits):
    dig = math.floor(math.log10(max(num, 1)))+1
    nst = '%s'%num
    while dig<digits:
        nst = '0%s'%nst
        dig += 1
    return nst
RAW_ROOMS = [
    # get_room('ROOM_00'),
]
NUM_ROOMS = 16
max_digits = math.floor(math.log10(NUM_ROOMS-1))+1
for i in range(0, NUM_ROOMS):
    RAW_ROOMS.append(get_room('ROOM_%s'%string_number(i, max_digits)))

"""
Room(
    name='',
    map=RAW_ROOMS[],
    doors=[],
    treasure=[0,0],
    spawnpoint=[0,0]
),
"""
ROOMS = [
    Room(
        name="empty 4-door",
        map=RAW_ROOMS[0],
        doors = [True, True, True, True],
        treasure = [0, 0],
        spawnpoint = [0, 0]
    ),
    Room(
        name="bottom left corner",
        map=RAW_ROOMS[1],
        doors = [False, True, True, False],
        treasure = [0, 0],
        spawnpoint = [0, 0]
    ),
    Room(
        name='top left corner',
        map=RAW_ROOMS[2],
        doors=[False, True, False, True],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='bottom right (broken)',
        map=RAW_ROOMS[3],
        doors=[True, False, True, False],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='top right',
        map=RAW_ROOMS[4],
        doors=[True, False, False, True],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='christmas tree',
        map=RAW_ROOMS[5],
        doors=[False, False, True, False],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='metal right-facing',
        map=RAW_ROOMS[6],
        doors=[False, True, False, False],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='tube up-down',
        map=RAW_ROOMS[7],
        doors=[False, False, True, True],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='tube left-right',
        map=RAW_ROOMS[8],
        doors=[True, True, False, False],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='christmas-right',
        map=RAW_ROOMS[9],
        doors=[True, False, False, False],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='christmas-nogravity',
        map=RAW_ROOMS[10],
        doors=[False, False, False, True],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='christmas-left',
        map=RAW_ROOMS[11],
        doors=[False, True, False, False],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='left-side',
        map=RAW_ROOMS[12],
        doors=[False, True, True, True],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='down-side',
        map=RAW_ROOMS[13],
        doors=[True, True, True, False],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='right-side',
        map=RAW_ROOMS[14],
        doors=[True, False, True, True],
        treasure=[0,0],
        spawnpoint=[0,0]
    ),
    Room(
        name='up-side',
        map=RAW_ROOMS[15],
        doors=[True, True, False, True],
        treasure=[0,0],
        spawnpoint=[0,0]
    )
]
DEFAULT_ROOM = ROOMS[0]

def draw_level (level):
    surface = pygame.Surface((Tilemap.TILE_SIZE*len(level[0]), Tilemap.TILE_SIZE*len(level)))
    print('drawing surface %dx%d'%(surface.get_width(), surface.get_height()))
    y = -1
    for lee in level:
        y += 1
        x = -1
        for tee in lee:
            x += 1
            # position = tee.pos
            #todo:make this use the tile position without making chunks disappear
            position = [x * Tilemap.TILE_SIZE, y * Tilemap.TILE_SIZE]
            surface.blit(tee.image, (position[0], position[1], Tilemap.TILE_SIZE, Tilemap.TILE_SIZE))
    return surface
def get_surrounding (mt, i, j):
    tid = mt[i][j].id
    left = mt[i][j-1].id if j > 0 else -1
    right = mt[i][j+1].id if j < len(mt[i])-1 else -1
    up = mt[i-1][j].id if i > 0 else -1
    down = mt[i+1][j].id if i < len(mt)-1 else -1
    # print('%d, %d, %d, %d'%(left, right, up, down))
    # print('tid: d')
    return int(up==tid) + int(right==tid) * 2 + int(down==tid) * 4 + int(left==tid) * 8

level_1_raw = read_output('test_level_3')
level_1 = level_to_tiles(level_1_raw)
# SCREEN.blit(pygame.transform.scale2x(pygame.transform.scale2x(draw_level(level_1))), (0, 0))


# create a level with a size
TESTING_LEVEL = Level(10)
TESTING_LEVEL.depth_first_generation()
# convert the level to room requirements
rr_world = TESTING_LEVEL.level_to_room_reqs()
# initialize rooms
r_world = []
# add in the rooms according to room reqs
for l in rr_world:
    next_t_world = []
    for rr in l:
        selected = False
        for rum in ROOMS:
            if selected:
                continue
            if rr.can_contain(rum):
                selected = True
                next_t_world.append(rum)
        if not selected:
            next_t_world.append(DEFAULT_ROOM)
    r_world.append(next_t_world)

world_width = len(r_world[0])*Room.ROOM_SIZE
world_height = len(r_world)*Room.ROOM_SIZE
master_tiles = [[None for i in range(0, world_width)] for j in range(0, world_height)]

offset_i = -1
for r_l in r_world:
    offset_i += 1
    offset_j = -1
    for rum in r_l:
        offset_j += 1
        r_map = rum.map
        t_i = -1
        for m_l in r_map:
            t_i += 1
            t_j = -1
            for t in m_l:
                t_j += 1
                t_world_i = offset_i*Room.ROOM_SIZE + t_i
                t_world_j = offset_j*Room.ROOM_SIZE + t_j
                master_tiles[t_world_i][t_world_j] = t.copy()
                master_tiles[t_world_i][t_world_j].pos = [t_world_j * Tilemap.TILE_SIZE, t_world_i * Tilemap.TILE_SIZE]
                master_tiles[t_world_i][t_world_j].needs_update = True
                # print('putting tile at %d, %d with tile %s'%(t_world_i, t_world_j, t))

world_graphic = draw_level(master_tiles)
og_image_width = world_graphic.get_width()
og_image_height = world_graphic.get_height()
ZOOM = min(float(WIDTH)/og_image_width, float(HEIGHT)/og_image_height)
world_graphic = pygame.transform.scale(world_graphic, (int(og_image_width * ZOOM), int(og_image_height * ZOOM)))
# SCREEN.blit(world_graphic, (0, 0))

# test_level_size = 30
# SCREEN.blit(TESTING_LEVEL.draw(test_level_size), (WIDTH-test_level_size, HEIGHT-test_level_size))
while True:
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
    max_redraw = 10
    i = -1
    j = -1
    for l in master_tiles:
        i += 1
        j = -1
        for t in l:
            j += 1
            if t.needs_update:
                # do updates
                t.update_pid(get_surrounding(master_tiles, i, j))
                # update screen
                SCREEN.blit(pygame.transform.scale(t.image, (int(t.image.get_width()*ZOOM)+1, int(t.image.get_height()*ZOOM)+1)), (t.pos[0]*ZOOM, t.pos[1]*ZOOM, ZOOM*Tilemap.TILE_SIZE, ZOOM*Tilemap.TILE_SIZE))
                max_redraw -= 1
                # now it's updated
                t.update()
            if max_redraw < 0:
                break
        if max_redraw < 0:
            break
    pygame.display.update()

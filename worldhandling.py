import pygame, sys, os
from pygame.locals import *
from assets.tile_control import *
from assets.tilesnfriends import *
from assets.world_generation import *
class WorldHandler:
    def __init__ (self):
        self.init_tilemaps()
        self.init_rooms()
    def init_tilemaps (self):
        # TILEMAPS
        self.testtmp = Tilemap('assets/tilemaps/testing_tilemap.png')
        self.grasstmp = Tilemap('assets/tilemaps/grass_tilemap.png')
        self.metaltmp = Tilemap('assets/tilemaps/metal_tilemap.png')
        self.woodtmp = Tilemap('assets/tilemaps/wood_tilemap.png')
        self.stonetmp = Tilemap('assets/tilemaps/stone_tilemap.png')
        self.glasstmp = Tilemap('assets/tilemaps/glass_tilemap.png', 0.0) # opacity is 0.0
        # more go here

        self.emptytmp = Tilemap('assets/tilemaps/testing_tilemap.png')
        self.emptytmp.image = pygame.Surface((80, 80))
        self.emptytmp.opacity_image = pygame.Surface((80, 80))
        self.emptytmp.load_images()
        # instances of tiles subclasses
        self.empty = TileCreator(
           self.emptytmp,
            id=0,
            name='empty'
        )
        self.tester = TileCreator(
           self.testtmp,
            name='test',
            id=-1
        )
        self.grass = TileCreator(
           self.grasstmp,
            name='grass',
            id=1,
            walkable=False
        )
        self.metal = TileCreator(
           self.metaltmp,
            name='metal',
            id=2
        )
        self.wood = TileCreator(
           self.woodtmp,
            name='wood',
            walkable=False,
            id=3
        )
        self.stone = TileCreator(
            self.stonetmp,
            name='stone',
            walkable=False,
            id=4
        )
        self.glass = TileCreator(
            self.glasstmp,
            name='glass',
            walkable=False,
            id=5,
            opacity=0.0
        )
        self.TILE_ENCODER = {
            # see assets/parse_levels.py
            ' ': self.empty,
            'g': self.grass,
            'm': self.metal,
            't': self.tester,
            'w': self.wood,
            'c': self.stone,
            'l': self.glass
        }
    def init_rooms (self):
        self.RAW_ROOMS = [
            # get_room('ROOM_00'),
        ]
        self.NUM_ROOMS = 16
        max_digits = math.floor(math.log10(self.NUM_ROOMS - 1)) + 1
        for i in range(0, self.NUM_ROOMS):
            self.RAW_ROOMS.append(self.get_room('ROOM_%s' % self.string_number(i, max_digits)))
        self.ROOMS = [
            Room(
                name="empty 4-door",
                map=self.RAW_ROOMS[0],
                doors=[True, True, True, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name="bottom left corner",
                map=self.RAW_ROOMS[1],
                doors=[False, True, True, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='top left corner',
                map=self.RAW_ROOMS[2],
                doors=[False, True, False, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='bottom right',
                map=self.RAW_ROOMS[3],
                doors=[True, False, True, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='top right',
                map=self.RAW_ROOMS[4],
                doors=[True, False, False, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='tube up-down',
                map=self.RAW_ROOMS[5],
                doors=[False, False, True, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='tube left-right',
                map=self.RAW_ROOMS[6],
                doors=[True, True, False, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='christmas tree',
                map=self.RAW_ROOMS[7],
                doors=[False, False, True, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='christmas-right',
                map=self.RAW_ROOMS[8],
                doors=[True, False, False, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='christmas-nogravity',
                map=self.RAW_ROOMS[9],
                doors=[False, False, False, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='christmas-left',
                map=self.RAW_ROOMS[10],
                doors=[False, True, False, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),

            Room(
                name='metal right-facing',
                map=self.RAW_ROOMS[11],
                doors=[False, True, False, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='left-side',
                map=self.RAW_ROOMS[12],
                doors=[False, True, True, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='down-side',
                map=self.RAW_ROOMS[13],
                doors=[True, True, True, False],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='right-side',
                map=self.RAW_ROOMS[14],
                doors=[True, False, True, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            ),
            Room(
                name='up-side',
                map=self.RAW_ROOMS[15],
                doors=[True, True, False, True],
                treasure=[0, 0],
                spawnpoint=[0, 0]
            )
        ]
        self.DEFAULT_ROOM = self.ROOMS[0]

    # statics
    def read_output(self, filepath):
        arr = []
        try:
            file = open('assets/output/' + filepath + '.txt', 'r')
        except:
            # if it doesn't contain
            print("couldn't open %s, executing the parse levels script" % filepath)
            os.chdir('assets')
            exec(open('parse_levels.py').read())
            os.chdir('..')
            try:
                file = open('assets/output/' + filepath + '.txt', 'r')
            except:
                print('could not find file %s' % filepath)
                return
        for line in file:
            lin = []
            txtline = line
            if line[len(line) - 1] == "\n":
                txtline = line[:-1:]
            for ch in txtline:
                lin.append(ch)
            arr.append(lin)
        return arr
    def level_to_tiles(self, level):
        x = -1
        y = -1
        tiles = []
        for l in level:
            y += 1
            x = -1
            line = []
            for t in l:
                x += 1
                PID = 0  # not what you think it is (positional identification number)
                if y > 0 and level[y - 1][x] == t:
                    PID += 1
                if x < len(l) - 1 and level[y][x + 1] == t:
                    PID += 2
                if y < len(level) - 1 and level[y + 1][x] == t:
                    PID += 4
                if x > 0 and level[y][x - 1] == t:
                    PID += 8
                try:
                    te = self.TILE_ENCODER[t]
                except:
                    te = self.TILE_ENCODER[' ']
                tile = te.generateTile(PID, [x * Tilemap.TILE_SIZE, y * Tilemap.TILE_SIZE])
                line.append(tile)
            tiles.append(line)
        return tiles
    def get_room(self, roomname):
        return self.level_to_tiles(self.read_output(roomname))
    def string_number(self, num, digits):
        dig = math.floor(math.log10(max(num, 1))) + 1
        nst = '%s' % num
        while dig < digits:
            nst = '0%s' % nst
            dig += 1
        return nst
    
    # level stuff
    def draw_level(self, level, opacity=False):
        surface = pygame.Surface((Tilemap.TILE_SIZE * len(level[0]), Tilemap.TILE_SIZE * len(level)))
        #print('drawing surface %dx%d' % (surface.get_width(), surface.get_height()))
        y = -1
        for lee in level:
            y += 1
            x = -1
            for tee in lee:
                x += 1
                # position = tee.pos
                # todo:make this use the tile position without making chunks disappear
                position = [x * Tilemap.TILE_SIZE, y * Tilemap.TILE_SIZE]
                surface.blit(tee.image if not opacity else tee.opacity_image, (position[0], position[1], Tilemap.TILE_SIZE, Tilemap.TILE_SIZE))
        return surface
    def get_surrounding(self, mt, i, j):
        tid = mt[i][j].id
        left = mt[i][j - 1].id if j > 0 else -1
        right = mt[i][j + 1].id if j < len(mt[i]) - 1 else -1
        up = mt[i - 1][j].id if i > 0 else -1
        down = mt[i + 1][j].id if i < len(mt) - 1 else -1
        # print('%d, %d, %d, %d'%(left, right, up, down))
        # print('tid: d')
        return int(up == tid) + int(right == tid) * 2 + int(down == tid) * 4 + int(left == tid) * 8


    def test (self):
        print(self.TILE_ENCODER)
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
        self.glasstmp = Tilemap('assets/tilemaps/glass_tilemap.png', 0.5) # opacity is 50%
        self.vinestmp = Tilemap('assets/tilemaps/vines_tilemap.png', 0.0) # clear

        self.goal = Tilemap('assets/tilemaps/testing_tilemap.png', 0)
        self.goal.image = pygame.Surface((80, 80))
        self.goal.image.fill((255, 0, 0))
        self.goal.opacity_image = pygame.Surface((80, 80))
        self.goal.opacity_image.fill((0, 128, 128))
        self.goal.load_images()
            #Tilemap('assets/tilemaps/goal.png') #todo:make this tilemap

        # more go here
        self.emptytmp = Tilemap('assets/tilemaps/testing_tilemap.png')
        self.emptytmp.image = pygame.Surface((80, 80))
        self.emptytmp.opacity_image = pygame.Surface((80, 80))
        self.emptytmp.opacity_image.fill((0, 128, 128))
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
            id=2,
            walkable=False
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
            id=5
        )
        self.vines = TileCreator(
            self.vinestmp,
            name='vines',
            walkable=True,
            id=6
        )
        self.gol = TileCreator(
            self.goal,
            name='gol',
            walkable=True,
            id=69
        )
        self.TILE_ENCODER = {
            # see assets/parse_levels.py
            ' ': self.empty,
            'g': self.grass,
            'm': self.metal,
            't': self.tester,
            'w': self.wood,
            'c': self.stone,
            'l': self.glass,
            'v': self.vines,

            'G': self.gol
            # $ = treasure, * = torch, S = spawnpoint
        }
    def init_rooms (self):
        self.RAW_ROOMS = [
            # get_room('ROOM_00'),
        ]
        self.META_ROOMS = [
            # get_meta('ROOM_00')
        ]
        self.NUM_ROOMS = 16
        max_digits = math.floor(math.log10(self.NUM_ROOMS - 1)) + 1
        for i in range(0, self.NUM_ROOMS):
            rstring = 'ROOM_%s' % self.string_number(i, max_digits)
            self.RAW_ROOMS.append(self.get_room(rstring))
            self.META_ROOMS.append(self.get_meta(rstring))

        self.ROOMS = [
            Room(
                name="empty 4-door",
                map=self.RAW_ROOMS[0],
                meta=self.META_ROOMS[0],
                doors=[True, True, True, True],
                portal=[3, 3, 10, 10]
            ),
            Room(
                name="bottom left corner",
                map=self.RAW_ROOMS[1],
                meta=self.META_ROOMS[1],
                doors=[False, True, True, False],
                portal=[2, 2, 2, 4]
            ),
            Room(
                name='top left corner',
                map=self.RAW_ROOMS[2],
                meta=self.META_ROOMS[2],
                doors=[False, True, False, True]),
            Room(
                name='bottom right',
                map=self.RAW_ROOMS[3],
                meta=self.META_ROOMS[3],
                doors=[True, False, True, False]),
            Room(
                name='top right',
                map=self.RAW_ROOMS[4],
                meta=self.META_ROOMS[4],
                doors=[True, False, False, True]),
            Room(
                name='tube up-down',
                map=self.RAW_ROOMS[5],
                meta=self.META_ROOMS[5],
                doors=[False, False, True, True]),
            Room(
                name='tube left-right',
                map=self.RAW_ROOMS[6],
                meta=self.META_ROOMS[6],
                doors=[True, True, False, False]),
            Room(
                name='christmas tree',
                map=self.RAW_ROOMS[7],
                meta=self.META_ROOMS[7],
                doors=[False, False, True, False]),
            Room(
                name='christmas-right',
                map=self.RAW_ROOMS[8],
                meta=self.META_ROOMS[8],
                doors=[True, False, False, False]),
            Room(
                name='christmas-nogravity',
                map=self.RAW_ROOMS[9],
                meta=self.META_ROOMS[9],
                doors=[False, False, False, True]),
            Room(
                name='christmas-left',
                map=self.RAW_ROOMS[10],
                meta=self.META_ROOMS[10],
                doors=[False, True, False, False]),
            Room(
                name='metal right-facing',
                map=self.RAW_ROOMS[11],
                meta=self.META_ROOMS[11],
                doors=[False, True, False, False]),
            Room(
                name='left-side',
                map=self.RAW_ROOMS[12],
                meta=self.META_ROOMS[12],
                doors=[False, True, True, True]),
            Room(
                name='down-side',
                map=self.RAW_ROOMS[13],
                meta=self.META_ROOMS[13],
                doors=[True, True, True, False]),
            Room(
                name='right-side',
                map=self.RAW_ROOMS[14],
                meta=self.META_ROOMS[14],
                doors=[True, False, True, True]),
            Room(
                name='up-side',
                map=self.RAW_ROOMS[15],
                meta=self.META_ROOMS[15],
                doors=[True, True, False, True])
        ]
        self.DEFAULT_ROOM = self.ROOMS[1]

        # now do sections
        self.allSections = [ # [code letter, number of rooms]
            ['Z', 2]
        ]
        self.section_room_data = {}
        self.section_metas = {}
        for l in self.allSections:
            self.section_room_data[l[0]] = []
            self.section_metas[l[0]] = []
            for r in range(l[1]):
                sstring = 'SECTION_%s_%d'%(l[0], r)
                self.section_room_data[l[0]].append(self.get_room(sstring))
                self.section_metas[l[0]].append(self.get_meta(sstring))

        # remember, left:right:up:down
        self.sections = {
            'Z': Section(
                [
                    Room(
                        map=self.section_room_data['Z'][0],
                        meta=self.section_metas['Z'][0],
                        doors=[True, True, False, False]
                    ),
                    Room(
                        map=self.section_room_data['Z'][1],
                        meta=self.section_metas['Z'][1],
                        doors=[True, False, False, False]
                    )
                ],
                [
                    [0, 0],
                    [0, 1]
                ]
            )
        }

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
    def get_output_meta (self, text_level):
        meta = {
            'treasure': [0, 0], # $
            'spawnpoint': [0, 0], # S
            'torch': [], # *
        }
        x = -1
        y = -1
        for l in text_level:
            y += 1
            x = -1
            for t in l:
                x += 1
                if t == '$':
                    meta['treasure'] = [y, x]
                elif t == '*':
                    meta['torch'].append([y, x])
                elif t == 'S':
                    meta['spawnpoint'] = [y, x]
        return meta
    def get_doors (self, levl): # yep, another abandoned method :(
        return [True, True, True, True]
    def get_meta(self, roomname):
        raw_meta = self.get_output_meta(self.read_output(roomname))
        #lvl = self.level_to_tiles(self.read_output(roomname))
        #doors = self.get_doors(lvl)
        #raw_meta['doors'] = doors # maybe later
        return raw_meta
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
        y = -1
        for lee in level:
            y += 1
            x = -1
            for tee in lee:
                x += 1
                # I don't even care about whether or not a tile is in the right spot or not
                # at this point it doesn't even matter lets just get on with it shall we
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
        #return int(up >= 0) + int(right >= 0) * 2 + int(down >= 0) * 4 + int(left >= 0) * 8
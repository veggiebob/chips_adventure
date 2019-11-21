import random, math, pygame
class Level:
    def __init__ (self, size):
        self.size = size
        # walls all exist at first
        self.vwalls = [[True for i in range(0, size)] for j in range(0, size)]# [top-down [left-right]] look like |
        self.hwalls = [[True for i in range(0, size)] for j in range(0, size)]# [left-right [top-down]] look like _
        # all the cells are unvisited
        self.cells = [[False for i in range(0, size)] for j in range(0, size)]# tells if visited
        self.total_cells = self.size * self.size
        self.visited_cells = 0
    def draw (self, boardSize): # returns a surface
        b = 0.05
        ts = boardSize/self.size
        ds = ts * (1-2*b)
        surf = pygame.Surface((boardSize, boardSize))
        for i in range(0, self.size):
            for j in range(0, self.size):
                walls = self.get_walls(i, j)
                cell = self.cells[i][j]
                x = j * ts
                y = i * ts
                #draw cell
                pygame.draw.rect(surf, (255, 200, 200) if cell else (100, 100, 100), (x, y, ts, ts), 0)
                x += b*ts
                y += b*ts
                #walls
                #left
                if walls[0]:
                    pygame.draw.line(surf, (255, 255, 255), (x, y), (x, y+ds))
                #right
                if walls[1]:
                    pygame.draw.line(surf, (255, 255, 255), (x+ds, y), (x+ds, y+ds))
                #up
                if walls[2]:
                    pygame.draw.line(surf, (255, 255, 255), (x, y), (x+ds, y))
                #down
                if walls[3]:
                    pygame.draw.line(surf, (255, 255, 255), (x, y+ds), (x+ds, y+ds))
        return surf
    def level_to_room_reqs (self):
        lvl = []
        for i in range(0, self.size):
            lin = []
            for j in range(0, self.size):
                #todo: will I need more room requirements?
                lin.append(RoomRequirement(doors=self.get_inverted_walls(i, j)))
            lvl.append(lin)
        return lvl
    def get_walls (self, i, j):
        # left, right, up, down
        l = self.vwalls[i][j-1] if j > 0 else True
        r = self.vwalls[i][j] if j < self.size - 1 else True
        u = self.hwalls[j][i-1] if i > 0 else True
        d = self.hwalls[j][i] if i < self.size - 1 else True
        return [l, r, u, d]
    def get_inverted_walls (self, i, j):
        walls = self.get_walls(i, j)
        for i in range(0, len(walls)):
            walls[i] = not walls[i]
        return walls
    def get_dir (self, i):
        # di, dj
        if i==0:
            return [0, -1]
        elif i==1:
            return [0, 1]
        elif i==2:
            return [-1, 0]
        elif i==3:
            return [1, 0]
    def depth_first_generation (self, maxSteps=-1):
        starti = random.randint(0, self.size-1)
        startj = random.randint(0, self.size-1)
        self.cells[starti][startj] = True
        self.visited_cells = 1
        path = [] # [i, j]
        ci = starti
        cj = startj
        # print('start is %d, %d'%(ci, cj))
        steps = 0
        while self.visited_cells<self.total_cells and steps < maxSteps or (maxSteps<0 and self.visited_cells<self.total_cells):
            steps += 1
            options = [False, False, False, False] # left, right, up, down
            # left
            if cj > 0 and not self.cells[ci][cj-1]:
                options[0] = True
            # right
            if cj < self.size - 1 and not self.cells[ci][cj+1]:
                options[1] = True
            #up
            if ci > 0 and not self.cells[ci-1][cj]:
                options[2] = True
            #down
            if ci < self.size - 1 and not self.cells[ci+1][cj]:
                options[3] = True
            keyed_options = []
            for i in range(0, len(options)):
                if options[i]:
                    keyed_options.append(i)
            if len(keyed_options)==0:
                last = len(path)-1
                if last<0:
                    #print('finished')
                    break
                ci = path[last][0]
                cj = path[last][1]
                path.pop()
                continue
            # if it will add a tile, then tell it that it added a tile
            self.total_cells += 1
            random_move = keyed_options[random.randint(0, len(keyed_options)-1)]
            # random_move should be a 0, 1, 2, 3
            direct = self.get_dir(random_move)
            # aka left, right, up, down
            # (up or down) and !(left or right)
            istop = direct[0] == 0
            lr = math.floor((direct[1] - 1) / 2)  # from (-1 to 1) -> (-1, 0)
            ud = math.floor((direct[0] - 1) / 2)  # from (-1 to 1) -> (-1, 0)
            # those transformations because 0 means *next* wall, -1 means prev. wall
            # here break down wall that it's going through
            if not istop:
                self.hwalls[cj][ci + ud] = False
            else:
                self.vwalls[ci][cj + lr] = False

            # cell is the new cell
            path.append([ci, cj])#append to stack
            ci += direct[0]
            cj += direct[1]
            # it is now visited
            self.cells[ci][cj] = True
            # (up or down) and !(left or right)
            istop = direct[0] == 0
            lr = -math.floor((direct[1]+1)/2) # from (-1 to 1) -> (0, -1)
            ud = -math.floor((direct[0]+1)/2) # from (-1 to 1) -> (0, -1)
            # here we need to reverse the direction because it means that's where it *came* from
            # notice how the order of the numbers flipped

            # break down the wall it came from (need to reverse direction)
            if not istop:
                self.hwalls[cj][ci + ud] = False
            else:
                self.vwalls[ci][cj + lr] = False

class Room:
    ROOM_SIZE = 12
    def __init__ (self, **kwargs): # needs MAP: STRING[], DOORS: INT[], SPAWNPOINT: INT[], TREASURE: INT[]
        self.args = {}
        for key, value in kwargs.items():
            self.args[key] = value
        self.map = self._req(self.args, 'map') # ROOM_SIZE x ROOM_SIZE 2d array of Tiles
        if not len(self.map) == Room.ROOM_SIZE or not len(self.map[0]) == Room.ROOM_SIZE:
            print('not the right size')
        self.name = self._opt(self.args, 'name')
        self.doors = self._req(self.args, 'doors')
        self.spawnpoint = self._req(self.args, 'spawnpoint')
        self.treasure = self._req(self.args, 'treasure')
    def _req (self, dict, item):
        try:
            return dict[item]
        except:
            assert False, "You need this item: %s"%item
    def _opt (self, dict, item, default=None):
        try:
            return dict[item]
        except:
            return default
    def can_be_in (self, room_requirement):
        return room_requirement.can_contain(self)
    def __copy__(self):
        return Room(**self.args)

class RoomRequirement: # this class is used for giving rooms to empty parts of the level
    def __init__ (self, **kwargs):
        args = {}
        for key, value in kwargs.items():
            args[key] = value
        self.doors = self._req(args, 'doors')
        self.used = False
        self.contained_room = None
    def _req (self, dict, item):
        try:
            return dict[item]
        except:
            assert False, "You need this requirement: %s"%item
    def _opt (self, dict, item, default=None):
        try:
            return dict[item]
        except:
            return default
    def can_contain (self, room): # this should always be in progress
        for i in range(0, 4):
            if not room.doors[i] == self.doors[i]:
                return False
        return True
    def matches_doors (self, doors):
        for i in range(0, 4):
            if not doors[i] == self.doors[i]:
                return False
    def fill_with_room (self, rum):
        self.contained_room = rum
        self.used = True
    def remove_room (self):
        self.contained_room = None
        self.used = False

class Section:
    def __init__ (self, rooms=[], locations=[]):
        self.rooms = rooms
        self.locations = locations # [i, j]
        self.irange = [-1, -1]
        self.jrange = [-1, -1]
        self.width = -1
        self.height = -1
        self.starti = 0
        self.startj = 0
        self.update_dims()
    def update_dims (self):
        l0 = self.locations[0]
        mini = l0[0]
        minj = l0[1]
        maxi = l0[0]
        maxj = l0[1]
        for l in self.locations:
            mini = min(mini, l[0])
            minj = min(minj, l[1])
            maxi = max(maxi, l[0])
            maxj = max(maxj, l[1])
        self.starti = mini
        self.startj = minj
        self.width = 1 + self.jrange[1] - self.jrange[0]
        self.height = 1 + self.irange[1] - self.irange[0]
    def add_room (self, roomreq, loc):
        self.rooms.append(roomreq)
        self.locations.append(loc)
        self.update_dims()
    def fit_in_level (self, level):
        size = level.size
        level = level.level_to_room_reqs()
        for i in range(-self.starti, size-self.height):
            for j in range(-self.startj, size-self.width):
                ok = True
                for r in range(0, len(self.rooms)):
                    rloc = self.locations[r]
                    rum = self.rooms[r]
                    loc = [rloc[0]+i, rloc[1]+j]
                    cell = level[loc[0]][loc[1]]
                    if cell.used:
                        ok = False
                        break
                    if not cell.can_contain(rum):
                        ok = False
                        break
                if ok:
                    return [i, j] # return first match
        return [-1, -1] # no matches
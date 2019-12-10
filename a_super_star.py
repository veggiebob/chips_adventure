import math
class a_star:
    # from https://www.khanacademy.org/computer-programming/a-try/5382161829756928
    # converted myself
    # note: terrain is a 2d array of bools, not ints
    def __init__ (self, terrain, starti, startj, endi, endj):
        self.finalPath = [] # [x, y], [x, y]
        self.foundEnd = False
        self.impossiblePath = False
        self.terrain = terrain
        self.startx = starti
        self.starty = startj
        self.endx = endi
        self.endy = endj
        # [0, 1, 2, 3, 4, 5]
        # [x, y, g, h, f, dir]
        self.open = [[starti, startj, 0, -1, -1, -1]] # start with the beginning node / tile
        self.closed = [] # [x, y, g, h, f, dir[dirx, diry]]
        self.score = []
        self.terrain[starti][startj] = False
        self.terrain[endi][endj] = False
    def get_manhattan (self, x, y):
        return abs(x-self.endx) + abs(y-self.endy)
    # def get_dir (self, dir):
    #     return [(dir + 1) % 2 - math.floor((dir % 3) / 2) * 2, dir % 2 - math.floor(((dir - 1) % 3) / 2) * 2]
    def get_dir (self, dir):
        # 0 -> right[1, 0]
        # 1 -> down[0, 1]
        # 2 -> left[-1, 0]
        # 3 -> up[0, -1]
        if dir == 0:
            return [1, 0]
        elif dir == 1:
            return [0, 1]
        elif dir == 2:
            return [-1, 0]
        elif dir == 3:
            return [0, -1]
    def flip_dir (self, dir):
        return [-dir[0], -dir[1]]
    def add_pos (self, posx, posy, dir):
        return [posx+dir[0], posy+dir[1]]
    def in_terrain (self, a, b):
        if b is None:
            return 0 <= a[0] < len(self.terrain[0]) and 0 <= a[1] < len(self.terrain)
        else:
            return 0 <= a < len(self.terrain[0]) and 0 <= b < len(self.terrain)
    def in_closed (self, x, y):
        ind = -1
        for i in self.closed:
            ind+=1
            if x == i[0] and y == i[1]:
                return ind
        return -1
    def in_open (self, x, y):
        ind = -1
        for i in self.open:
            ind += 1
            if x == i[0] and y == i[1]:
                return ind
        return -1
    def find_path (self, maxSteps=10000): ### CALL THIS ONE for determining a final path easily
        if self.terrain[self.starty][self.startx] or self.terrain[self.endy][self.endx]:
            print('Impossible because one of them is inside a wall.')
            self.impossiblePath = True
            self.foundEnd = True
        if not self.impossiblePath:
            steps = 0
            while not self.foundEnd:
                steps += 1
                self.take_step()
                if self.foundEnd:
                    self.determine_final_path()
                if len(self.open) == 0:
                    print('Impossible path.')
                    self.impossiblePath = True
                    break
                if steps>maxSteps:
                    self.impossiblePath = True
                    break
    def take_step (self):
        if self.foundEnd:
            self.determine_final_path()
        for i in range(len(self.open)):
            if self.open[i][3] < 0:
                self.open[i][3] = self.get_manhattan(self.open[i][0], self.open[i][1])
            if self.open[i][4] < 0:
                self.open[i][4] = self.open[i][2] + self.open[i][3]
            if self.open[i][0] == self.endx and self.open[i][1] == self.endy:
                self.foundEnd = True
                break
        if not self.foundEnd:
            self.open.sort(key=lambda a:a[4])
            if len(self.open) > 0:
                i = 0
                for n in range(0, 4):
                    dir = self.get_dir(n)
                    nw = self.add_pos(self.open[i][0], self.open[i][1], dir) # get the connected tile
                    if not self.in_terrain(nw, None):
                        continue
                    if not self.terrain[nw[1]][nw[0]] and self.in_closed(nw[0], nw[1]) < 0: # if it's not in closed and it's walkable (no wall)
                        g = self.open[i][2]+1
                        h = self.get_manhattan(nw[0], nw[1])
                        f = g + h
                        ino = self.in_open(nw[0], nw[1])
                        if ino >= 0:
                            if f < self.open[ino][4]:
                                self.open[ino] = [nw[0], nw[1], g, h, f, dir]
                        else:
                            self.open.append([nw[0], nw[1], g, h, f, dir])
                self.closed.append(self.open[i])
                self.open.remove(self.open[i])
    def determine_final_path (self):
        if self.foundEnd and len(self.finalPath) == 0:
            self.finalPath = [[]]
            self.finalPath[0] = [self.endx, self.endy]
            cx = self.endx
            cy = self.endy
            a = self.in_open(cx, cy)
            if a < 0:
                print("Bad start.")
                self.foundEnd = False
            dir = self.open[a][5]
            while dir != -1:
                n = self.add_pos(cx, cy, self.flip_dir(dir))
                cx = n[0]
                cy = n[1]
                b = self.in_closed(cx, cy)
                if b < 0:
                    print("Encountered a faulty arrow.")
                    self.foundEnd = False
                    break
                dir = self.closed[b][5]
                self.finalPath.append([cx, cy])
                if len(self.finalPath) > 1000:
                    print('Near infinite loop encountered!')
                    break
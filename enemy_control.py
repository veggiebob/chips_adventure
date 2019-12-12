import math, pygame
import os

from assets.tile_control import Tilemap
from assets.game_gl_wrapper import from_shader_to_tile_loc, to_shader_from_tile_loc
from a_super_star import a_star as a_star
class EnemyHandler:
    WORLD_CLOSE = 0.01
    def __init__ (self, level, spritesheet):
        self.walkable_map = []
        self.level = level
        self.spritesheet = spritesheet
        self.world_image_size = self.level.tile_dim * Tilemap.TILE_SIZE
        self.enemy_world_image = pygame.Surface((self.world_image_size, self.world_image_size))
        self.enemies = []
        #this is static
        self.enemy_params = [
            # name, max_health, speed, anim_speed
            ['blob', 10, 3, 30],
            ['bat', 2, 5, 5],
            ['lava', 15, 2, 45],
            ['person', 50, 1, 15],
            ['cloud', 1, 8, 45]
        ]
        self.get_walkable_map()
    def update (self, ppos, debug=False):# player position
        damage = 0.0
        for e in self.enemies:
            damage += e.behave(ppos, debug)
            #self.splice_walkable_square([e.x, e.y], ppos, debug)
        return damage

    def splice_walkable (self, epos, ppos): # enemy pos, player pos
        mini = max(min(ppos[0], epos[0])-1, 0)
        minj = max(min(ppos[1], epos[1])-1, 0)
        maxi = min(max(ppos[0], epos[0])+1, self.level.tile_dim-1)
        maxj = min(max(ppos[1], epos[1])+1, self.level.tile_dim-1)
        splcd = []
        for i in range(mini, maxi+1):
            splcdl = []
            for j in range(minj, maxj+1):
                splcdl.append(self.walkable_map[i][j])
            splcd.append(splcdl)
        return splcd
    def splice_walkable_square (self, epos, ppos, debug=False):
        pp = from_shader_to_tile_loc(self.level, ppos)
        ep = from_shader_to_tile_loc(self.level, epos)
        if debug:
            print("player position in tiles %s"%pp)
            print("enemy position in tiles %s"%ep)
        dx = abs(ep[0]-pp[0])
        dy = abs(ep[1]-pp[1])
        d = int(max(dx, dy))
        ex = int(ep[0])
        ey = int(ep[1])
        splcd = []
        for i in range(ex-d, ex+d+1):
            splcdl = []
            for j in range(ey-d, ey+d+1):
                if i < 0 or j < 0 or i >= self.level.tile_dim or j >= self.level.tile_dim:
                    splcdl.append(False)
                    continue
                splcdl.append(self.walkable_map[i][j])
            splcd.append(splcdl)
        return splcd
    def get_walkable_map (self):
        self.walkable_map = [[t.walkable for t in i] for i in self.level.master_tiles]
    def add_enemy (self, index, pos):
        pa = self.enemy_params[index]
        self.enemies.append(
            # name, spritesheet, index, pos, max_health, speed, anim_speed
            Enemy(pa[0], self.spritesheet, index, to_shader_from_tile_loc(self.level, pos), pa[1], pa[2], pa[3], self.walkable_map, self.level)
        )

class Enemy:
    SIZE = 8
    SPRITE_NUMBER = 5
    SPEED_CONSTANT = 0.001
    def __init__ (self, name, spritesheet, index, pos, max_health=100, speed=1, anim_speed=10, movement_sheet=[], level=None):
        self.index = index
        self.sheet = spritesheet.subsurface((0, index * Enemy.SIZE, Enemy.SIZE * Enemy.SPRITE_NUMBER, Enemy.SIZE))
        self.anim_speed = anim_speed
        self.time = 0
        self.hp = max_health
        self.name = name
        self.dead = False
        self.x = pos[0]
        self.y = pos[1]
        self.speed = speed
        self.movement_sheet = movement_sheet
        self.level = level
        self.terrain = []
        for i in range(len(self.movement_sheet)):
            roh = []
            for j in range(len(self.movement_sheet)):
                roh.append(not self.movement_sheet[j][i])
            self.terrain.append(roh)
        self.a_star = a_star(self.terrain, 0, 0, 0, 0)
    def move (self, x, y, zoom=1):
        self.x += x * self.speed * Enemy.SPEED_CONSTANT * zoom
        self.y += y * self.speed * Enemy.SPEED_CONSTANT * zoom
    def pmove (self, p, zoom=1):
        self.x += p[0] * self.speed * Enemy.SPEED_CONSTANT * zoom
        self.y += p[1] * self.speed * Enemy.SPEED_CONSTANT * zoom
    def long (self, v):
        return math.sqrt(v[0] * v[0] + v[1] * v[1])
    def normalize (self, n):
        l = math.sqrt(n[0] * n[0] + n[1] * n[1])
        return [n[0]/l, n[1]/l]
    def swapxy (self, n):
        return [n[1], n[0]]
    def can_walk (self, x, y, lvl, cmmap):
        ctileloc = self.swapxy(from_shader_to_tile_loc(lvl, [x, y]))
        ctileloc[0] = math.floor(ctileloc[0])
        ctileloc[1] = math.floor(ctileloc[1])
        return 0 <= ctileloc[0] < lvl.tile_dim and 0 <= ctileloc[1] < lvl.tile_dim and cmmap[ctileloc[0]][ctileloc[1]]
    def collide (self, mx, my, lvl, cmmap): # need this to work but it doesn't right now
        # collisions identical to those in complete_game_test.py
        if not self.can_walk(self.x, self.y, lvl, cmmap):
            look_distance = 10.0
            stuck = True
            if self.can_walk(self.x - mx * look_distance, self.y, lvl, cmmap):
                #self.x -= mx
                self.move(-mx, 0, lvl.zoom)
                stuck = False
            if stuck and self.can_walk(self.x, self.y - my * look_distance, lvl, cmmap):
                #self.y -= my
                self.move(-my, 0, lvl.zoom)
                stuck = False
            if stuck:
                s = self.long([mx, my])
                done = False
                for look_distance in range(4, 50):
                    for a in range(0, 360, 45):
                        d = [math.cos(a / 180 * 3.14159), math.sin(a / 180 * 3.14159)]
                        if self.can_walk(self.x + s * d[0] * look_distance, self.y + s * d[1] * look_distance, lvl, cmmap):
                            # self.x += d[0] * s
                            # self.y += d[1] * s
                            self.move(d[0] * s, d[1] * s, lvl.zoom)
                            done = True
                            break
                    if done: break
                #if not done: self.y -= s
                if not done: self.move(0, -s, lvl.zoom)
    def update_a_star (self, ppos):
        try:
            eloc = self.swapxy(from_shader_to_tile_loc(self.level, [self.x, self.y], True))
            ploc = self.swapxy(from_shader_to_tile_loc(self.level, ppos, True))
            self.a_star = a_star(self.terrain, eloc[0], eloc[1], ploc[0], ploc[1])
            self.a_star.find_path()
        except:
            pass
    def behave (self, ppos, debug=False): # square walkable map
        # very simple "come at me" approach
        spd = 1
        damage = 0.0
        epos = self.swapxy(from_shader_to_tile_loc(self.level, [self.x, self.y]))
        eloc = self.swapxy(from_shader_to_tile_loc(self.level, [self.x, self.y], True))
        ploc = self.swapxy(from_shader_to_tile_loc(self.level, ppos, True))

        #do actual movement
        """
        movement = self.normalize(
            [
                ppos[0] - self.x,
                ppos[1] - self.y
            ]
        )
        """
        if len(self.a_star.finalPath) > 1:
            self.a_star.finalPath.reverse()
            movement = self.normalize(self.swapxy([
                (self.a_star.finalPath[1][0] + 0.5-epos[0]),
                -(self.a_star.finalPath[1][1] + 0.5-epos[1])
            ]))
        else:
            disp = [
                ppos[0] - self.x,
                ppos[1] - self.y
            ]
            if self.long(disp) < self.speed * Enemy.SPEED_CONSTANT * 2:
                movement = [0, 0]
                damage = 1.0
            else:
                movement = self.normalize(disp)

        #nonw move the enemy
        movement[0] *= spd
        movement[1] *= spd
        self.pmove(movement, self.level.zoom)
        if self.time % 10 == 0:
            self.update_a_star(ppos)
        # if not self.can_walk(self.x, self.y, self.level, self.movement_sheet):
        #     print('sadnessss %d'%self.time)
        # self.collide(movement[0], movement[1], self.level, self.movement_sheet)
        # if self.time % 30 == 0:
        #     map = [[1 if t else 0 for t in i] for i in self.a_star.terrain]
        #     map[eloc[0]][eloc[1]] = 2
        #     map[ploc[0]][ploc[1]] = 3
        #     if len(self.a_star.finalPath) > 0:
        #         for p in self.a_star.finalPath:
        #             map[p[0]][p[1]] = 4
        #     print('\n'.join([' '.join([('#' if t == 0 else ' ' if t == 1 else 'e' if t == 2 else 'p' if t == 3 else 'o' if t == 4 else '?') for t in i]) for i in map]))
        #     #print('\n'.join([' '.join([' ' if t else '#' for t in i]) for i in self.movement_sheet]))
        #     print('from %s to %s' % (eloc, ploc))
        #     print('motion is %s'%movement)
        return damage
    def get_image (self):
        self.time += 1
        x = math.floor((self.time % self.anim_speed) / self.anim_speed * Enemy.SPRITE_NUMBER)
        return self.sheet.subsurface((Enemy.SIZE * x, 0, Enemy.SIZE, Enemy.SIZE))
    def hit (self, hits):
        self.hp -= hits
        if self.hp < 0:
            self.hp = 0
            self.dead = True
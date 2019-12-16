from assets.world_generation import *
from assets.tile_control import *
class LevelHandler:
    teleport_distance = 3
    def __init__ (self, _size):
        self.size = _size
        self.zoom = 1/self.size
        self.tile_dim = self.size * Room.ROOM_SIZE
        self.level = Level(self.size)
        self.level.depth_first_generation()
        #self.teleport_distance = 3 # made this static
    def create_layers (self, world_handler):
        # room requirements
        self.rr_world = self.level.level_to_room_reqs()
        # rooms
        self.r_world = [[None for j in range(len(self.rr_world[0]))] for i in range(len(self.rr_world))]

        for ss in world_handler.sections:
            sec = world_handler.sections[ss]
            fit = sec.fit_in_level(self.level)
            if fit is not None:
                print('using section %s'%ss)
                for l in range(sec.num_rooms):
                    loc = sec.locations[l]
                    rum = sec.rooms[l]
                    self.r_world[fit[0]+loc[0]][fit[1]+loc[1]] = rum


        # add in (non-special) rooms according to room reqs
        ri = -1
        for l in self.rr_world:
            ri += 1
            rj = -1
            for rr in l:
                rj += 1
                if self.r_world[ri][rj] is None:
                    index = -1
                    possibilities = []
                    for rum in world_handler.ROOMS:
                        index += 1
                        if rr.can_contain(rum):
                            possibilities.append(index)
                    if len(possibilities) == 0:
                        self.r_world[ri][rj] = world_handler.DEFAULT_ROOM
                    else:
                        self.r_world[ri][rj] = world_handler.ROOMS[possibilities[random.randint(0, len(possibilities)-1)]]

        self.level_width = len(self.r_world[0]) * Room.ROOM_SIZE
        self.level_height = len(self.r_world) * Room.ROOM_SIZE
        self.master_tiles = [[None for i in range(0, self.level_width)] for j in range(0, self.level_height)]
        # fill the world with tiles from rooms
        offset_i = -1
        for r_l in self.r_world:
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
                        t_world_i = offset_i * Room.ROOM_SIZE + t_i
                        t_world_j = offset_j * Room.ROOM_SIZE + t_j
                        self.master_tiles[t_world_i][t_world_j] = t.copy()
                        self.master_tiles[t_world_i][t_world_j].pos = [
                            t_world_j * Tilemap.TILE_SIZE,
                            t_world_i * Tilemap.TILE_SIZE
                        ]
                        self.master_tiles[t_world_i][t_world_j].needs_update = True

        # rooms done
        # [j, i]?
        # start_room = [random.randint(0, self.size-1), 0] # left side
        end_room = [random.randint(0, self.size - 1), self.size - 1]  # right side
        rum_loc = self.r_world[end_room[0]][end_room[1]].spawnpoint
        # make the goal at the end (:
        #self.r_world[end_room[0]][end_room[1]].map[rum_loc[0]][rum_loc[1]]\
        world_i = (end_room[0]*Room.ROOM_SIZE+rum_loc[0])
        world_j = (end_room[1]*Room.ROOM_SIZE+rum_loc[0])
        self.master_tiles[world_i][world_j] = world_handler.gol.generateTile(0, [world_i * Tilemap.TILE_SIZE,world_j * Tilemap.TILE_SIZE])

        #make some treasure -- 30% the number of rooms
        tries = 1000
        successes = 0
        treasure_goal = 0.3
        total_rooms = self.size * self.size
        while tries>0 and successes / total_rooms < treasure_goal:
            tries -= 1
            rand_room = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
            rum = self.r_world[rand_room[0]][rand_room[1]]
            if not rum.has_treasure:
                successes += 1
                tries += 1
                rum.has_treasure = True
                world_i = rand_room[0]*Room.ROOM_SIZE + rum_loc[0]
                world_j = rand_room[1]*Room.ROOM_SIZE + rum_loc[1]
                print('generated a chest')
                self.master_tiles[world_i][world_j] = world_handler.chest.generateTile(0, [world_i * Tilemap.TILE_SIZE, world_j * Tilemap.TILE_SIZE])
                self.master_tiles[world_i][world_j].needs_update = True


        # now images
        self.master_tile_image = world_handler.draw_level(self.master_tiles)
        self.master_opacity_image = world_handler.draw_level(self.master_tiles, True)
        self.draw_portals()
        # todo: need a pre-lit image here
        self.RESCALE = 1.0 # change this depending on rescale to power of 2
    def draw_portals (self):
        # now add portals in the g & b of self.master_opacity_image
        r_i = -1
        for l in self.r_world:
            r_i += 1
            r_j = -1
            for rum in l:
                r_j += 1
                portal = rum.portal
                r_x = r_j * Room.ROOM_SIZE
                r_y = r_i * Room.ROOM_SIZE
                if portal is not None:
                    print('drawing a portal at location %s,%s'%((r_x+portal[0])*Tilemap.TILE_SIZE, (r_y+portal[1])*Tilemap.TILE_SIZE))
                    self.master_opacity_image = self.draw_portal(
                        self.master_opacity_image,
                        (r_x + portal[0]) * Tilemap.TILE_SIZE,
                        (r_y + portal[1]) * Tilemap.TILE_SIZE,
                        (r_x + portal[2]) * Tilemap.TILE_SIZE,
                        (r_y + portal[3]) * Tilemap.TILE_SIZE,
                        Tilemap.TILE_SIZE / 2
                    )
    def constrain (self, v, x, y):
        return min(max(v, x), y)
    def draw_portal (self, surf, x, y, nx, ny, radius):
        # test this
        # 3 ^ (-5 * x ^ 2)
        # or math.sqrt(max(1-r,0))
        w = surf.get_width()
        h = surf.get_height()
        disp = [nx-x, y-ny] # i did y-ny on purpose
        max_distance_range = 128 / (Room.ROOM_SIZE * Tilemap.TILE_SIZE) / LevelHandler.teleport_distance
        for i in range(h):
            if abs(y-i)>radius:
                continue
            for j in range(w):
                if abs(x-j)>radius:
                    continue
                d2 = ((x-j)*(x-j)+(y-i)*(y-i))
                r = math.sqrt(d2) / radius
                intensity = max(1.1 - r * r * r, 0)
                #intensity = 1 if r < 1 else 0
                pr = surf.get_at([j, i]).r
                surf.set_at([j, i], (
                    pr,
                    # about -Room.ROOM_SIZE * Tilemap.TILE_SIZE to
                    #        Room.ROOM_SIZE * Tilemap.TILE_SIZE
                    self.constrain(128+disp[0] * intensity * max_distance_range, 0, 255),
                    self.constrain(128+disp[1] * intensity * max_distance_range, 0, 255)
                    )
                )
                #surf.set_at([j, i], (255 * intensity, 0, 0))
        return surf
    def draw_color (self):
        return self.master_tile_image
    def draw_opacity (self):
        return self.master_opacity_image
    def get_size (self):
        return [self.master_tile_image.get_width(), self.master_tile_image.get_height()]
    def update_tiles (self, world_handler):
        max_redraw = 10
        i = -1
        j = -1
        ZOOM = self.RESCALE
        redraw_portals = False
        for l in self.master_tiles:
            i += 1
            j = -1
            for t in l:
                j += 1
                if t.needs_update:
                    # do updates
                    rum = self.r_world[
                        math.floor(i / Room.ROOM_SIZE)
                    ][
                        math.floor(j / Room.ROOM_SIZE)
                    ]
                    if rum.portal is not None and abs(rum.portal[0]-j) < 2 and abs(rum.portal[1]-i) < 2:
                        redraw_portals = True
                    t.update_pid(world_handler.get_surrounding(self.master_tiles, i, j))
                    # update screen
                    # SCREEN.blit(pygame.transform.scale(t.image, (
                    # int(t.image.get_width() * ZOOM) + 1, int(t.image.get_height() * ZOOM) + 1)),
                    #             (t.pos[0] * ZOOM, t.pos[1] * ZOOM, ZOOM * Tilemap.TILE_SIZE, ZOOM * Tilemap.TILE_SIZE))
                    self.master_tile_image.blit(
                        pygame.transform.scale(
                            t.image, (
                                int(t.image.get_width() * ZOOM) + 1,
                                int(t.image.get_height() * ZOOM) + 1
                            )
                        ),
                        (
                            t.pos[0] * ZOOM,
                            t.pos[1] * ZOOM,
                            ZOOM * Tilemap.TILE_SIZE,
                            ZOOM * Tilemap.TILE_SIZE
                        )
                    )
                    self.master_opacity_image.blit(
                        pygame.transform.scale(
                            t.opacity_image, (
                                int(t.image.get_width() * ZOOM) + 1,
                                int(t.image.get_height() * ZOOM) + 1
                            )
                        ),
                        (
                            t.pos[0] * ZOOM,
                            t.pos[1] * ZOOM,
                            ZOOM * Tilemap.TILE_SIZE,
                            ZOOM * Tilemap.TILE_SIZE
                        )
                    )
                    max_redraw -= 1
                    # now it's updated
                    t.update()
                if max_redraw < 0:
                    break
            if max_redraw < 0:
                break
        if redraw_portals:
            self.draw_portals()


def gaussianBlur (img):
    gaussian = [
     # gaussian blur
        [1, 2, 1],
        [2, 4, 2],
        [1, 2, 1]
    ]
    gsizex = len(gaussian[0])
    gsizey = len(gaussian)
    gcenterx = math.floor(gsizex/2)
    gcentery = math.floor(gsizey/2)
    width = img.get_width()
    height = img.get_height()
    nimg = pygame.Surface((width, height))
    for x in range(width):
        for y in range(height):
            r = 0
            g = 0
            b = 0
            t = 0
            for i in range(gsizey):
                for j in range(gsizex):
                    ri = i-gcentery
                    rj = j-gcenterx
                    if x + rj >= width or y + ri >= height or y + ri < 0 or x + rj < 0:
                        continue
                    p = img.get_at([x + rj, y + ri])
                    gn = gaussian[i][j]
                    r += gn * p.r * p.r
                    g += gn * p.g * p.g
                    b += gn * p.b * p.b
                    t += gn
            t = 1 if t == 0 else t
            r /= t
            g /= t
            b /= t
            nimg.set_at([x, y], (
                min(max(math.sqrt(r), 0), 255),
                min(max(math.sqrt(g), 0), 255),
                min(max(math.sqrt(b), 0), 255)
            ))
    return nimg
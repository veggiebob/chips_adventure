from assets.world_generation import *
from assets.tile_control import *
class LevelHandler:
    def __init__ (self, _size):
        self.size = _size
        self.level = Level(self.size)
        self.level.depth_first_generation()
    def create_layers (self, world_handler):
        # room requirements
        self.rr_world = self.level.level_to_room_reqs()
        # rooms
        self.r_world = []
        # add in rooms according to room reqs
        # todo: use sections as well (defined in world_handler)
        for l in self.rr_world:
            next_t_world = []
            for rr in l:
                selected = False
                for rum in world_handler.ROOMS:
                    if selected:
                        continue
                    if rr.can_contain(rum):
                        selected = True
                        next_t_world.append(rum)
                if not selected:
                    next_t_world.append(world_handler.DEFAULT_ROOM)
            self.r_world.append(next_t_world)
        self.level_width = len(self.r_world[0]) * Room.ROOM_SIZE
        self.level_height = len(self.r_world) * Room.ROOM_SIZE
        self.master_tiles = [[None for i in range(0, self.level_width)] for j in range(0, self.level_height)]
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
        self.master_tile_image = world_handler.draw_level(self.master_tiles)
        self.master_opacity_image = world_handler.draw_level(self.master_tiles, True)
        # todo: need a opacity image here
        # todo: need a pre-lit image here
        self.RESCALE = 1.0 # change this depending on rescale to power of 2
    def draw_color (self):
        return self.master_tile_image
    def draw_opacity (self):
        return self.master_opacity_image
    def update_tiles (self, world_handler):
        max_redraw = 10
        i = -1
        j = -1
        ZOOM = self.RESCALE
        for l in self.master_tiles:
            i += 1
            j = -1
            for t in l:
                j += 1
                if t.needs_update:
                    # do updates
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

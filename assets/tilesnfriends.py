import pygame
class TileCreator:
    def __init__ (self, tilemap, **kwargs):
        # need: name, id
        self.args = {}
        for key, value in kwargs.items():
            self.args[key] = value
        self.tmp = tilemap
    def generateTile(self, tileid, pos):
        self.args['image'] = self.tmp.get_image_index(tileid)
        self.args['opacity_image'] = self.tmp.get_oimage_index(tileid)
        self.args['pos'] = pos
        self.args['tmp'] = self.tmp
        return Tile(**self.args)
class Tile:
    def __init__ (self, **kwargs):
        args = {}
        for key, value in kwargs.items():
            args[key] = value
        self.tmp = args['tmp']
        self.name = args['name']
        self.id = args['id']
        self.pos = args['pos']
        self.image = args['image']
        self.opacity_image = args['opacity_image']
        self.opacity = self.p_opt(args, 'opacity', 1.0)
        self.img_width = self.image.get_width()
        self.img_height = self.image.get_height()
        self.walkable = self.p_opt(args, 'walkable', True)
        self.collider = self.p_opt(args, 'collider', pygame.Rect(0, 0, 0, 0))
        self.needs_update = False
    def p_opt (self, a, k, d=None):
        try:
            return a[k]
        except:
            return d
    def copy (self):
        return Tile(**{
            'tmp':self.tmp,
            'name':self.name,
            'id':self.id,
            'pos':self.pos,
            'image':self.image,
            'walkable':self.walkable,
            'collider':self.collider,
            'opacity':self.opacity,
            'opacity_image': self.opacity_image
        })
    def update_pid (self, pid):
        self.set_image(self.tmp.get_image_index(pid), self.tmp.get_oimage_index(pid))
    def update (self):
        self.needs_update = False
    def set_image (self, img, oimg):
        self.image = img
        self.opacity_image = oimg
    def draw (self):
        return self.image
    def draw_at (self, surf):
        surf.blit(self.image, self.pos)
    def collide (self, collide_rect):
        if self.walkable:
            return False
        else:
            return collide_rect.colliderect(self.collider)
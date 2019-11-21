import pygame, math
class Tilemap:
    TILE_POSITION_INDEXER = [
        [4, 4],
        [4, 2],
        [0, 4],
        [0, 2],
        [4, 0],
        [4, 1],
        [0, 0],
        [0, 1],
        [2, 4],
        [2, 2],
        [1, 4],
        [1, 2],
        [2, 0],
        [2, 1],
        [1, 0],
        [1, 1]
    ]
    TILE_SIZE = 16
    def __init__ (self, filepath):
        self.filepath = filepath
        self.image = pygame.Surface((100, 100))
        self.images = []
        self.loaded = False
        self.load()
    def get_image (self, up, right, down, left):
        if not self.loaded:
            return
        return self.images[up + right * 2 + down * 4 + left * 8]
    def get_image_index (self, ind):
        if not self.loaded:
            return
        return self.images[ind]
    def load_file (self):
        if self.loaded:
            print('reloading from file destination')
        self.image = pygame.image.load(self.filepath)
    def load_images (self, screen=None):
        if self.loaded:
            print('reloading images')
        imgHelp = ImageHelper(self.image)
        self.images = []
        ts = Tilemap.TILE_SIZE
        if screen is not None:
            screen.blit(self.image, (0, 0))
        for i in Tilemap.TILE_POSITION_INDEXER:
            gx = i[0]*ts
            gy = i[1]*ts
            #print('getting from %d, %d'%(gx, gy))
            self.images.append(imgHelp.get_sub(gx, gy, ts, ts))
            if screen is not None:
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(gx+ts*0.05, gy+ts*0.05, ts*0.9, ts*0.9), 1)
    def load (self, screen=None):
        if self.loaded:
            self.loaded = False
            print('reloading the tilemap')
        self.load_file()
        self.load_images(screen)
        self.loaded = True
class RawImage:
    def __init__ (self, pixels):
        self.pixels = pixels
        self.width = len(pixels[0])
        self.height = len(pixels)
    def get_sub_rawimage (self, x, y, w, h):
        x = max(math.floor(x), 0)
        y = max(math.floor(y), 0)
        w = max(math.floor(w), 1)
        h = max(math.floor(h), 1)
        pix = []
        for i in range(y, y+h):
            nextrow = []
            for j in range(x, x+w):
                gp = self.pixels[i][j]
                nextrow.append(gp)
            pix.append(nextrow)
        return RawImage(pix) # image
    def get_surface (self, raw_image=None):
        px = None
        width = 0
        height = 0
        if raw_image is None:
            px = self.pixels
            width = self.width
            height = self.height
        else:
            px = raw_image.pixels
            width = len(px[0])
            height = len(px)

        surf = pygame.Surface((width, height))
        for i in range(0, height):
            for j in range(0, width):
                surf.set_at((j, i), px[i][j])
        return surf
    def get_sub_surface (self, x, y, w, h):
        ri = self.get_sub_rawimage(x, y, w, h)
        return self.get_surface(ri)
    def rotate_clockwise (self):
        p = []
        for i in range(0, self.width):
            p.append([])
            for j in range(0, self.height):
                p[i].append(self.pixels[j][i])
        return RawImage(p)
class ImageHelper:
    def __init__ (self, img):
        self.img = img
        self.raw = RawImage(self.get_pixels(self.img))
    def get_sub (self, x, y, w, h):
        return self.raw.get_sub_surface(x, y, w, h)
    def rotate_clockwise (self):
        self.raw.rotate_clockwise()
        self.img = self.raw.get_surface()
    def rotate_counterclockwise (self):
        self.rotate_clockwise()
        self.rotate_clockwise()
        self.rotate_clockwise()
    def get_pixels (self, img):
        arr = pygame.PixelArray(img)
        i_width = len(arr)
        i_height = len(arr[0])
        pa = []
        # surface.unmap_rgb(int)
        # pa is 2d array of ints
        for row in range(0, i_height):
            pa.append([])
            for col in range(0, i_width):
                pa[row].append(img.unmap_rgb(arr[col][row]))
        return pa

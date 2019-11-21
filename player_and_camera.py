import pygame
class WorldImage:
    def __init__ (self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
class Camera:
    def __init__ (self, x, y, draw_width, draw_height, zoom=1):
        self.x = x
        self.y = y
        self.zoom = zoom
        self.draw_width = draw_width
        self.draw_height = draw_height
    def disp_image (self, wimgs):
        surf = pygame.Surface((self.draw_width, self.draw_height))
        for img in wimgs:
            dx = (img.x-self.x) * self.zoom + self.draw_width/2
            dy = (img.y-self.y) * self.zoom + self.draw_height/2
            dw = img.width * self.zoom
            dh = img.height * self.zoom
            surf.blit(pygame.transform.scale(img.image, (dw, dh)), (dx, dy))
        return surf
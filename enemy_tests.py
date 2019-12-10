from enemy_control import *
import pygame, sys
pygame.init()
SCREEN = pygame.display.set_mode((16, 16))
spritesheet = pygame.image.load('assets/enemy_spritesheet.png')
screech = Enemy('ree', spritesheet, 0, [0, 0], 100, 1, 30)
clock = pygame.time.Clock()
while True:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
    clock.tick(60)
    SCREEN.fill((0,0,0))
    SCREEN.blit(screech.get_image(), (0, 0))
    pygame.display.update()
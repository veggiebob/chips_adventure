import pygame, sys, os
from pygame.locals import *
from level_handling import *
from worldhandling import *
pygame.init()

WIDTH = 576 * 2
HEIGHT = 576
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
yeet = WorldHandler()
test_level = LevelHandler(3)
test_level.create_layers(yeet)
while True:
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
    SCREEN.blit(test_level.draw_opacity(), (0, 0))
    SCREEN.blit(test_level.draw_color(), (576, 0))
    test_level.update_tiles(yeet)
    pygame.display.update()


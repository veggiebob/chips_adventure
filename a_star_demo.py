from a_super_star import a_star
import pygame, sys
from pygame.locals import *
pygame.init()

terrain = [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1],
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0]
]
terrain = [[bool(j) for j in i] for i in terrain]
nadd = a_star(terrain, 0, 0, 4, 4)
curr_pos = [0, 0]
nadd.find_path()

# pygame stuff
screen_size = 400
SCREEN = pygame.display.set_mode((screen_size, screen_size))
SCREEN.fill((0, 0, 0))
bor = 0.9
bor2 = 0.4
sq = screen_size / len(terrain)
for i in range(len(terrain)):
    for j in range(len(terrain[i])):
        x = (j+0.5) * sq
        y = (i+0.5) * sq
        if terrain[i][j]:
            pygame.draw.rect(SCREEN, (255, 255, 255), (x-sq * bor/2, y-sq * bor/2, sq * bor, sq * bor), 0)

for f in nadd.finalPath:
    x = (f[0]+0.5) * sq
    y = (f[1]+0.5) * sq
    pygame.draw.rect(SCREEN, (255, 0, 0), (x-sq * bor2/2, y-sq * bor2/2, sq * bor2, sq * bor2), 0)
while True:
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
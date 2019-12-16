#automatically gets run
import pygame, os
from pygame.locals import *

dicter = {
    (0, 255, 0): 'g', # grass
    (255, 255, 255): 't', # test
    (100, 100, 100): 'm', # metal
    (200, 100, 0): 'w', # wood
    (50, 50, 50): 'c', # cobblestone
    (0, 255, 255): 'l', # glass
    (50, 100, 50): 'v', # vines

    (150, 150, 0): '$', # treasure
    (255, 50, 0): '*', # torch
    (255, 0, 255): 'S' # spawnpoint
}
mainDefault = ' ' # default character for unrecognized colors

def main(runDefault, dictint, imgint):
    imageWorking = pygame.image.load(imgint)
    working = pygame.PixelArray(imageWorking)
    arr = []
    # print(working)
    print(len(working), 'x', len(working[0]))
    for x in range(0, len(working[0])):
        arr.append('')
        for y in range(0, len(working)):
            # print(x, y)
            # print('t')
            # print(working[x][y])
            colornow = tuple(
                imageWorking.unmap_rgb(
                    working[y][x]))
            # print('u')
            colornow = (colornow[0], colornow[1], colornow[2])
            if colornow in dictint:
                arr[x] = arr[x] + dictint[colornow]
            else:
                arr[x] = arr[x] + runDefault
        print(arr[x])
        arr[x] = arr[x] + '\n'
    return arr


# dictFile = open('key.txt', 'r')
# rawDict = dictFile.readlines()
# dictFile.close()

# for i in rawDict:
#     tempProcess = i[i.index(':') + 1:]
#     tempProcess = tempProcess[tempProcess.index("'") + 1:]
#     tempProcess = tempProcess[:tempProcess.index("'")]
#     if i[:i.index(":")] == "default":
#         mainDefault = tempProcess
#     else:
#         destinationKey = tempProcess
#         tempProcess = i[:i.index((':'))]
#         colorKey = []
#         while (tempProcess.__contains__('(')):
#             colorKey.append(int(tempProcess[tempProcess.index('(') + 1:tempProcess.index(')')]))
#             tempProcess = tempProcess[tempProcess.index(')') + 1:]
#         dicter[tuple(colorKey)] = destinationKey

inputArr = os.listdir('input/')

for fileName in inputArr:
    if fileName[len(fileName) - 4:] == '.png':
        print(fileName)
        workingFile = open('output/' + fileName[:len(fileName) - 4] + '.txt', 'w')
        workingFile.writelines(main(mainDefault, dicter, 'input/' + fileName))
        workingFile.close()


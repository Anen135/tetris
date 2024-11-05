import pygame as pg
import random, time, sys  # noqa: E401
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_RETURN, K_SPACE, KEYDOWN, KEYUP, QUIT
import config
from render import Render

def calcSpeed(points):
    # вычисляет уровень
    level = int(points / 10) + 1
    fall_speed = 0.27 - (level * 0.02)
    return level, fall_speed
def getNewFig():
    # возвращает новую фигуру со случайным цветом и углом поворота
    shape = random.choice(list(config.figures.keys()))
    return {
        'shape': shape,
        'rotation': random.randint(0, len(config.figures[shape]) - 1),
        'x': int(config.cup_w / 2) - int(config.fig_w / 2),
        'y': -2, 
        'color': random.randint(0, len(config.colors)-1)
    }
def addToCup(cup, fig):  # sourcery skip: use-itertools-product
    for x in range(config.fig_w):
        for y in range(config.fig_h):
            if config.figures[fig['shape']][fig['rotation']][y][x] != config.empty:
                cup[x + fig['x']][y + fig['y']] = fig['color']

def getkKey():
    for event in pg.event.get():
        if event.type == QUIT:
            return 303
        if event.type == KEYUP:
            return event.key

def checkKeys():
    quitGame()
    return next((event.key for event in pg.event.get([KEYDOWN, KEYUP]) if event.type != KEYDOWN), None)

def shutdown():
    pg.quit()
    sys.exit()

def quitGame():
    for _ in pg.event.get(QUIT): # проверка всех событий, приводящих к выходу из игры
        shutdown() 
    for event in pg.event.get(KEYUP): 
        if event.key == K_ESCAPE:
            shutdown() 
        pg.event.post(event) 

    
def checkPos(cup, fig, adjX=0, adjY=0):
    """
    A function to check if a figure can be positioned within the cup without conflicts.

    Parameters:
        cup (list of lists): The cup grid where the figure is to be placed.
        fig (dict): The figure to be positioned.
        adjX (int): The adjustment in the x-coordinate for positioning the figure.
        adjY (int): The adjustment in the y-coordinate for positioning the figure.

    Returns:
        bool: True if the figure can be positioned without conflicts, False otherwise.
    """
    # sourcery skip: use-itertools-product
    for x in range(config.fig_w):
        for y in range(config.fig_h):
            if y + fig['y'] + adjY < 0 or config.figures[fig['shape']][fig['rotation']][y][x] == config.empty:
                continue
            if x + fig['x'] + adjX < 0 or x + fig['x'] + adjX >= config.cup_w or y + fig['y'] + adjY >= config.cup_h or cup[x + fig['x'] + adjX][y + fig['y'] + adjY] != config.empty:
                return False
    return True

def isCompleted(cup, y):
    return all(cup[x][y] != config.empty for x in range(config.cup_w))

def clearCompleted(cup):  # sourcery skip: invert-any-all
# Удаление заполенных рядов и сдвиг верхних рядов вниз
    removed_lines = 0
    y = config.cup_h - 1 
    while y >= 0:
        if not any(cup[x][y] == config.empty for x in range(config.cup_w)):
            for pushDownY in range(y, 0, -1):
                for x in range(config.cup_w):
                    cup[x][pushDownY] = cup[x][pushDownY-1]
            for x in range(config.cup_w):
                cup[x][0] = config.empty
            removed_lines += 1
        else:
            y -= 1 
    return removed_lines


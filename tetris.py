import pygame
import random, sys  # noqa: E401
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_RETURN, K_SPACE, KEYDOWN, KEYUP, QUIT
import config
from time import time

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

class TetrisEngine:
    def __init__(self):
        self.points = 0 
        self.cup = [[config.empty] * config.cup_h for _ in range(config.cup_w)]
        self.fps_clock = pygame.time.Clock()
        self.display_surf = pygame.display.set_mode((config.window_w, config.window_h))
        self.basic_font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('verdana', 45)
        self.game_on = False
        self.last_fall = time()
        self.last_time = [time(), time()] # [move down, move side]
        self.going = [0,0,0] # [down, left, right]
        self.dir = {
            K_DOWN: 0,
            K_LEFT: 1,
            K_RIGHT: 2
        }
        self.level, self.fall_speed = calcSpeed(self.points)
        self.fallingFig = getNewFig()
        self.nextFig = getNewFig()
    
    def resetGame(self):
        self.points = 0 
        self.cup = [[config.empty] * config.cup_h for _ in range(config.cup_w)]
        self.fps_clock = pygame.time.Clock()
        self.display_surf = pygame.display.set_mode((config.window_w, config.window_h))
        self.basic_font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('verdana', 45)
        self.last_fall = time()
        self.last_time = [time(), time()] # [move down, move side]
        self.going = [0,0,0] # [down, left, right]
        self.dir = {
            K_DOWN: 0,
            K_LEFT: 1,
            K_RIGHT: 2
        }
        self.level, self.fall_speed = calcSpeed(self.points)
        self.fallingFig = getNewFig()
        self.nextFig = getNewFig()
    
    def run(self):
        ...
    
    def draw(self):
        ...
    
    def waitKeys(self):
        while True:
            for event in pygame.event.get(KEYUP):
                if event.key:
                    return event
            pygame.display.update()
            self.fps_clock.tick()
    def tryRotate(self):
        self.fallingFig['rotation'] = (self.fallingFig['rotation'] + 1) % len(config.figures[self.fallingFig['shape']])
        if not checkPos(self.cup, self.fallingFig):
            self.fallingFig['rotation'] = (self.fallingFig['rotation'] - 1) % len(config.figures[self.fallingFig['shape']])
    def hardDrop(self):
        return next((i - 1 for i in range(1, config.cup_h) if not checkPos(self.cup, self.fallingFig, adjY=i)), 0)
    
    def moveFigure(self, going_i, dir, val, time_i, adjX = 0, adjY = 0):
        """
        try to move the falling figure in the given direction

        going_i : the index in self.going to increment [down, left, right]
        dir : the key in self.fallingFig to increment (X or Y)
        val : the value to add to going_i and dir (1 or -1)
        adjY : the adjustment in the y coordinate to use in checkPos (0 or val)
        adjX : the adjustment in the x coordinate to use in checkPos (0 or val)
        time : the index in self.last_time to set to the current time [down or side]

        if the move is possible, sets the last time to the current time
        """
        self.going[going_i] = val
        if checkPos(self.cup, self.fallingFig, adjX=adjX, adjY=adjY):
            self.fallingFig[dir] += val
            self.last_time[time_i] = time()
    
    def fall(self):
        if time() - self.last_fall > self.fall_speed:  # свободное падение фигуры
            if not checkPos(self.cup, self.fallingFig, adjY=1):  # проверка "приземления" фигуры
                addToCup(self.cup, self.fallingFig)  # фигура приземлилась, добавляем ее в содержимое стакана
                self.points += clearCompleted(self.cup)
                self.level, self.fall_speed = calcSpeed(self.points)
                self.fallingFig = None
            else: # фигура пока не приземлилась, продолжаем движение вниз
                self.fallingFig['y'] += 1
                self.last_fall = time()
            #print(self.going)

    def resetTime(self):
        self.last_fall = time()
        self.last_time = [time(), time()]
    
    def TryExit(self):
        self.game_on = False
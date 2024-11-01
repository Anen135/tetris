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
    shape = 'O' # random.choice(list(config.figures.keys()))
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

class Tetris:
    def __init__(self):
        pg.init()
        self.fps_clock = pg.time.Clock()
        self.display_surf = pg.display.set_mode((config.window_w, config.window_h))
        self.basic_font = pg.font.SysFont('arial', 20)
        self.big_font = pg.font.SysFont('verdana', 45)
        pg.display.set_caption('Тетрис')
        self.pauseScreen = pg.Surface((config.window_w, config.window_h), pg.SRCALPHA)
        self.pauseScreen.fill(config.pause_screen_color)
        self.game_on = False
        self.render = Render(self.display_surf)

    def run(self):
        cup = [[config.empty] * config.cup_h for _ in range(config.cup_w)]
        last_move_down = time.time()
        last_side_move = time.time()
        last_fall = time.time()
        going = [0,0,0] # [down, left, right]
        dir = {
            K_DOWN: 0,
            K_LEFT: 1,
            K_RIGHT: 2
        }
        points = 0
        level, fall_speed = calcSpeed(points)
        fallingFig = getNewFig()
        nextFig = getNewFig()
        self.game_on = True
        self.render.drawPopup('Тетрис')
        def gameDraw():
            quitGame()
            # рисуем окно игры со всеми надписями
            self.display_surf.fill(config.bg_color)
            self.render.drawTitle()
            self.render.drawGameCup(cup)
            self.render.drawInfos(points, level)
            self.render.drawnextFig(nextFig)
            if not fallingFig: 
                raise ValueError('Не найдена фигура') 
            self.render.drawFig(fallingFig)
            pg.display.update()
            self.fps_clock.tick(config.fps)
        while not checkKeys():
            pg.display.update()
            self.fps_clock.tick()
        while self.game_on:
            if not fallingFig:
                # если нет падающих фигур, генерируем новую
                fallingFig = nextFig
                nextFig = getNewFig()
                last_fall = time.time()

                if not checkPos(cup, fallingFig):
                    return # если на игровом поле нет свободного места - игра закончена
            gameDraw()

            for event in pg.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        self.display_surf.blit(self.pauseScreen, (0, 0))
                        self.render.drawPopup("Пауза")
                        while not checkKeys():
                            pg.display.update()
                            self.fps_clock.tick()
                        last_fall = time.time()
                        last_move_down = time.time()
                    if event.key in dir:
                        going[dir[event.key]] = 0
                elif event.type == KEYDOWN:
                    # поворачиваем фигуру, если есть место
                    if event.key == K_UP:
                        fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(config.figures[fallingFig['shape']])
                        if not checkPos(cup, fallingFig):
                            fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(config.figures[fallingFig['shape']])
                        break
                    # мгновенный сброс вниз
                    elif event.key == K_RETURN:
                        for i in range(1, config.cup_h):
                            if not checkPos(cup, fallingFig, adjY=i):break
                        fallingFig['y'] += i - 1
                        break
                    # ускоряем падение фигуры
                    if event.key == K_DOWN:
                        going[0] = 1
                        if checkPos(cup, fallingFig, adjY=going[0]):
                            fallingFig['y'] += going[0]
                            last_move_down = time.time()
                    # перемещение фигуры вправо и влево
                    if event.key == K_LEFT:
                        going[1] = -1
                        if checkPos(cup, fallingFig, adjX=going[1]):
                            fallingFig['x'] += going[1]
                            last_side_move = time.time()
                    elif event.key == K_RIGHT:
                        going[2] = 1
                        if checkPos(cup, fallingFig, adjX=going[2]):
                            fallingFig['x'] += going[2]
                            last_side_move = time.time()

            # управление падением фигуры при удержании клавиш
            if time.time() - last_side_move > config.side_freq:
                if going[1] and checkPos(cup, fallingFig, adjX=-1):
                    fallingFig['x'] += going[1]
                elif going[2] and checkPos(cup, fallingFig, adjX=1):
                    fallingFig['x'] += going[2]
                last_side_move = time.time()

            if going[0] and time.time() - last_move_down > config.down_freq and checkPos(cup, fallingFig, adjY=1):
                fallingFig['y'] += going[0]
                last_move_down = time.time()


            if time.time() - last_fall > fall_speed: # свободное падение фигуры            
                if not checkPos(cup, fallingFig, adjY=1): # проверка "приземления" фигуры
                    addToCup(cup, fallingFig) # фигура приземлилась, добавляем ее в содержимое стакана
                    points += clearCompleted(cup)
                    level, fall_speed = calcSpeed(points)
                    fallingFig = None
                else: # фигура пока не приземлилась, продолжаем движение вниз
                    fallingFig['y'] += 1
                    last_fall = time.time()
            print(going)


if __name__ == '__main__':
    app = Tetris()
    app.run()
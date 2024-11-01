import pygame as pg
import random, time, sys  # noqa: E401
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_RETURN, K_SPACE, KEYDOWN, KEYUP, QUIT
import config
from render import Render

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
        going_down = False
        going_left = False
        going_right = False
        points = 0
        level, fall_speed = self.calcSpeed(points)
        fallingFig = self.getNewFig()
        nextFig = self.getNewFig()
        self.game_on = True
        self.render.drawPopup('Тетрис')
        while not self.checkKeys():
            pg.display.update()
            self.fps_clock.tick()
        while self.game_on:
            if not fallingFig:
                # если нет падающих фигур, генерируем новую
                fallingFig = nextFig
                nextFig = self.getNewFig()
                last_fall = time.time()

                if not self.checkPos(cup, fallingFig):
                    return # если на игровом поле нет свободного места - игра закончена
            self.quitGame()
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
            for event in pg.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        self.display_surf.blit(self.pauseScreen, (0, 0))
                        self.render.drawPopup("Пауза")
                        while not self.checkKeys():
                            pg.display.update()
                            self.fps_clock.tick()
                        last_fall = time.time()
                        last_move_down = time.time()
                        last_side_move = time.time()
                    elif event.key == K_LEFT:
                        going_left = False
                    elif event.key == K_RIGHT:
                        going_right = False
                    elif event.key == K_DOWN:
                        going_down = False

                elif event.type == KEYDOWN:
                    # перемещение фигуры вправо и влево
                    if event.key == K_LEFT and self.checkPos(cup, fallingFig, adjX=-1):
                        fallingFig['x'] -= 1
                        going_left = True
                        going_right = False
                        last_side_move = time.time()

                    elif event.key == K_RIGHT and self.checkPos(cup, fallingFig, adjX=1):
                        fallingFig['x'] += 1
                        going_right = True
                        going_left = False
                        last_side_move = time.time()

                    # поворачиваем фигуру, если есть место
                    elif event.key == K_UP:
                        fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(config.figures[fallingFig['shape']])
                        if not self.checkPos(cup, fallingFig):
                            fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(config.figures[fallingFig['shape']])

                    # ускоряем падение фигуры
                    elif event.key == K_DOWN:
                        going_down = True
                        if self.checkPos(cup, fallingFig, adjY=1):
                            fallingFig['y'] += 1
                        last_move_down = time.time()

                    # мгновенный сброс вниз
                    elif event.key == K_RETURN:
                        going_down = False
                        going_left = False
                        going_right = False
                        for i in range(1, config.cup_h):
                            if not self.checkPos(cup, fallingFig, adjY=i):
                                break
                        fallingFig['y'] += i - 1

            # управление падением фигуры при удержании клавиш
            if (going_left or going_right) and time.time() - last_side_move > config.side_freq:
                if going_left and self.checkPos(cup, fallingFig, adjX=-1):
                    fallingFig['x'] -= 1
                elif going_right and self.checkPos(cup, fallingFig, adjX=1):
                    fallingFig['x'] += 1
                last_side_move = time.time()

            if going_down and time.time() - last_move_down > config.down_freq and self.checkPos(cup, fallingFig, adjY=1):
                fallingFig['y'] += 1
                last_move_down = time.time()


            if time.time() - last_fall > fall_speed: # свободное падение фигуры            
                if not self.checkPos(cup, fallingFig, adjY=1): # проверка "приземления" фигуры
                    self.addToCup(cup, fallingFig) # фигура приземлилась, добавляем ее в содержимое стакана
                    points += self.clearCompleted(cup)
                    level, fall_speed = self.calcSpeed(points)
                    fallingFig = None
                else: # фигура пока не приземлилась, продолжаем движение вниз
                    fallingFig['y'] += 1
                    last_fall = time.time()


    
    def checkKeys(self):
        self.quitGame()
        return next((event.key for event in pg.event.get([KEYDOWN, KEYUP]) if event.type != KEYDOWN), None)
    
    def shutdown(self):
        pg.quit()
        sys.exit()
    
    def quitGame(self):
        for _ in pg.event.get(QUIT): # проверка всех событий, приводящих к выходу из игры
            self.shutdown() 
        for event in pg.event.get(KEYUP): 
            print(event.key)
            if event.key == K_ESCAPE:
                self.shutdown() 
            pg.event.post(event) 
    
    def calcSpeed(self, points):
        # вычисляет уровень
        level = int(points / 10) + 1
        fall_speed = 0.27 - (level * 0.02)
        return level, fall_speed

    def getNewFig(self):
        # возвращает новую фигуру со случайным цветом и углом поворота
        shape = 'O' # random.choice(list(config.figures.keys()))
        return {
            'shape': shape,
            'rotation': random.randint(0, len(config.figures[shape]) - 1),
            'x': int(config.cup_w / 2) - int(config.fig_w / 2),
            'y': -2, 
            'color': random.randint(0, len(config.colors)-1)
        }

    def addToCup(self, cup, fig):  # sourcery skip: use-itertools-product
        for x in range(config.fig_w):
            for y in range(config.fig_h):
                if config.figures[fig['shape']][fig['rotation']][y][x] != config.empty:
                    cup[x + fig['x']][y + fig['y']] = fig['color']
    
    def checkPos(self, cup, fig, adjX=0, adjY=0):
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


    def isCompleted(self, cup, y):
        return all(cup[x][y] != config.empty for x in range(config.cup_w))

    def clearCompleted(self, cup):  # sourcery skip: invert-any-all
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

    
    def convertCoords(self, block_x, block_y):
        return (config.side_margin + (block_x * config.block)), (config.top_margin + (block_y * config.block))
    
    def drawBlock(self, block_x, block_y, color, pixelx=None, pixely=None):
        #отрисовка квадратных блоков, из которых состоят фигуры
        if color == config.empty:
            return
        if not (pixelx and pixely):
            pixelx, pixely = self.convertCoords(block_x, block_y)
        pg.draw.rect(self.display_surf, config.colors[color], (pixelx + 1, pixely + 1, config.block - 1, config.block - 1), 0, 3)
        pg.draw.rect(self.display_surf, config.lightcolors[color], (pixelx + 1, pixely + 1, config.block - 4, config.block - 4), 0, 3)
        pg.draw.circle(self.display_surf, config.colors[color], (pixelx + config.block / 2, pixely + config.block / 2), 5)
    
    def drawTitle(self):
        titleSurf = self.basic_font.render('Тетрис Lite', True, config.title_color)
        self.drawText(titleSurf, 425, 30)
    
    def drawInfos(self, points, level):
        self.drawText(self.basic_font.render(f'Баллы: {points}', True, config.txt_color), 550, 180)
        self.drawText(self.basic_font.render(f'Уровень: {level}', True, config.txt_color), 550, 250)
        self.drawText(self.basic_font.render('Пауза: пробел', True, config.info_color), 550, 420)
        self.drawText(self.basic_font.render('Выход: Esc', True, config.info_color), 550, 450)

    def drawFig(self, fig, pixelx=None, pixely=None):
        figToDraw = config.figures[fig['shape']][fig['rotation']]
        if not (pixelx and pixely):    
            pixelx, pixely = self.convertCoords(fig['x'], fig['y'])

        #отрисовка элементов фигур
        for x in range(config.fig_w):
            for y in range(config.fig_h):
                if figToDraw[y][x] != config.empty:
                    self.drawBlock(None, None, fig['color'], pixelx + (x * config.block), pixely + (y * config.block))


    def drawnextFig(self, fig):  # превью следующей фигуры
        nextSurf = self.basic_font.render('Следующая:', True, config.txt_color)
        self.drawText(nextSurf, 150, 180)
        self.drawFig(fig, pixelx=config.window_w-150, pixely=230)
        
    def drawText(self, surf, x, y):
        titleRect = surf.get_rect()
        titleRect.topleft = config.window_w - x, y
        self.display_surf.blit(surf, titleRect)

if __name__ == '__main__':
    app = Tetris()
    app.run()
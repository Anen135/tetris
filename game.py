import pygame
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_RETURN, K_SPACE, KEYDOWN, KEYUP, K_ESCAPE
import config
import time
from render import Render
import tetris

class Game:
    def __init__(self, render):
        self.render = render
        self.game_on = False
        self.cup = [[config.empty] * config.cup_h for _ in range(config.cup_w)]
        self.last_fall = time.time()
        self.last_time = [time.time(), time.time()] # [move down, move side]
        self.going = [0,0,0] # [down, left, right]
        self.dir = {
            K_DOWN: 0,
            K_LEFT: 1,
            K_RIGHT: 2
        }
        self.points = 0
        self.level, self.fall_speed = tetris.calcSpeed(self.points)
        self.fallingFig = tetris.getNewFig()
        self.nextFig = tetris.getNewFig()

    def draw(self):
        tetris.quitGame()
        # рисуем окно игры со всеми надписями
        self.display_surf.fill(config.bg_color)
        self.render.drawTitle()
        self.render.drawGameCup(self.cup)
        self.render.drawInfos(self.points, self.level)
        self.render.drawnextFig(self.nextFig)
        assert self.fallingFig
        self.render.drawFig(self.fallingFig)
        pygame.display.update()
        self.fps_clock.tick(config.fps)
    
    def waitKeys(self):
        while not tetris.checkKeys():
            pygame.display.update()
            self.fps_clock.tick()
    
    def pause(self):
        self.display_surf.blit(self.pauseScreen, (0, 0))
        self.render.drawPopup("Пауза")
        while not tetris.checkKeys():
            pygame.display.update()
            self.fps_clock.tick()
        self.last_fall = time.time()
        self.last_time = [time.time(), time.time()]
    
    def tryRotate(self):
        self.fallingFig['rotation'] = (self.fallingFig['rotation'] + 1) % len(config.figures[self.fallingFig['shape']])
        if not tetris.checkPos(self.cup, self.fallingFig):
            self.fallingFig['rotation'] = (self.fallingFig['rotation'] - 1) % len(config.figures[self.fallingFig['shape']])
    def hardDrop(self):
        return next((i - 1 for i in range(1, config.cup_h) if not tetris.checkPos(self.cup, self.fallingFig, adjY=i)), 0)
    def tryMoveDown(self):
        self.going[0] = 1
        if tetris.checkPos(self.cup, self.fallingFig, adjY=self.going[0], adjX=0):
            self.fallingFig['y'] += self.going[0]
            self.last_time[0] = time.time()

    def tryMoveLeft(self):
        self.going[1] = -1
        if tetris.checkPos(self.cup, self.fallingFig, adjX=self.going[1], adjY=0):
            self.fallingFig['x'] += self.going[1]
            self.last_time[1] = time.time()
    
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
        if tetris.checkPos(self.cup, self.fallingFig, adjX=adjX, adjY=adjY):
            self.fallingFig[dir] += val
            self.last_time[time_i] = time.time()
    
    def fall(self):
        if not tetris.checkPos(self.cup, self.fallingFig, adjY=1):  # проверка "приземления" фигуры
            tetris.addToCup(self.cup, self.fallingFig)  # фигура приземлилась, добавляем ее в содержимое стакана
            self.points += tetris.clearCompleted(self.cup)
            self.level, self.fall_speed = tetris.calcSpeed(self.points)
            self.fallingFig = None
        else: # фигура пока не приземлилась, продолжаем движение вниз
            self.fallingFig['y'] += 1
            self.last_fall = time.time()

    def run(self):
        self.render.drawPopup('Тетрис')
        self.waitKeys()
        self.game_on = True
        while self.game_on:
            if not self.fallingFig:
                # если нет падающих фигур, генерируем новую
                self.fallingFig = self.nextFig
                self.nextFig = tetris.getNewFig()
                self.last_fall = time.time()

                if not tetris.checkPos(self.cup, self.fallingFig): # если на игровом поле нет свободного места - игра закончена
                    self.game_on = False
                    break
            self.draw()
            # Управление фигурой
            for event in pygame.event.get():
                match event.type:
                    case pygame.KEYUP:
                        if event.key == K_ESCAPE:
                            tetris.shutdown()
                            break
                        elif event.key == K_SPACE:
                            self.pause()
                            break
                        if event.key in self.dir:
                            self.going[self.dir[event.key]] = 0
                            continue
                    case pygame.KEYDOWN:
                        if event.key == K_UP:
                            self.tryRotate() # поворачиваем фигуру, если есть место
                            break
                        # мгновенный сброс вниз
                        elif event.key == K_RETURN:                
                            self.fallingFig['y'] += self.hardDrop()
                            break
                        # ускоряем падение фигуры
                        if event.key == K_DOWN:
                            # ускоряем падение фигуры
                            self.moveFigure(going_i=0, dir='y', val=1, adjY=1, time_i=0)
                        # перемещение фигуры вправо и влево
                        if event.key == K_LEFT:
                            self.moveFigure(going_i=1, dir="x", val=-1, adjX=-1, time_i=1)
                        elif event.key == K_RIGHT:
                            self.moveFigure(going_i=2, dir="x", val=1, adjX=1, time_i=1)
            # управление фигурой при удержании клавиш
            if time.time() - self.last_time[1] > config.side_freq:
                if self.going[1] and tetris.checkPos(self.cup, self.fallingFig, adjX=-1):
                    self.fallingFig['x'] += self.going[1]
                elif self.going[2] and tetris.checkPos(self.cup, self.fallingFig, adjX=1):
                    self.fallingFig['x'] += self.going[2]
                self.last_time[1] = time.time()
            if time.time() - self.last_time[0] > config.down_freq and tetris.checkPos(self.cup, self.fallingFig, adjY=1) and self.going[0]:
                self.fallingFig['y'] += self.going[0]
                self.last_time[0] = time.time()
            if time.time() - self.last_fall > self.fall_speed:  # свободное падение фигуры
                self.fall()
                print(self.going)
                
if __name__ == '__main__':
    pygame.init()
    app = Game(Render(pygame.display.set_mode((config.window_w, config.window_h))))
    app.fps_clock = pygame.time.Clock()
    app.display_surf = pygame.display.set_mode((config.window_w, config.window_h))
    app.basic_font = pygame.font.SysFont('arial', 20)
    app.big_font = pygame.font.SysFont('verdana', 45)
    pygame.display.set_caption('Тетрис')
    app.pauseScreen = pygame.Surface((config.window_w, config.window_h), pygame.SRCALPHA)
    app.pauseScreen.fill(config.pause_screen_color)
    app.game_on = False
    app.run()
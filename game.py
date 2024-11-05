import pygame
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_RETURN, K_SPACE, K_ESCAPE
import pygame.locals
import config
import time
from render import Render
import tetris

class Game(tetris.TetrisEngine):
    def __init__(self, render):
        super().__init__()
        pygame.display.set_caption('Тетрис')
        self.pauseScreen = pygame.Surface((config.window_w, config.window_h), pygame.SRCALPHA)
        self.pauseScreen.fill(config.pause_screen_color)
        self.render = render

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
    
    def pause(self):
        self.display_surf.blit(self.pauseScreen, (0, 0))
        self.render.drawPopup("Пауза")
        tetris.quitGame()
        while not tetris.checkKeys():
            pygame.display.update()
            self.fps_clock.tick()
        self.last_fall = time.time()
        self.last_time = [time.time(), time.time()]
    
    def controller(self):
        # Управление фигурой
        for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP]):
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
                        super().tryRotate() # поворачиваем фигуру, если есть место
                        break
                    # мгновенный сброс вниз
                    elif event.key == K_RETURN:                
                        self.fallingFig['y'] += super().hardDrop()
                        break
                    # ускоряем падение фигуры
                    if event.key == K_DOWN:
                        # ускоряем падение фигуры
                        super().moveFigure(going_i=0, dir='y', val=1, adjY=1, time_i=0)
                    # перемещение фигуры вправо и влево
                    if event.key == K_LEFT:
                        super().moveFigure(going_i=1, dir="x", val=-1, adjX=-1, time_i=1)
                    elif event.key == K_RIGHT:
                        super().moveFigure(going_i=2, dir="x", val=1, adjX=1, time_i=1)
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

    def run(self):
        self.render.drawPopup('Тетрис')
        super().waitKeys()
        self.game_on = True
        while self.game_on:
            tetris.quitGame()
            if not self.fallingFig:
                # если нет падающих фигур, генерируем новую
                self.fallingFig = self.nextFig
                self.nextFig = tetris.getNewFig()
                self.last_fall = time.time()

                if not tetris.checkPos(self.cup, self.fallingFig): # если на игровом поле нет свободного места - игра закончена
                    self.game_on = False
                    break
            self.draw()
            self.controller()
            super().fall()
                
if __name__ == '__main__':
    pygame.init()
    app = Game(Render(pygame.display.set_mode((config.window_w, config.window_h))))
    app.run()
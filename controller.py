import tetris
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_RETURN, K_SPACE, K_ESCAPE, K_r
from pygame.locals import KEYDOWN, KEYUP
from config import side_freq, down_freq
from pygame.event import get as get_events
from time import time
class Controller:
    def __init__(self, game):
        self.game = game  # ссылка на объект Game
    def handle_keyup(self, event):
        """Обработка событий при отпускании клавиш."""
        if event.key == K_ESCAPE:
            self.game.TryExit()
        elif event.key == K_SPACE:
            self.game.pause_on = not self.game.pause_on
            if self.game.pause_on:
                self.game.pause()
        elif event.key == K_r:
            self.game.resetGame()
        elif event.key in self.game.dir:
            self.game.going[self.game.dir[event.key]] = 0

    def handle_keydown(self, event):
        """Обработка событий при нажатии клавиш."""
        if event.key == K_UP:
            self.game.tryRotate()
        elif event.key == K_RETURN:
            self.game.fallingFig['y'] += self.game.hardDrop()
        elif event.key == K_DOWN:
            self.game.moveFigure(going_i=0, dir='y', val=1, adjY=1, time_i=0)
        elif event.key == K_LEFT:
            self.game.moveFigure(going_i=1, dir="x", val=-1, adjX=-1, time_i=1)
        elif event.key == K_RIGHT:
            self.game.moveFigure(going_i=2, dir="x", val=1, adjX=1, time_i=1)

    def handle_key_hold(self):
        """Обработка движения при удерживании клавиш."""
        current_time = time()
        if current_time - self.game.last_time[1] > side_freq:
            if self.game.going[1] and tetris.checkPos(self.game.cup, self.game.fallingFig, adjX=-1):
                self.game.fallingFig['x'] += self.game.going[1]
            elif self.game.going[2] and tetris.checkPos(self.game.cup, self.game.fallingFig, adjX=1):
                self.game.fallingFig['x'] += self.game.going[2]
            self.game.last_time[1] = current_time
        if current_time - self.game.last_time[0] > down_freq and tetris.checkPos(self.game.cup, self.game.fallingFig, adjY=1) and self.game.going[0]:
            self.game.fallingFig['y'] += self.game.going[0]
            self.game.last_time[0] = current_time

    def handle_events(self):
        """Основной метод обработки событий, вызывающий вспомогательные обработчики."""
        for event in get_events([KEYDOWN, KEYUP]):
            if event.type == KEYUP:
                self.handle_keyup(event)
            elif event.type == KEYDOWN:
                self.handle_keydown(event)
        self.handle_key_hold()
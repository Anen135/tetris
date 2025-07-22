import pygame
import pygame.locals
import config
from render import Render
import tetris
from controller import Controller

class Game(tetris.TetrisEngine):
    def __init__(self, render):
        super().__init__()
        pygame.display.set_caption('Тетрис')
        self.pauseScreen = pygame.Surface((config.window_w, config.window_h), pygame.SRCALPHA)
        self.pauseScreen.fill(config.pause_screen_color)
        self.render = render
        self.pause_on = False
        self.controller = Controller(self)  # добавляем контроллер

    def draw(self):
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
        event = super().waitKeys()
        if event.key == pygame.K_PAUSE: return
        self.controller.handle_keyup(event)  # передача события в контроллер
        super().resetTime()

    def run(self):
        self.game_on = True
        while self.game_on:
            if not self.fallingFig:
                # если нет падающих фигур, генерируем новую
                self.fallingFig = self.nextFig
                self.nextFig = tetris.getNewFig()
                super().resetTime()

                if not tetris.checkPos(self.cup, self.fallingFig): # если на игровом поле нет свободного места - игра закончена
                    self.game_on = False
                    break
            self.draw()
            self.controller.handle_events()  # управление передано контроллеру
            super().fall()

if __name__ == '__main__':
    pygame.init()
    while True:
        app = Game(Render(pygame.display.set_mode((config.window_w, config.window_h))))
        app.run()

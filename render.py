import pygame as pg
from config import window_w, txt_color, figures, block, fig_h, fig_w, empty, info_color, title_color, colors, lightcolors, window_h, bg_color, brd_color, side_margin, top_margin, cup_w, cup_h


def txtObjects(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

class Render:
    def __init__(self, surface):
        self.surface = surface
        self.basic_font = pg.font.SysFont('arial', 20)
        self.big_font = pg.font.SysFont('verdana', 45)
    
    def drawText(self, surf, x, y):
        titleRect = surf.get_rect()
        titleRect.topleft = window_w - x, y
        self.surface.blit(surf, titleRect)

    def drawnextFig(self, fig):  # превью следующей фигуры
        self.drawText(self.basic_font.render('Следующая:', True, txt_color), 150, 180)
        self.drawFig(fig, pixelx=window_w-150, pixely=230)
    
    def drawFig(self, fig, pixelx=None, pixely=None):
        # sourcery skip: use-itertools-product
        figToDraw = figures[fig['shape']][fig['rotation']]
        if not (pixelx and pixely): pixelx, pixely = side_margin + (fig['x'] * block), top_margin + (fig['y'] * block)

        #отрисовка элементов фигур
        for x in range(fig_w):
            for y in range(fig_h):
                if figToDraw[y][x] != empty: self.drawBlock(None, None, fig['color'], pixelx + (x * block), pixely + (y * block))
    
    def drawInfos(self, points, level):
        self.drawText(self.basic_font.render(f'Баллы: {points}', True, txt_color), 550, 180)
        self.drawText(self.basic_font.render(f'Уровень: {level}', True, txt_color), 550, 250)
        self.drawText(self.basic_font.render('Пауза: пробел', True, info_color), 550, 420)
        self.drawText(self.basic_font.render('Выход: Esc', True, info_color), 550, 450)

    def drawTitle(self):
        titleSurf = self.big_font.render('Тетрис', True, title_color)
        self.drawText(titleSurf, 385, 30)
    
    def drawBlock(self, block_x, block_y, color, pixelx=None, pixely=None):
        #отрисовка квадратных блоков, из которых состоят фигуры
        if color == empty: return
        if not (pixelx and pixely): pixelx, pixely = side_margin + (block_x * block), top_margin + (block_y * block)
        pg.draw.rect(self.surface, colors[color], (pixelx + 1, pixely + 1, block - 1, block - 1), 0, 3)
        pg.draw.rect(self.surface, lightcolors[color], (pixelx + 1, pixely + 1, block - 4, block - 4), 0, 3)
        pg.draw.circle(self.surface, colors[color], (pixelx + block / 2, pixely + block / 2), 5)
    
    def drawPopup(self, text):
        titleSurf, titleRect = txtObjects(text, self.big_font, title_color)
        titleRect.center = (int(window_w / 2) - 3, int(window_h / 3) - 3)
        self.surface.blit(titleSurf, titleRect)
    
        pressKeySurf, pressKeyRect = txtObjects('Нажмите любую клавишу для продолжения', self.basic_font, title_color)
        pressKeyRect.center = (int(window_w / 2), int(window_h / 2) + 100)
        self.surface.blit(pressKeySurf, pressKeyRect)

    def drawGameCup(self, cup):
        # рамка игрового поля
        pg.draw.rect(self.surface, brd_color, (side_margin - 4, top_margin - 4, (cup_w * block) + 8, (cup_h * block) + 8), 5)

        # фон игрового поля
        pg.draw.rect(self.surface, bg_color, (side_margin, top_margin, block * cup_w, block * cup_h))
        for x in range(cup_w):
            for y in range(cup_h):
                self.drawBlock(x, y, cup[x][y])

    

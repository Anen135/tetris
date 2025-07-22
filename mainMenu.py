import pygame
import sys
from game import Game
from render import Render
from config import window_w, window_h
from settingsMenu import SettingsMenu

class MainMenu:
    def __init__(self, screen, font, background_color=(0, 0, 0), text_color=(255, 255, 255)):
        self.screen = screen
        self.font = font
        self.background_color = background_color
        self.text_color = text_color
        self.options = ["Tetris", "Settings", "Exit"]
        self.selected_option = 0
        self.option_spacing = 40  # Расстояние между пунктами меню

    def draw_menu(self):
        """Рисует меню и выделяет выбранный пункт."""
        self.screen.fill(self.background_color)
        
        # Отрисовка всех пунктов меню
        for index, option in enumerate(self.options):
            color = self.text_color
            if index == self.selected_option:  # Выделение выбранного пункта
                color = (255, 215, 0)  # Цвет выделения
            
            # Рендер текста и позиционирование
            label = self.font.render(option, True, color)
            label_rect = label.get_rect(center=(self.screen.get_width() / 2,
                                                self.screen.get_height() / 2 + index * self.option_spacing))
            self.screen.blit(label, label_rect)

        pygame.display.flip()

    def handle_input(self):
        """Обрабатывает ввод для управления меню."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected_option]  # Возвращает выбранный пункт меню

        return None  # Ничего не выбрано, продолжаем в меню

    def run(self):
        """Запускает цикл отображения и обработки меню."""
        while True:
            selected_option = self.handle_input()
            if selected_option:  # Выбрана опция
                return selected_option  # Возвращаем выбранную опцию
            
            self.draw_menu()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 50)  # Используем шрифт по умолчанию
    menu = MainMenu(screen, font)
    while True:
        selected = menu.run()
        match selected:
            case "Tetris":
                app = Game(Render(pygame.display.set_mode((window_w, window_h))))
                app.run()
            case "Settings":
                settings_menu = SettingsMenu(screen, font)
                music_on = settings_menu.run()
            case "Exit":
                break
    pygame.quit()

import pygame
import sys

class SettingsMenu:
    def __init__(self, screen, font, music_on=True, background_color=(0, 0, 0), text_color=(255, 255, 255)):
        self.screen = screen
        self.font = font
        self.background_color = background_color
        self.text_color = text_color
        self.options = ["Toggle Music", "Back"]
        self.selected_option = 0
        self.option_spacing = 40
        self.music_on = music_on  # Текущее состояние музыки

    def draw_menu(self):
        """Рисует меню настроек и выделяет выбранный пункт."""
        self.screen.fill(self.background_color)

        # Отрисовка всех пунктов меню
        for index, option in enumerate(self.options):
            color = self.text_color
            if index == self.selected_option:
                color = (255, 215, 0)  # Цвет выделения
            
            # Дописываем состояние музыки в пункт "Toggle Music"
            label_text = option
            if option == "Toggle Music":
                label_text += f" -- {'On' if self.music_on else 'Off'}"
            
            # Рендер текста и позиционирование
            label = self.font.render(label_text, True, color)
            label_rect = label.get_rect(center=(self.screen.get_width() / 2,
                                                self.screen.get_height() / 2 + index * self.option_spacing))
            self.screen.blit(label, label_rect)

        pygame.display.flip()

    def handle_input(self):
        """Обрабатывает ввод для управления меню настроек."""
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
                    # Проверяем выбранный пункт
                    if self.selected_option == 0:
                        self.music_on = not self.music_on  # Переключаем состояние музыки
                    elif self.selected_option == 1:
                        return "Back"  # Выход из настроек
        return None

    def run(self):
        """Запускает цикл отображения и обработки меню настроек."""
        while True:
            selected_option = self.handle_input()
            if selected_option == "Back":
                return self.music_on  # Возвращаем текущее состояние музыки
            
            self.draw_menu()


# Для тестирования можно добавить запуск, если этот файл запускается напрямую.
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 50)  # Используем шрифт по умолчанию
    settings_menu = SettingsMenu(screen, font)
    music_on = settings_menu.run()
    print(f"Музыка включена: {music_on}")
    pygame.quit()

import pygame as pg

from .Button import Button
from .DropDownButton import DropDownButton

class MainMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background = pg.image.load("Assets/MainMenu/Background.jpg")
        rect1 = pg.image.load("Assets/MainMenu/Play Rect.png")
        rect2 = pg.image.load("Assets/MainMenu/Quit Rect.png")
        self.font_main = "Assets/MainMenu/Font.ttf"
        self.font_options = None
        options_map_size = ["Small", "Medium", "Large"]
        options_num_players = ["2", "3", "4", "5"]
        self.game_state = 0
        self.button_play = Button(rect1, self.width // 2, self.height // 3, "PLAY",
                             self.font_main, "White", "Gray", 75)
        self.button_quit = Button(rect2, self.width // 2, 0.55*self.height, "QUIT",
                             self.font_main, "White", "Gray", 75)
        self.button_map_size = DropDownButton(rect1, self.width // 4, self.height // 4,
                                         "MAP", self.font_options, "White",
                                         "Gray", 75, options_map_size,(169, 169, 169))
        self.button_number_players = DropDownButton(rect2, 3 * self.width // 4, self.height // 4,
                                               "PLAYERS", self.font_options, "White",
                                               "Gray", 75, options_num_players,
                                               (169, 169, 169))
        self.button_start_game = Button(rect1, self.width // 2, self.height // 2,
                                   "START GAME", self.font_options, "White", "Gray", 75)

    def draw_game_name(self, screen):
        screen.blit(self.background, (0, 0))
        menu_text = self.button_play.get_font(100).render("PyKingdom", True, "#ffd700")
        menu_rect = menu_text.get_rect(center=(self.width // 2, self.height // 10))
        screen.blit(menu_text, menu_rect)

    def check_dropdown(self, mouse_pos):
        self.button_map_size.check_input(mouse_pos)
        self.button_number_players.check_input(mouse_pos)

    def draw_menu_buttons(self, screen, mouse_pos):
        if self.game_state == 0:

            self.draw_game_name(screen)

            self.button_play.update(screen, mouse_pos)
            self.button_quit.update(screen, mouse_pos)

        elif self.game_state == 1:
            self.draw_game_name(screen)

            self.button_map_size.draw_dropdown(screen, mouse_pos)
            self.button_map_size.update(screen, mouse_pos)

            self.button_number_players.draw_dropdown(screen, mouse_pos)
            self.button_number_players.update(screen, mouse_pos)

            self.button_start_game.update(screen, mouse_pos)

    def get_game_state(self):
        return self.game_state

    def set_game_state(self, game_state):
        self.game_state = game_state

    def check_input_play(self, mouse_pos):
        if self.button_play.check_for_input(mouse_pos) and self.game_state == 0:
            return True

        return False

    def check_input_quit(self, mouse_pos):
        if self.button_quit.check_for_input(mouse_pos) and self.game_state == 0:
            return True

        return False

    def check_input_start(self, mouse_pos):
        if self.button_start_game.check_for_input(mouse_pos) and self.game_state == 1:
            return True

        return False

    def check_input_dropdown(self, mouse_pos):
        return self.game_state == 1


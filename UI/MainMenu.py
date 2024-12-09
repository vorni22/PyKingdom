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
        self.button_play = Button(background=rect1, x_coord=self.width // 2, y_coord=self.height // 3, text_input="PLAY",
                             font=self.font_main, color="White", hover_color="Gray", size=75)
        self.button_quit = Button(background=rect2, x_coord=self.width // 2, y_coord=0.55*self.height, text_input="QUIT",
                             font=self.font_main, color="White", hover_color="Gray", size=75)
        self.button_map_size = DropDownButton(background=rect1, x_coord=self.width // 4, y_coord=self.height // 4,
                                         text_input="MAP", font=self.font_options, color="White",
                                         hover_color="Gray", size=75, options=options_map_size,
                                         options_background_color=(169, 169, 169))
        self.button_number_players = DropDownButton(background=rect2, x_coord=3 * self.width // 4, y_coord=self.height // 4,
                                               text_input="PLAYERS", font=self.font_options, color="White",
                                               hover_color="Gray", size=75, options=options_num_players,
                                               options_background_color=(169, 169, 169))
        self.button_start_game = Button(background=rect1, x_coord=self.width // 2, y_coord=self.height // 2,
                                   text_input="START GAME", font=self.font_options, color="White", hover_color="Gray", size=75)

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


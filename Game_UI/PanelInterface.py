import time
import pygame as pg

from .BasicPanel import BasicPanel
from .CityPanel import CityPanel
from .UnitPanel import UnitPanel
from .PermanentPanel import PermanentPanel
from UI.CircleButton import CircleButton


class PanelInterface:
    def __init__(self, width, height):
        city_panel_back = pg.image.load("Assets/MainMenu/ct3.png")
        basic_panel_back = pg.image.load("Assets/MainMenu/tile_panel.png")
        unit_panel_back = pg.image.load("Assets/MainMenu/unit_panel2.png")
        next_turn_back = pg.image.load("Assets/MainMenu/next_turn_button.png")
        self.width = width
        self.height = height
        self.clicked = False
        self.clicked_options = [False, False, False]
        self.sw = True
        self.update_every_frame = False
        self.tile_panel = BasicPanel(self.width, self.height, None, 60, "Black", "",
                                 0, self.height - basic_panel_back.get_rect().height, "Red", basic_panel_back)
        self.unit_panel = UnitPanel(self.width, self.height, None, 60, "Black", "",
                                 0, 50, "Red", unit_panel_back)
        self.city_panel = CityPanel(self.width, self.height, None, 60, "Black", "",
                                    self.width - city_panel_back.get_rect().width, 50, "Red", city_panel_back)
        self.status_panel = PermanentPanel()
        self.end_turn_button = CircleButton(next_turn_back, 75, (self.width - next_turn_back.get_rect().width, self.height - next_turn_back.get_rect().height))

        self.unit_is_moving = False
        self.clicks_unit_is_moving = 0
        self.temp = False

    def draw_interface(self, screen, position, objects, tile, unit, purchasable):
        if not self.unit_panel.is_unit_moved or self.clicks_unit_is_moving != 2:
            if self.sw:
                for obj in objects:
                    self.clicked_options[obj] = True

                if len(objects) == 2:
                    if objects[1] == 2:
                        self.clicked_options[0] = False

                if len(objects) == 3:
                    self.clicked_options[0] = False

                if not purchasable[0]:
                    self.clicked_options[2] = False
                    self.clicked_options[1] = False
                self.sw = False

            if self.clicked_options[0]:
                self.tile_panel.draw_surf(screen, position, tile, unit, purchasable)

            if self.clicked_options[1]:
                self.unit_panel.draw_surf(screen, position, tile, unit, purchasable)

            if self.clicked_options[2]:
                self.city_panel.draw_surf(screen, position, tile, unit, purchasable)

            self.clicked = True

        # if self.city_panel.error_message_time and time.time() - self.city_panel.error_message_time < 1:
        #     self.city_panel.draw_error_box(screen, self.city_panel.error_message_time)

    def close_interface(self, position, screen, unit, settle_func):
        if not self.cursor_is_on_ui(position):
            self.clicked_options = [False for _ in self.clicked_options]

            self.clicked = False
            self.sw = True
            self.city_panel.clicked = False
            self.tile_panel.clicked = False
            self.unit_panel.clicked = False
            return

        if self.clicked_options[0]:
            self.tile_panel.close_surf(position, screen)
            self.clicked_options[0] = self.tile_panel.clicked

        if self.clicked_options[1]:
            self.unit_panel.close_surf(position, screen)
            if self.unit_panel.move_unit(position, screen):
                self.unit_is_moving = True
            self.unit_panel.settle_city(position, screen, unit, settle_func)
            self.clicked_options[1] = self.unit_panel.clicked

        if self.clicked_options[2]:
            self.city_panel.close_surf(position, screen)
            self.city_panel.return_to_init_surf(position, screen)
            self.city_panel.switch_to_buy_units_districts(position)
            self.clicked_options[2] = self.city_panel.clicked

        all_panels_closed = False
        for option in self.clicked_options:
            all_panels_closed = all_panels_closed or option

        if not all_panels_closed or self.unit_is_moving:
            self.clicked = False
            self.sw = True

    def update_interface(self):
        if not self.clicked:
            self.clicked = True
            self.update_every_frame = True
            if self.unit_is_moving:
                self.clicks_unit_is_moving += 1
            return 1

        return 0

    def set_clicked(self, clicked):
        self.clicked = clicked

    def click_is_out_of_map(self, tile, mouse_x, mouse_y):
        if not 0 <= tile < mouse_x * mouse_y and self.update_every_frame:
            self.set_clicked(False)

    def set_update_every_frame(self, update_every_frame):
        self.update_every_frame = update_every_frame

    def cursor_is_on_ui(self, position):
        if self.clicked_options[0]:
            temp = self.tile_panel.surf.get_rect()
            temp.center = self.tile_panel.text_rect.center
            if temp.collidepoint(position):
                return True
            if self.tile_panel.close_rect.collidepoint(position):
                return True

        if self.clicked_options[1]:
            temp = self.unit_panel.surf.get_rect()
            temp.center = self.unit_panel.text_rect.center
            if temp.collidepoint(position):
                return True
            if self.unit_panel.close_rect.collidepoint(position):
                return True
            if self.unit_panel.move_unit_rect.collidepoint(position):
                return True
            if self.unit_panel.settler_rect.collidepoint(position):
                return True

        if self.clicked_options[2]:
            temp = self.city_panel.surf.get_rect()
            temp.center = self.city_panel.text_rect.center
            if temp.collidepoint(position):
                return True
            if self.city_panel.close_rect.collidepoint(position):
                return True

        status_rect = pg.rect.Rect(0, 0, self.width, 50)
        if status_rect.collidepoint(position):
            return True

        if self.end_turn_button.rendered:
            temp = self.end_turn_button.surf.get_rect()
            temp.topleft = self.end_turn_button.center
            if temp.collidepoint(position):
                return True

        return False

    def end_turn(self, position, player_end_turn):
        if self.end_turn_button.rendered:
            if self.end_turn_button.circle_collidepoint(position):
                print("end turn")
                player_end_turn()

    def move_units(self, unit, position, screen, tile_line, tile_column, move_func):
        if self.unit_panel.move_unit(position, screen) or self.unit_is_moving:
            self.city_panel.clicked = False
            self.tile_panel.clicked = False
            if not self.unit_is_moving:
                self.unit_is_moving = True
            if self.clicks_unit_is_moving == 1:
                move_func(unit[1], unit[2], tile_line, tile_column)
                self.unit_is_moving = False
                self.clicks_unit_is_moving = 0




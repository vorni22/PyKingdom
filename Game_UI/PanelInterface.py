
import pygame as pg

from .BasicPanel import BasicPanel
from .CityPanel import CityPanel
from .UnitPanel import UnitPanel


class PanelInterface:
    def __init__(self, width, height):
        city_panel_back = pg.image.load("Assets/MainMenu/ct3.png")
        basic_panel_back = pg.image.load("Assets/MainMenu/basic_panel.png")
        unit_panel_back = pg.image.load("Assets/MainMenu/unit_panel.png")

        self.clicked = False
        self.clicked_options = [False, False, False]
        self.sw = True

        self.tile_panel = BasicPanel(width, height, None, 60, "Black", "LOH",
                                 0, height - basic_panel_back.get_rect().height, "Red", basic_panel_back)
        self.unit_panel = UnitPanel(width, height, None, 60, "Black", "LOH",
                                 0, 0, "Red", unit_panel_back)
        self.city_panel = CityPanel(width, height, None, 60, "Black", "LOH",
                                 width - city_panel_back.get_rect().width, 0, "Red", city_panel_back)

        self.unit_is_moving = False
        self.clicks_unit_is_moving = 0

    def draw_interface(self, screen, position, objects):
        if not self.unit_panel.is_unit_moved or self.clicks_unit_is_moving != 2:
            if self.sw:
                for obj in objects:
                    self.clicked_options[obj] = True

                if len(objects) == 2:
                    if objects[1] == 2:
                        self.clicked_options[0] = False

                if len(objects) == 3:
                    self.clicked_options[0] = False

                self.sw = False

            if self.clicked_options[0]:
                self.tile_panel.draw_surf(screen, position)

            if self.clicked_options[1]:
                self.unit_panel.draw_surf(screen, position)

            if self.clicked_options[2]:
                self.city_panel.draw_surf(screen, position)

            self.clicked = True

    def close_interface(self, position ,screen):
        if self.clicked_options[0]:
            self.tile_panel.close_surf(position, screen)
            self.clicked_options[0] = self.tile_panel.clicked

        if self.clicked_options[1]:
            self.unit_panel.close_surf(position, screen)
            if self.unit_panel.move_unit(position, screen):
                self.unit_is_moving = True
            self.clicked_options[1] = self.unit_panel.clicked

        if self.clicked_options[2]:
            self.city_panel.close_surf(position, screen)
            self.city_panel.return_to_init_surf(position, screen)
            self.city_panel.switch_to_buy_units_buildings(position)
            self.clicked_options[2] = self.city_panel.clicked

        all_panels_closed = False
        for option in self.clicked_options:
            all_panels_closed = all_panels_closed or option

        if not all_panels_closed or self.unit_is_moving:
            self.clicked = False
            self.sw = True







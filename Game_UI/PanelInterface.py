
import pygame as pg
from openpyxl.packaging.manifest import Override

from .BasicPanel import BasicPanel
from .CityPanel import CityPanel

class PanelInterface:
    def __init__(self, width, height):
        city_panel_back = pg.image.load("Assets/MainMenu/ct2.png")
        basic_panel_back = pg.image.load("Assets/MainMenu/basic_panel.png")
        self.tile_panel = BasicPanel(width, height, None, 60, "Black", "LOH",
                                 0, 3 * height // 4 - 100, "Red", basic_panel_back)
        self.unit_panel = BasicPanel(width, height, None, 60, "Black", "LOH",
                                 0, 0, "Red", basic_panel_back)
        self.city_panel = CityPanel(width, height, None, 60, "Black", "LOH",
                                 width - city_panel_back.get_rect().width, 0, "Red", city_panel_back)



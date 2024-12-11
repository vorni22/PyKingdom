
import pygame as pg
from .GameUI import GameUI

class PanelInterface:
    def __init__(self, width, height):
        self.tile_panel = GameUI(width, height, None, 60, "Black", "LOH",
                                 3 * width // 4 - 100, 3 * height // 4 - 100, "Red")
        self.unit_panel = GameUI(width, height, None, 60, "Black", "LOH",
                                 0, 0, "Red")
        self.city_panel = GameUI(width, height, None, 60, "Black", "LOH",
                                 0, 3 * height // 4 - 100, "Red")

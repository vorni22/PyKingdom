import pygame as pg

from .BasicPanel import BasicPanel

class UnitPanel(BasicPanel):
    def __init__(self, width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf):
        super().__init__(width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf)
        self.move_unit_rect = pg.Rect(7 + self.center_x, 7 + self.center_y, 41, 41)
        self.is_unit_moved = False
        self.unit_coords = (30, 30)

    def move_unit(self, position, screen):
        if self.move_unit_rect.collidepoint(position):
            pg.draw.rect(screen, "Blue", self.move_unit_rect)
            self.clicked = False
            return True

        return False


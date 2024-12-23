import pygame as pg

from .BasicPanel import BasicPanel
from Logic.Unit import unit_classes

class UnitPanel(BasicPanel):
    def __init__(self, width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf):
        super().__init__(width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf)
        self.move_unit_rect = pg.Rect(7 + self.center_x, 7 + self.center_y, 41, 41)
        self.is_unit_moved = False
        self.settler_surf = pg.image.load("Assets/MainMenu/settler_panel.png")
        self.settler_rect = pg.Rect(7 + self.center_x, 48 + self.center_y, 41, 41)
        self.is_settler = False

    def move_unit(self, position, screen):
        if self.move_unit_rect.collidepoint(position):
            pg.draw.rect(screen, "Blue", self.move_unit_rect)
            self.clicked = False
            return True

        return False

    def draw_surf(self, screen, mouse_pos, tile, unit, purchasable):
        if unit[3] is None:
            return
        if 3 in unit[0]:
            self.is_settler = True
            screen.blit(self.settler_surf, (self.center_x, self.center_y))
        else:
            screen.blit(self.surf, (self.center_x, self.center_y))
        self.draw_title_text(f"Unit class: {unit[3][4]}", 45)
        screen.blit(self.text_rendered, self.text_rect)


    def settle_city(self, position, screen, unit, settle_func):
        if self.settler_rect.collidepoint(position) and 3 in unit[0]:
            pg.draw.rect(screen, "Blue", self.settler_rect)
            settle_func(unit[1], unit[2])
            self.clicked = False

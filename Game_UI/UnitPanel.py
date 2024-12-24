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

    def draw_surf(self, screen, mouse_pos, tile, unit, purchasable, city):
        if unit[3] is None:
            return
        if 3 in unit[0]:
            self.is_settler = True
            screen.blit(self.settler_surf, (self.center_x, self.center_y))
        else:
            screen.blit(self.surf, (self.center_x, self.center_y))
        self.draw_title_text(f"Unit class: {unit[3][4]}", 45, (self.center_x, self.center_y + 10))
        screen.blit(self.text_rendered, self.text_rect)

        self.render_text(unit[3][0], (200, 119), screen)

        i = 1
        unit_information = [("Melee Strength", unit[3][1]), ("Ranged Strength", unit[3][2]), ("Movement", unit[3][3])]
        for information in unit_information:
            self.draw_data_text(f"{information[0]}: {information[1]}", 30, i, 50)
            screen.blit(self.text_rendered, self.text_rect)
            i += 1

    def settle_city(self, position, screen, unit, settle_func):
        if self.settler_rect.collidepoint(position) and 3 in unit[0]:
            pg.draw.rect(screen, "Blue", self.settler_rect)
            settle_func(unit[1], unit[2])
            self.clicked = False

    def render_text(self, text_type, center, screen):
        text = str(text_type)
        fnt = pg.font.Font(self.font, 45)
        rendered_text = fnt.render(text, True, "Black")
        rect = rendered_text.get_rect(center=(center[0], center[1]))
        screen.blit(rendered_text, rect)
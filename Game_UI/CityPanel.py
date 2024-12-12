
import pygame as pg

from UI.Button import Button
from .BasicPanel import BasicPanel

class CityPanel(BasicPanel):
    def __init__(self, width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf):
        super().__init__(width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf)

        self.close_rect = pg.Rect(437 + 3 * width // 4 - 100, 7 + 3 * height // 4 - 100, 40, 42)

        rect = self.surf.get_rect()
        w = rect.width // 2 + self.center_x
        h = rect.height // 2 + self.center_y

        self.buy_melee = Button(None, w, h - 180, "Melee", None, "Black", "Gray", 30)
        self.buy_ranged = Button(None, w, h - 150, "Ranged", None, "Black", "Gray", 30)
        self.buy_cavalry = Button(None, w, h - 120, "Cavalry", None, "Black", "Gray", 30)
        self.buy_siege = Button(None, w, h - 90, "Siege", None, "Black", "Gray", 30)
        self.buy_naval_melee = Button(None, w, h - 60, "Naval Melee", None, "Black", "Gray", 30)
        self.buy_naval_ranged = Button(None, w, h - 30, "Navel Ranged", None, "Black", "Gray", 30)
        self.buy_civilian = Button(None, w, h, "Civilian", None, "Black", "Gray", 30)

    def draw_surf(self, screen, mouse_pos):
        screen.blit(self.surf, (self.center_x, self.center_y))
        # screen.blit(self.text_rendered, self.text_rect)
        self.buy_siege.update(screen, mouse_pos)
        self.buy_naval_melee.update(screen, mouse_pos)
        self.buy_naval_ranged.update(screen, mouse_pos)
        self.buy_melee.update(screen, mouse_pos)
        self.buy_ranged.update(screen, mouse_pos)
        self.buy_cavalry.update(screen, mouse_pos)
        self.buy_civilian.update(screen, mouse_pos)
        self.clicked = True

    def close_surf(self, position, screen):
        close = self.buy_melee.check_for_input(position) and self.buy_ranged.check_for_input(position) and self.buy_naval_melee.check_for_input(position)
        close = close and self.buy_naval_ranged.check_for_input(position) and self.buy_civilian.check_for_input(position)
        close = close and self.buy_cavalry.check_for_input(position) and self.buy_civilian.check_for_input(position)
        if self.close_rect.collidepoint(position) and not close:
            pg.draw.rect(screen, "Red", self.close_rect)
            self.clicked = False

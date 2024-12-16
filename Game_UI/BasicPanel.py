import pygame as pg

from Logic.Tile import tile_types

class BasicPanel:
    def __init__(self, width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf):
        self.width = width
        self.height = height
        self.surf = surf
        self.font = font
        self.text_size = text_size
        self.text = text
        self.text_color = text_color
        self.center_x = center_x
        self.center_y = center_y
        self.hover_color = hover_color
        self.clicked = False

        self.fnt = pg.font.Font(font, self.text_size)
        self.text_rendered = self.fnt.render(self.text, True, self.text_color)

        self.rect_width = self.width - self.center_x
        self.rect_height = self.height - self.center_y

        surf_rect = self.surf.get_rect()
        surf_rect.topleft = (self.center_x, self.center_y)
        self.text_rect = self.text_rendered.get_rect()
        self.text_rect.center = surf_rect.center

        self.close_rect = pg.Rect(437 + self.center_x, 7 + self.center_y, 40, 42)

    def draw_surf(self, screen, mouse_pos, tile):
        screen.blit(self.surf, (self.center_x, self.center_y))
        self.change_text("Tile type: " + str(tile_types[tile[0]]))
        screen.blit(self.text_rendered, self.text_rect)
        self.clicked = True

    def change_text(self, new_text):
        self.text = new_text
        self.text_rendered = self.fnt.render(self.text, True, self.text_color)

        surf_rect = self.surf.get_rect()
        surf_rect.topleft = (self.center_x, self.center_y)
        self.text_rect = self.text_rendered.get_rect()
        self.text_rect.center = surf_rect.center

    def close_surf(self, position, screen):
        if self.close_rect.collidepoint(position):
            pg.draw.rect(screen, "Red", self.close_rect)
            self.clicked = False
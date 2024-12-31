import pygame as pg

from Logic.Tile import tile_types
from Logic.Tile import tile_basic_resources
from Logic.Tile import tile_features
from Logic.Tile import tile_strategic_resources
from Logic.Tile import tile_luxury_resources

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

    def draw_surf(self, screen, mouse_pos, tile, unit, purchasable, city):
        screen.blit(self.surf, (self.center_x, self.center_y))
        self.draw_title_text(f"Tile type: {tile_types[tile[0]]}", 45, (self.center_x, self.center_y + 10))
        screen.blit(self.text_rendered, self.text_rect)

        i = 1
        tile_information = [
            ("Basic Resource", tile_basic_resources[tile[1]]), ("Strategic Resource", tile_strategic_resources[tile[2]]),
            ("Luxury Resource", tile_luxury_resources[tile[3]]), ("Tile Features", tile_features[tile[4]])
        ]

        for information in tile_information:
            if information[1] is not None:
                self.draw_data_text(f"{information[0]}: {information[1]}", 30, i, 0)
                screen.blit(self.text_rendered, self.text_rect)
                i += 1

        if i == 1:
            self.draw_data_text("There is nothing on this tile", 30, i, 0)
            screen.blit(self.text_rendered, self.text_rect)

        resources = {
            "food": (tile[5], (125 + self.center_x, 238 + self.center_y)),
            "production": (tile[6], (125 + self.center_x, 183 + self.center_y)),
            "science": (tile[7], (223 + self.center_x, 238 + self.center_y)),
            "gold": (tile[9], (223 + self.center_x, 183 + self.center_y)),
            "culture": (tile[8], (330 + self.center_x, 238 + self.center_y)),
        }

        f = pg.font.Font(None, 30)

        for resource, (value, position) in resources.items():
            yields = f.render(str(value), True, self.text_color)
            rect = yields.get_rect(center=position)
            screen.blit(yields, rect)

        self.clicked = True

    def draw_title_text(self, new_text, font_size, center):
        self.text = new_text
        f = pg.font.Font(self.font, font_size)
        self.text_rendered = f.render(self.text, True, "Black")

        self.text_rect = self.text_rendered.get_rect()
        self.text_rect.topleft = center
        self.text_rect.centerx = self.surf.get_rect().centerx

    def draw_data_text(self, new_text, font_size, idx, delta):
        self.text = new_text
        f = pg.font.Font(self.font, font_size)
        self.text_rendered = f.render(self.text, True, self.text_color)

        self.text_rect = self.text_rendered.get_rect()
        self.text_rect.topleft = (self.center_x + 10, self.center_y + 10 + 40 * idx + delta)

    def close_surf(self, position, screen):
        if self.close_rect.collidepoint(position):
            pg.draw.rect(screen, "Red", self.close_rect)
            self.clicked = False
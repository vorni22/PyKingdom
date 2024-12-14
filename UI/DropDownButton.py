import pygame as pg

from .Button import Button

class DropDownButton(Button):
    def __init__(self, background, x_coord,  y_coord, text_input, font, color, hover_color, size, options, options_background_color):
        super().__init__(background, x_coord, y_coord, text_input, font, color, hover_color, size)
        self.options = options
        self.dropdown_open = False
        self.selected_option = None
        self.options_rects = []
        self.options_font = pg.font.Font(self.font, 3 * self.size // 4)
        self.options_color = (0, 0, 0)
        self.hovered_option_index = None
        self.options_background_color = options_background_color

    def draw_dropdown(self, screen, position):

        screen.blit(self.text, self.text_rect)

        if self.dropdown_open:
            for i, option in enumerate(self.options):
                option_rect = pg.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                self.options_rects.append(option_rect)
                hover = option_rect.collidepoint(position)
                if hover:
                    color = self.hover_color
                else:
                    color = self.options_background_color
                pg.draw.rect(screen, color, option_rect)
                option_text = self.options_font.render(option, True, self.options_color)
                text_rect = option_text.get_rect(center=option_rect.center)
                screen.blit(option_text, text_rect)

    def check_input(self, position):
        if self.check_for_input(position):
            self.dropdown_open = not self.dropdown_open
        else:
            for i, option_rect in enumerate(self.options_rects):
                if option_rect.collidepoint(position) and self.dropdown_open:
                    self.selected_option = self.options[i]
                    self.text_input = self.options[i]
                    self.text = self.fnt.render(self.text_input, True, self.color)
                    self.text_rect = self.text.get_rect(center=self.rect.center)
                    self.dropdown_open = False
                    break

    def get_text_input(self):
        return self.text_input
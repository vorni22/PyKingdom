import pygame as pg

from .Button import Button

# @author Alexandru Condorache
# Represents a dropdown button that has an interactive behaviour, allows users to select from a list of options
# @param options (list): List of string options available in the dropdown menu.
# @param dropdown_open (bool): Indicates whether the dropdown menu is currently open.
# @param selected_option (str): The currently selected option from the dropdown menu.
# @param options_rects (list): List of rectangles representing the clickable areas for each dropdown option.
# @param options_font (pg.font.Font): Font object for rendering dropdown option text.
# @param options_color (tuple): Color of the dropdown option text.
# @param hovered_option_index (int): Index of the currently hovered dropdown option, or None if none are hovered.
# @param options_background_color (tuple): Background color of the dropdown options when not hovered.

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

# This function draw the button
# Options are displayed when the user clicked on button
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

# Checks if the user clicked on the button
# If the button is clicked the user chose the option and the option is saved
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
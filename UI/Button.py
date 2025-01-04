import pygame as pg


# @author Alexandru Condorache
# Represents a button that has an interactive behaviour
# @param image (pg.Surface): Background image for the button.
# @param x_coord (int): X-coordinate of the button's center.
# @param y_coord (int): Y-coordinate of the button's center.
# @param text_input (str): Text displayed on the button.
# @param font (str): Path to the font used for the button text.
# @param color (tuple): Default color of the button text.
# @param hover_color (tuple): Color of the button text when hovered.
# @param curr_color (tuple): Current color of the button text (changes on hover).
# @param size (int): Font size of the button text.
# @param fnt (pg.font.Font): Font object created with the specified font and size.
# @param text (pg.Surface): Rendered surface of the button text.
# @param rect (pg.Rect): Rectangle for the button's area (based on the image or text).
# @param text_rect (pg.Rect): Rectangle for the positioning of the button text.

class Button:
    def __init__(self, background, x_coord,  y_coord, text_input, font, color, hover_color, size):
        self.background = background
        self.x_coord, self.y_coord = x_coord, y_coord
        self.text_input = text_input
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.curr_color = color
        self.size = size
        self.fnt = pg.font.Font(self.font, self.size)
        self.text = self.fnt.render(self.text_input, True, self.color)

        if self.background:
            self.rect = self.background.get_rect(center=(self.x_coord, self.y_coord))
        else:
            self.rect = self.text.get_rect(center=(self.x_coord, self.y_coord))

        self.text_rect = self.text.get_rect(center=(self.x_coord, self.y_coord))

    def draw_button(self, screen):
        if self.background:
            screen.blit(self.background, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_for_input(self, position):
        return self.rect.collidepoint(position)

    def change_color(self, position):
        if self.check_for_input(position):
            self.curr_color = self.hover_color
        else:
            self.curr_color = self.color

        self.text = self.fnt.render(self.text_input, True, self.curr_color)

    def update(self, screen, mouse_pos):
        self.change_color(mouse_pos)
        self.draw_button(screen)

    def get_font(self, size):
        return pg.font.Font(self.font, size)

    def set_colors(self, color, hover):
        self.color = color
        self.curr_color = color
        self.hover_color = hover
        self.text = self.fnt.render(self.text_input, True, self.curr_color)

    def update_position(self):
        if self.background:
            self.rect = self.background.get_rect(center=(self.x_coord, self.y_coord))
        else:
            self.rect = self.text.get_rect(center=(self.x_coord, self.y_coord))
        self.text_rect = self.text.get_rect(center=(self.x_coord, self.y_coord))

    def set_coords(self, x_coord, y_coord):
        self.x_coord, self.y_coord = x_coord, y_coord

    def set_text(self, new_text):
        self.text_input = new_text
        self.text = self.fnt.render(self.text_input, True, self.color)
        self.text_rect = self.text.get_rect(center=(self.x_coord, self.y_coord))
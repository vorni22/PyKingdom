import pygame as pg

class Button:
    def __init__(self, background, x_coord,  y_coord, text_input, font, color, hover_color, size):
        self.image = background
        self.x_coord, self.y_coord = x_coord, y_coord
        self.text_input = text_input
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.curr_color = color
        self.size = size
        self.fnt = pg.font.Font(self.font, self.size)
        self.text = self.fnt.render(self.text_input, True, self.color)

        if self.image:
            self.rect = self.image.get_rect(center=(self.x_coord, self.y_coord))
        else:
            self.rect = self.text.get_rect(center=(self.x_coord, self.y_coord))

        self.text_rect = self.text.get_rect(center=(self.x_coord, self.y_coord))

    def draw_button(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
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
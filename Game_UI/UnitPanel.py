import pygame as pg

from .BasicPanel import BasicPanel

# @author Alexandru Condorache
# Unit panel to display information about a unit, inherits the BasicPanel class
# @param width (int): Width of the screen.
# @param height (int): Height of the screen.
# @param surf (pg.Surface): Surface object for rendering the panel.
# @param font (str): Path to the font used for text rendering.
# @param text_size (int): Font size for the panel text.
# @param text (str): Initial text to display on the panel.
# @param text_color (str): Color of the text in the panel.
# @param x_coord (int): X-coordinate of the panel's top-left corner.
# @param y_coord (int): Y-coordinate of the panel's top-left corner.
# @param hover_color (str): Color of the panel when hovered over.
# @param clicked (bool): Tracks whether the panel is clicked.
# @param fnt (pg.font.Font): Font object created from the specified font and size.
# @param text_rendered (pg.Surface): Rendered text surface for display.
# @param text_rect (pg.Rect): Rectangle for positioning the text.
# @param close_rect (pg.Rect): Rectangle for the close button on the panel.

class UnitPanel(BasicPanel):
    def __init__(self, width, height, font, text_size, text_color, text, x_coord, y_coord, hover_color, surf):
        super().__init__(width, height, font, text_size, text_color, text, x_coord, y_coord, hover_color, surf)
        self.move_unit_rect = pg.Rect(7 + self.x_coord, 7 + self.y_coord, 41, 41)
        self.is_unit_moved = False
        self.settler_surf = pg.image.load("Assets/UIAssets/settler_panel.png")
        self.settler_rect = pg.Rect(7 + self.x_coord, 48 + self.y_coord, 41, 41)
        self.is_settler = False

# Checks if the move button is clicked
    def move_unit(self, position, screen):
        if self.move_unit_rect.collidepoint(position):
            pg.draw.rect(screen, "Blue", self.move_unit_rect)
            self.clicked = False
            return True

        return False

# Draws the unit panel and display the information about unit based on unit param
    def draw_surf(self, screen, mouse_pos, tile, unit, purchasable, city):
        if unit[3] is None:
            return
        if 3 in unit[0]:
            self.is_settler = True
            screen.blit(self.settler_surf, (self.x_coord, self.y_coord))
        else:
            screen.blit(self.surf, (self.x_coord, self.y_coord))
        self.draw_title_text(f"Unit class: {unit[3][4]}", 45, (self.x_coord, self.y_coord + 10))
        screen.blit(self.text_rendered, self.text_rect)

        self.render_text(unit[3][0], (200, 119), screen)

        i = 1
        unit_information = [("Melee Strength", unit[3][1]), ("Ranged Strength", unit[3][2]), ("Movement", unit[3][3])]
        for information in unit_information:
            if information[1] >= 0:
                self.draw_data_text(f"{information[0]}: {information[1]}", 30, i, 50)
                screen.blit(self.text_rendered, self.text_rect)
                i += 1

# Checks if the settle button is clicked
    def settle_city(self, position, screen, unit, settle_func):
        if self.settler_rect.collidepoint(position) and 3 in unit[0]:
            pg.draw.rect(screen, "Blue", self.settler_rect)
            settle_func(unit[1], unit[2])
            self.clicked = False
            return True
        return False

    def render_text(self, text_type, center, screen):
        text = str(text_type)
        fnt = pg.font.Font(self.font, 45)
        rendered_text = fnt.render(text, True, "Black")
        rect = rendered_text.get_rect(center=(center[0], center[1]))
        screen.blit(rendered_text, rect)
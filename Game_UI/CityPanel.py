import pygame as pg

from UI.Button import Button
from .BasicPanel import BasicPanel
from Logic.Unit import unit_classes, naval_ranged_units_costs
from Logic.Unit import melee_units, ranged_units, cavalry_units
from Logic.Unit import siege_units, naval_melee_units, naval_ranged_units, civilian_units
from Logic.Unit import melee_units_costs, ranged_units_costs, cavalry_units_costs
from Logic.Unit import siege_units_costs, naval_melee_units_costs, civilian_units_costs
from Logic.Unit import civilian_units_costs
from Logic.City import district_types

class CityPanel(BasicPanel):
    def __init__(self, width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf):
        super().__init__(width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf)

        self.close_rect = pg.Rect(437 + 3 * width // 4 - 100, 7, 40, 42)
        self.return_rect = pg.Rect(392 + 3 * width // 4 - 100, 7, 40, 42)

        rect = self.surf.get_rect()
        w = rect.width // 2 + self.center_x
        h = rect.height // 2 + self.center_y
        self.buy_units = False
        self.buy_buildings = False
        self.buy_units_buttons = []
        self.buy_buildings_buttons = []
        self.bg = pg.image.load("Assets/MainMenu/cnt2.png")

        self.bg = pg.transform.scale(self.bg, (self.bg.get_rect().width + 50, self.bg.get_rect().height))

        self.units_cost = [melee_units_costs[0], ranged_units_costs[0], cavalry_units_costs[0], siege_units_costs[0], naval_melee_units_costs[0], naval_ranged_units_costs[0], civilian_units_costs]
        for i, unit_name in enumerate(unit_classes):
            self.buy_units_buttons.append(Button(self.bg, w, h - i * 50, self.format_text(unit_name, str(self.units_cost[i]), 350, 30), None, "White", "Gray", 30))

        for i, building_name in enumerate(district_types[:-1]):
            self.buy_buildings_buttons.append(Button(self.bg, w, h - i * 50, self.format_text(building_name, str(self.units_cost[i]), 350, 30), None, "White", "Gray", 30))

        self.buy_units_button = Button(None, w, 100, "Units", None, "White", "Gray", 60)
        self.buy_buildings_button = Button(None, w, 200, "Buildings", None, "White", "Gray", 60)

    def draw_surf(self, screen, mouse_pos):
        screen.blit(self.surf, (self.center_x, self.center_y))
        # screen.blit(self.text_rendered, self.text_rect)
        if not self.buy_buildings and not self.buy_units:
            self.buy_units_button.update(screen, mouse_pos)
            self.buy_buildings_button.update(screen, mouse_pos)

        if self.buy_units:
            for i, unit in enumerate(self.buy_units_buttons):
                unit.update(screen, mouse_pos)

        if self.buy_buildings:
            for building in self.buy_buildings_buttons:
                building.update(screen, mouse_pos)

        self.clicked = True

    def close_surf(self, position, screen):
        close = True
        if self.buy_units:
            for i in self.buy_units_buttons:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_units_button.check_for_input(position)

        if self.buy_buildings:
            for i in self.buy_buildings_buttons:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_buildings_button.check_for_input(position)

        if self.close_rect.collidepoint(position) and not close:
            pg.draw.rect(screen, "Red", self.close_rect)
            self.clicked = False
            self.buy_units = False
            self.buy_buildings = False

    def return_to_init_surf(self, position, screen):
        close = True
        if self.buy_units:
            for i in self.buy_units_buttons:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_units_button.check_for_input(position)

        if self.buy_buildings:
            for i in self.buy_buildings_buttons:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_buildings_button.check_for_input(position)

        if self.return_rect.collidepoint(position) and not close:
            pg.draw.rect(screen, "Blue", self.return_rect)
            self.buy_units = False
            self.buy_buildings = False

    def format_text(self, unit, cost, width, font_size):
        font = pg.font.Font(None, font_size)
        unit_width = font.size(unit)[0]
        cost_width = font.size(cost)[0]
        space_width = width - unit_width - cost_width
        num_spaces = max(0, space_width // font.size(" ")[0] - 5)
        return unit + " " * num_spaces + cost

    def switch_to_buy_units_buildings(self, position):
        if self.buy_units_button.check_for_input(position):
            self.buy_units = True
        if self.buy_buildings_button.check_for_input(position):
            self.buy_buildings = True
import pygame as pg
import time

from UI.Button import Button
from .BasicPanel import BasicPanel
from Logic.Unit import unit_classes, naval_ranged_units_costs
from Logic.Unit import melee_units, ranged_units, cavalry_units
from Logic.Unit import siege_units, naval_melee_units, naval_ranged_units, civilian_units
from Logic.Unit import melee_units_costs, ranged_units_costs, cavalry_units_costs
from Logic.Unit import siege_units_costs, naval_melee_units_costs
from Logic.Unit import civilian_units_costs
from Logic.City import district_types

class CityPanel(BasicPanel):
    def __init__(self, width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf):
        super().__init__(width, height, font, text_size, text_color, text, center_x, center_y, hover_color, surf)

        self.close_rect = pg.Rect(437 + 3 * width // 4 - 100, 57, 40, 42)
        self.return_rect = pg.Rect(392 + 3 * width // 4 - 100, 57, 40, 42)

        rect = self.surf.get_rect()
        rect.center = self.text_rect.center
        w = rect.width // 2 + self.center_x
        h = rect.height // 2 + self.center_y

        self.buy_units = [False, False]
        self.buy_districts = [False, False]
        self.buy_units_buttons = [[], []]
        self.buy_districts_buttons = [[], []]

        bg = pg.image.load("Assets/MainMenu/cnt2.png")
        bg_buy_buttons = pg.image.load("Assets/MainMenu/buy_smth_bg.png")
        bg_buy = pg.transform.scale(bg_buy_buttons, (2 * bg.get_rect().width // 3 - 10, bg.get_rect().height + 20))
        self.error_message_time = 0
        self.error_message = "Not enough production to buy this"

        bg = pg.transform.scale(bg, (bg.get_rect().width + 50, bg.get_rect().height))

        self.units_cost_production = [melee_units_costs[0], ranged_units_costs[0], cavalry_units_costs[0], siege_units_costs[0], naval_melee_units_costs[0], naval_ranged_units_costs[0], civilian_units_costs]
        self.units_cost_gold = [cost * 2 for cost in self.units_cost_production]

        # self.update_units_buttons = [[], []]
        self.update_districts_buttons = [[], []]

        for i, unit_name in enumerate(unit_classes[::-1]):
            self.buy_units_buttons[0].append(Button(bg, w, h - i * 50, self.format_text(unit_name, str(self.units_cost_production[i]), 350, 30), None, "White", "Gray", 30))

        for i, district_name in enumerate(district_types[-2::-1]):
            self.buy_districts_buttons[0].append(Button(bg, w, h - i * 50, self.format_text(district_name, str(self.units_cost_production[i]), 350, 30), None, "White", "Gray", 30))

        for i, unit_name in enumerate(unit_classes[::-1]):
            self.buy_units_buttons[1].append(Button(bg, w, h - i * 50, self.format_text(unit_name, str(self.units_cost_gold[i]), 350, 30), None, "White", "Gray", 30))

        for i, district_name in enumerate(district_types[-2::-1]):
            self.buy_districts_buttons[1].append(Button(bg, w, h - i * 50, self.format_text(district_name, str(self.units_cost_gold[i]), 350, 30), None, "White", "Gray", 30))

        self.buy_units_button_production = Button(bg_buy, w - 100, 210, "Production", None, "White", "Gray", 40)
        self.buy_districts_button_production = Button(bg_buy, w - 100, 330, "Production", None, "White", "Gray", 40)
        self.buy_units_button_gold = Button(bg_buy, w + 100, 210, "Gold", None, "White", "Gray", 40)
        self.buy_districts_button_gold = Button(bg_buy, w + 100, 330, "Gold", None, "White", "Gray", 40)

    def render_text(self, text_type, center, screen):
        text = "Buy " + text_type + " with:"
        rendered_text = self.fnt.render(text, True, "Black")
        rect = rendered_text.get_rect(center=(center[0], center[1]))
        screen.blit(rendered_text, rect)

    def draw_purchase_units(self, idx, pidx, screen, position, purchasable):
        for i, unit in enumerate(self.buy_units_buttons[idx]):
            if len(purchasable[pidx][i]) == 0:
                unit.set_colors("#9c9c9c", "#9c9c9c")
            else:
                unit.set_colors("White", "Gray")

        for i, unit in enumerate(self.buy_units_buttons[idx]):
            if len(purchasable[pidx][i]) != 0:
                unit.update(screen, position)
            else:
                unit.draw_button(screen)

    def draw_purchase_districts(self, idx, pidx, screen, position, purchasable):
        for i, district in enumerate(self.buy_districts_buttons[idx]):
            if not i in purchasable[pidx]:
                district.set_colors("#9c9c9c", "#9c9c9c")
            else:
                district.set_colors("White", "Gray")

        for i, district in enumerate(self.buy_districts_buttons[idx]):
            if i in purchasable[pidx]:
                district.update(screen, position)
            else:
                district.draw_button(screen)

    def draw_surf(self, screen, position, tile, unit, purchasable):
        screen.blit(self.surf, (self.center_x, self.center_y))

        if not self.buy_districts[0] and not self.buy_units[0] and not self.buy_districts[1] and not self.buy_units[1]:
            rect = self.surf.get_rect()
            rect.center = self.text_rect.center
            w = rect.width // 2 + self.center_x
            h = rect.height // 2 + self.center_y
            self.render_text("units", (w, 150), screen)
            self.render_text("units", (w, 270), screen)
            self.buy_units_button_production.update(screen, position)
            self.buy_districts_button_production.update(screen, position)
            self.buy_units_button_gold.update(screen, position)
            self.buy_districts_button_gold.update(screen, position)
            self.clicked = True

        if self.buy_units[0]:
            self.draw_purchase_units(0, 1, screen, position, purchasable)
            self.clicked = True
            return

        if self.buy_units[1]:
            self.draw_purchase_units(1, 4, screen, position, purchasable)
            self.clicked = True
            return

        if self.buy_districts[0]:
            self.draw_purchase_districts(0, 2, screen, position, purchasable)
            self.clicked = True
            return

        if self.buy_districts[1]:
            self.draw_purchase_districts(1, 5, screen, position, purchasable)
            self.clicked = True
            return

    def check_if_in_special_rects(self, position):
        close = True
        if self.buy_units[0]:
            for i in self.buy_units_buttons[0]:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_units_button_production.check_for_input(position)

        if self.buy_units[1]:
            for i in self.buy_units_buttons[1]:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_units_button_production.check_for_input(position)

        if self.buy_districts[0]:
            for i in self.buy_districts_buttons[0]:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_districts_button_production.check_for_input(position)

        if self.buy_districts[1]:
            for i in self.buy_districts_buttons[1]:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_districts_button_production.check_for_input(position)

        return close

    def close_surf(self, position, screen):

        close = self.check_if_in_special_rects(position)

        if self.close_rect.collidepoint(position) and not close:
            pg.draw.rect(screen, "Red", self.close_rect)
            self.clicked = False
            for i in range(2):
                self.buy_units[i] = False
                self.buy_districts[i] = False

    def return_to_init_surf(self, position, screen):
        close = self.check_if_in_special_rects(position)

        if self.return_rect.collidepoint(position) and not close:
            pg.draw.rect(screen, "Blue", self.return_rect)
            for i in range(2):
                self.buy_units[i] = False
                self.buy_districts[i] = False

    @staticmethod
    def format_text(unit, cost, width, font_size):
        font = pg.font.Font(None, font_size)
        unit_width = font.size(unit)[0]
        cost_width = font.size(cost)[0]
        space_width = width - unit_width - cost_width
        num_spaces = max(0, space_width // font.size(" ")[0] - 5)
        return unit + " " * num_spaces + cost

    def switch_to_buy_units_districts(self, position):
        if self.buy_units_button_production.check_for_input(position) and not self.buy_districts[0]:
            self.buy_units[0] = True
        if self.buy_districts_button_production.check_for_input(position) and not self.buy_units[0]:
            self.buy_districts[0] = True
        if self.buy_units_button_gold.check_for_input(position) and not self.buy_districts[1]:
            self.buy_units[1] = True
        if self.buy_districts_button_gold.check_for_input(position) and not self.buy_units[1]:
            self.buy_districts[1] = True

    # def draw_error_box(self, screen, start_time, duration=1000):
    #
    #     current_time = time.time()
    #     if current_time - start_time < duration:
    #
    #         box_rect = pg.Rect(self.width // 4, self.height // 2 - 50, self.width // 2, 100)
    #
    #         text = self.fnt.render(self.error_message, True, "Red")
    #         text_rect = text.get_rect(center=box_rect.center)
    #         screen.blit(text, text_rect)
    #         return True
    #     return False

    # def try_to_buy_something(self, position, production):
    #     if self.buy_units:
    #         for i, unit in enumerate(self.buy_units_buttons):
    #             if unit.check_for_input(position):
    #                 if self.units_cost[i] > production:
    #                     self.error_message_time = time.time()
    #                 else:
    #                     print("Unit purchased!")
    #                     self.error_message_time = None
    #         return
    #
    #     if self.buy_districts:
    #         for i, district in enumerate(self.buy_districts_buttons):
    #             if district.check_for_input(position):
    #                 if self.units_cost[i] > production:
    #                     self.error_message_time = time.time()
    #                 else:
    #                     print("district purchased!")
    #                     self.error_message_time = None
    #         return


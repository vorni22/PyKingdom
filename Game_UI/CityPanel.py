import pygame as pg

from UI.Button import Button
from .BasicPanel import BasicPanel
from Logic.Unit import unit_classes, naval_ranged_units_costs
from Logic.Unit import melee_units_costs, ranged_units_costs, cavalry_units_costs
from Logic.Unit import siege_units_costs, naval_melee_units_costs
from Logic.Unit import civilian_units_costs
from Logic.City import district_types
from Logic.City import district_cost
from Logic.City import city_center_buildings
from Logic.City import campus_buildings_costs, theatre_square_buildings_costs, commercial_hub_buildings_costs
from Logic.City import  harbour_buildings_costs, industrial_zone_buildings_costs, neighborhood_buildings_costs, city_center_buildings_costs

# @author Alexandru Condorache
# City panel to display information about a city, inherits the BasicPanel class
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

class CityPanel(BasicPanel):
    def __init__(self, width, height, font, text_size, text_color, text, x_coord, y_coord, hover_color, surf):
        super().__init__(width, height, font, text_size, text_color, text, x_coord, y_coord, hover_color, surf)

        self.close_rect = pg.Rect(437 + 3 * width // 4 - 100, 57, 40, 42)
        self.return_rect = pg.Rect(392 + 3 * width // 4 - 100, 57, 40, 42)

        rect = self.surf.get_rect()
        rect.center = self.text_rect.center
        w = rect.width // 2 + self.x_coord
        h = rect.height // 2 + self.y_coord - 120

        self.buy_units = [False, False]
        self.buy_districts = [False, False]
        self.buy_buildings_city_center = [False, False]
        self.buy_buildings = [False, False]
        self.buy_units_buttons = [[], []]
        self.buy_districts_buttons = [[], []]
        self.buy_buildings_city_center_buttons = [[], []]
        self.buy_buildings = [[], []]
        self.update_districts_buttons = [[], []]
        self.heights = [[], []]
        self.upgradable = [[], []]

        bg = pg.image.load("Assets/UIAssets/cnt2.png")
        bg_buy_buttons = pg.image.load("Assets/UIAssets/buy_smth_bg.png")
        bg_buy = pg.transform.scale(bg_buy_buttons, (2 * bg.get_rect().width // 3 - 10, bg.get_rect().height + 20))

        self.change_coords = [True, True]
        bg = pg.transform.scale(bg, (bg.get_rect().width + 50, bg.get_rect().height - 10))

        self.units_cost_production = [melee_units_costs[0], ranged_units_costs[0], cavalry_units_costs[0], siege_units_costs[0], naval_melee_units_costs[0], naval_ranged_units_costs[0], civilian_units_costs]
        self.units_cost_gold = [cost * 2 for cost in self.units_cost_production]
        district_cost_gold = 2 * district_cost

        self.scale = 35

        for i, unit_name in enumerate(unit_classes):
            self.buy_units_buttons[0].append(Button(bg, w - 35, h - (i + 1) * self.scale, self.format_text(unit_name, str(self.units_cost_production[i]), 350, 30), None, "White", "Gray", 30))

        for i, district_name in enumerate(district_types[-2::-1]):
            self.buy_districts_buttons[0].append(Button(bg, w - 35, h - (i + 1) * self.scale, self.format_text(district_name, str(district_cost), 350, 30), None, "White", "Gray", 30))
            self.heights[0].append(h - (i + 1) * self.scale)

        for i, unit_name in enumerate(unit_classes):
            self.buy_units_buttons[1].append(Button(bg, w - 35, h - (i + 1) * self.scale , self.format_text(unit_name, str(self.units_cost_gold[i]), 350, 30), None, "White", "Gray", 30))

        for i, district_name in enumerate(district_types[-2::-1]):
            self.buy_districts_buttons[1].append(Button(bg, w - 35, h - (i + 1) * self.scale, self.format_text(district_name, str(district_cost_gold), 350, 30), None, "White", "Gray", 30))
            self.heights[1].append(h - (i + 1) * self.scale)

        j = 0
        for i, building_name in enumerate(city_center_buildings[1:]):
            self.buy_buildings_city_center_buttons[0].append(Button(bg, w - 35, h - (i + 4) * self.scale, self.format_text(building_name, str(city_center_buildings_costs[i + 1]), 350, 30), None, "White", "Gray", 30))

        temp = [cost * 2 for cost in city_center_buildings_costs]
        for i, building_name in enumerate(city_center_buildings[1:]):
            self.buy_buildings_city_center_buttons[1].append(Button(bg, w - 35, h - (i + 4) * self.scale, self.format_text(building_name, str(temp[i + 1]), 350, 30),None, "White", "Gray", 30))

        self.update_buttons = [[], []]
        for i in range(len(self.buy_districts_buttons[0])):
            self.update_buttons[0].append(Button(bg, w - 35, h - (i + 1) * self.scale, self.format_text("Update" + str(i), str(self.units_cost_production[0]), 350, 30), None, "White", "Gray", 30))

        for i in range(len(self.buy_districts_buttons[1])):
            self.update_buttons[1].append(Button(bg, w - 35, h - (i + 1) * self.scale, self.format_text("Update" + str(i), str(self.units_cost_production[0]), 350, 30), None, "White", "Gray", 30))

        self.buy_units_button_production = Button(bg_buy, w - 100, 210, "Production", None, "White", "Gray", 40)
        self.buy_districts_button_production = Button(bg_buy, w - 100, 330, "Production", None, "White", "Gray", 40)
        self.buy_units_button_gold = Button(bg_buy, w + 100, 210, "Gold", None, "White", "Gray", 40)
        self.buy_districts_button_gold = Button(bg_buy, w + 100, 330, "Gold", None, "White", "Gray", 40)
        self.buy_buildings_city_center_button_production = Button(bg_buy, w - 100, 450, "Production", None, "White", "Gray", 40)
        self.buy_buildings_city_center_button_gold = Button(bg_buy, w + 100, 450, "Gold", None, "White", "Gray", 40)
        self.buildings_costs = [[campus_buildings_costs, theatre_square_buildings_costs, commercial_hub_buildings_costs, harbour_buildings_costs, industrial_zone_buildings_costs, neighborhood_buildings_costs], []]
        self.buildings_costs[1] = [[value * 2 for value in sublist] for sublist in self.buildings_costs[0]]

    def render_text(self, text_type, center, screen):
        text = "Buy " + text_type + " with:"
        fnt = pg.font.Font(self.font, 45)
        rendered_text = fnt.render(text, True, "Black")
        rect = rendered_text.get_rect(center=(center[0], center[1]))
        screen.blit(rendered_text, rect)

# Checks if the player can buy a unit
# If he cannot buy it changes the color and hover color of button to #9c9c9c
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

# Checks if the player can buy a district
# If he cannot buy it changes the color and hover color of button to #9c9c9c
# Also if a district is upgradable the button for upgrade is displayed and
# The positions of other buttons are changed
    def draw_purchase_districts(self, idx, pidx, screen, position, purchasable):
        for i, district in enumerate(self.buy_districts_buttons[idx][::-1]):
            if not i in purchasable[pidx]:
                district.set_colors("#9c9c9c", "#9c9c9c")
            else:
                district.set_colors("White", "Gray")

        if self.change_coords[idx] and not self.check_array_is_empty(purchasable[pidx + 1]):
            for i in range(len(purchasable[pidx + 1]) - 1):
                if len(purchasable[pidx + 1][i]) != 0:
                    for j, d in enumerate(self.buy_districts_buttons[idx][::-1][i + 1:]):
                        d.set_coords(d.x_coord, d.y_coord + self.scale)
                        d.update_position()

            for i, update in enumerate(self.update_buttons[idx][::-1]):
                if len(purchasable[pidx + 1][i]) != 0:
                    update.set_coords(update.x_coord, self.buy_districts_buttons[idx][len(self.buy_districts_buttons[idx]) - i - 1].y_coord + self.scale)
                    update.update_position()
                    self.upgradable[idx].append(update)
                else:
                    update.set_coords(update.x_coord, 4000)
                    update.update_position()

            self.change_coords[idx] = False

        if not self.check_array_is_empty(purchasable[pidx + 1]):
            for i, building in enumerate(self.update_buttons[idx][::-1]):
                if len(purchasable[pidx + 1][i]) != 0:
                    j = purchasable[pidx + 1][i][-1]
                    building.set_text(self.format_text("Upgrade " + district_types[i], str(self.buildings_costs[idx][i][j]), 350, 30))
                    building.update(screen, position)

        for i, district in enumerate(self.buy_districts_buttons[idx][::-1]):
            if i in purchasable[pidx]:
                district.update(screen, position)
            else:
                district.draw_button(screen)

# Checks if the player can buy a city center building
# If he cannot buy it changes the color and hover color of button to #9c9c9c
    def draw_purchase_city_center_buildings(self, idx, pidx, screen, position, purchasable):
        for i, building in enumerate(self.buy_buildings_city_center_buttons[idx]):
            if not i + 1 in purchasable[pidx][-1]:
                building.set_colors("#9c9c9c", "#9c9c9c")
            else:
                building.set_colors("White", "Gray")

        for i, building in enumerate(self.buy_buildings_city_center_buttons[idx]):
            if i + 1 in purchasable[pidx][-1]:
                building.update(screen, position)
            else:
                building.draw_button(screen)

# Draws the city panel and display the information about the city
# If a player want to buy something it renders buttons for buying what players wants
    def draw_surf(self, screen, position, tile, unit, purchasable, city):
        screen.blit(self.surf, (self.x_coord, self.y_coord))

        if not self.buy_districts[0] and not self.buy_units[0] and not self.buy_districts[1] and not self.buy_units[1] and not self.buy_buildings_city_center[0] and not self.buy_buildings_city_center[1]:
            rect = self.surf.get_rect()
            rect.center = self.text_rect.center
            w = rect.width // 2 + self.x_coord
            self.render_text("units", (w, 150), screen)
            self.render_text("districts", (w, 270), screen)
            self.render_text("buildings", (w, 390), screen)
            self.buy_units_button_production.update(screen, position)
            self.buy_districts_button_production.update(screen, position)
            self.buy_units_button_gold.update(screen, position)
            self.buy_districts_button_gold.update(screen, position)
            self.buy_buildings_city_center_button_production.update(screen, position)
            self.buy_buildings_city_center_button_gold.update(screen, position)
            self.clicked = True

        if city is None:
            return

        self.draw_title_text(f"{city[11]}", 45, (self.width + self.x_coord, self.y_coord + 10))
        screen.blit(self.text_rendered, self.text_rect)
        resources_per_turn = ["+" + str(round(city[0])), "+" + str(round(city[1])), "+" + str(round(city[2])), "+" + str(round(city[4])), "+" + str(round(city[3]))]

        i = 0
        rects = []
        for j in range(5):
            rects.append(pg.Rect(1070 + j * 88, 610, 50, 25))

        for resource in resources_per_turn:
            self.resources_per_turn(f"{resource}", 25, rects[i], screen)
            i += 1

        city_information = [("Total Food", round(city[5])), ("Total Production", round(city[6])), ("Housing", city[7]), ("Population", city[8]), ("Health", city[9]), ("Combat Strength", city[10])]

        i = 0
        for information in city_information:
            self.draw_data_text(f"{information[0]}: {information[1]}", 30, i, screen)
            i += 1

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

        if self.buy_buildings_city_center[0]:
            self.draw_purchase_city_center_buildings(0, 3, screen, position, purchasable)
            self.clicked = True
            return

        if self.buy_buildings_city_center[1]:
            self.draw_purchase_city_center_buildings(1, 6, screen, position, purchasable)
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

        if self.buy_buildings_city_center[0]:
            for i in self.buy_buildings_city_center_buttons[0]:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_buildings_city_center_button_production.check_for_input(position)

        if self.buy_buildings_city_center[1]:
            for i in self.buy_buildings_city_center_buttons[1]:
                close = close and i.check_for_input(position)
        else:
            close = close and self.buy_buildings_city_center_button_gold.check_for_input(position)

        return close

# Closes the city panel and update the positions of buttons
    def close_surf(self, position, screen):

        close = self.check_if_in_special_rects(position)

        if self.close_rect.collidepoint(position) and not close:
            pg.draw.rect(screen, "Red", self.close_rect)
            self.clicked = False
            for i in range(2):
                self.buy_units[i] = False
                self.buy_districts[i] = False
                self.buy_buildings_city_center[i] = False

            for i, district in enumerate(self.buy_districts_buttons[0]):
                district.set_coords(district.x_coord, self.heights[0][i])
                district.update_position()

            for i, district in enumerate(self.buy_districts_buttons[1]):
                district.set_coords(district.x_coord, self.heights[1][i])
                district.update_position()

            self.change_coords = [True, True]

    def return_to_init_surf(self, position, screen):
        close = self.check_if_in_special_rects(position)

        if self.return_rect.collidepoint(position) and not close:
            pg.draw.rect(screen, "Blue", self.return_rect)
            for i in range(2):
                self.buy_units[i] = False
                self.buy_districts[i] = False
                self.buy_buildings_city_center[i] = False

    def switch_to_buy_units_districts(self, position):
        if self.check_if_rendered():
            return
        if self.buy_units_button_production.check_for_input(position):
            self.buy_units[0] = True
            return
        if self.buy_districts_button_production.check_for_input(position):
            self.buy_districts[0] = True
            return
        if self.buy_units_button_gold.check_for_input(position):
            self.buy_units[1] = True
            return
        if self.buy_districts_button_gold.check_for_input(position):
            self.buy_districts[1] = True
            return
        if self.buy_buildings_city_center_button_production.check_for_input(position):
            self.buy_buildings_city_center[0] = True
            return
        if self.buy_buildings_city_center_button_gold.check_for_input(position):
            self.buy_buildings_city_center[1] = True
            return

    def check_if_rendered(self):
        ret = False
        for i in range(2):
            ret = ret or self.buy_units[i] or self.buy_districts[i] or self.buy_buildings_city_center[i]

        return ret

    def draw_title_text(self, new_text, font_size, center):
        self.text = new_text
        f = pg.font.Font(self.font, font_size)
        self.text_rendered = f.render(self.text, True, "Black")

        temp = self.surf.get_rect()
        temp.center = self.text_rect.center
        self.text_rect = self.text_rendered.get_rect()
        self.text_rect.topleft = center
        self.text_rect.centerx = temp.centerx

    def resources_per_turn(self, new_text, font_size, rect, screen):
        f = pg.font.Font(self.font, font_size)
        text_rendered = f.render(new_text, True, self.text_color)

        text_rect = rect
        screen.blit(text_rendered, text_rect)

    def draw_data_text(self, new_text, font_size, idx, screen):
        text = new_text
        f = pg.font.Font(self.font, font_size)
        text_rendered = f.render(text, True, self.text_color)

        text_rect = text_rendered.get_rect()
        text_rect.topleft = (self.x_coord + 10, self.height - (self.y_coord - 10 + 35 * idx))
        screen.blit(text_rendered, text_rect)

    @staticmethod
    def check_array_is_empty(arr):
        for a in arr[:-1]:
            if len(a) != 0:
                return False
        return True

    @staticmethod
    def format_text(unit, cost, width, font_size):
        font = pg.font.Font(None, font_size)
        unit_width = font.size(unit)[0]
        cost_width = font.size(cost)[0]
        space_width = width - unit_width - cost_width
        num_spaces = max(0, space_width // font.size(" ")[0] - 5)
        return unit + " " * num_spaces + cost

import time

import pygame as pg

from .BasicPanel import BasicPanel
from .CityPanel import CityPanel
from .UnitPanel import UnitPanel
from .PermanentPanel import PermanentPanel
from UI.CircleButton import CircleButton
from Logic.City import district_cost, city_center_buildings_costs

class PanelInterface:
    def __init__(self, width, height):
        city_panel_back = pg.image.load("Assets/MainMenu/city_panel.png")
        basic_panel_back = pg.image.load("Assets/MainMenu/tile_panel.png")
        unit_panel_back = pg.image.load("Assets/MainMenu/unit_panel.png")
        next_turn_back = pg.image.load("Assets/MainMenu/next_turn_button.png")
        self.loading_screen = pg.image.load("Assets/MainMenu/Loading_screen.png")
        self.culture_victory = pg.image.load("Assets/MainMenu/Culture_victory_bg.png")
        self.science_victory = pg.image.load("Assets/MainMenu/Science_victory_bg.png")
        self.domination_victory = pg.image.load("Assets/MainMenu/Domination_victory_bg.png")
        self.width = width
        self.height = height
        self.clicked = False
        self.clicked_options = [False, False, False]
        self.sw = True
        self.update_every_frame = False
        self.tile_panel = BasicPanel(self.width, self.height, None, 60, "Black", "",
                                 0, self.height - basic_panel_back.get_rect().height, "Red", basic_panel_back)
        self.unit_panel = UnitPanel(self.width, self.height, None, 60, "Black", "",
                                 0, 50, "Red", unit_panel_back)
        self.city_panel = CityPanel(self.width, self.height, None, 60, "Black", "",
                                    self.width - city_panel_back.get_rect().width, 50, "Red", city_panel_back)
        self.status_panel = PermanentPanel()
        self.end_turn_button = CircleButton(next_turn_back, 75, (self.width - next_turn_back.get_rect().width, self.height - next_turn_back.get_rect().height))

        self.unit_is_moving = False
        self.clicks_unit_is_moving = 0
        self.clicks = [0, 0, 0, 0, 0, 0]
        self.district_is_purchased_p = False
        self.district_is_purchased_g = False
        self.clicks_district_is_purchased = 0
        self.load_screen = False
        self.start_time = None
        self.victory = 0

    def draw_interface(self, screen, position, objects, tile, unit, purchasable, city):
        self.purchasable = purchasable
        if self.victory == 1:
            screen.blit(self.domination_victory, (0, 0))
            return
        if self.victory == 3:
            screen.blit(self.culture_victory, (0, 0))
            return
        if self.victory == 2:
            screen.blit(self.science_victory, (0, 0))
            return
        if not self.unit_is_moving:
            if self.sw:
                for obj in objects:
                    self.clicked_options[obj] = True

                if len(objects) == 2:
                    if objects[1] == 2:
                        self.clicked_options[0] = False

                if len(objects) == 3:
                    self.clicked_options[0] = False

                if not purchasable[0]:
                    self.clicked_options[2] = False
                    self.clicked_options[1] = False
                self.sw = False

            if self.clicked_options[0]:
                self.tile_panel.draw_surf(screen, position, tile, unit, purchasable, city)

            if self.clicked_options[1]:
                self.unit_panel.draw_surf(screen, position, tile, unit, purchasable, city)

            if self.clicked_options[2]:
                self.city_panel.draw_surf(screen, position, tile, unit, purchasable, city)
                self.end_turn_button.rendered = False
            else:
                self.end_turn_button.rendered = True
            self.clicked = True

    def close_interface(self, position, screen, unit, settle_func):
        if self.victory:
            return
        if not self.cursor_is_on_ui(position):
            self.clicked_options = [False for _ in self.clicked_options]

            self.clicked = False
            self.sw = True
            self.city_panel.clicked = False
            self.tile_panel.clicked = False
            self.unit_panel.clicked = False
            self.end_turn_button.rendered = True
            return

        if self.clicked_options[0]:
            self.tile_panel.close_surf(position, screen)
            self.clicked_options[0] = self.tile_panel.clicked

        if self.clicked_options[1]:
            self.unit_panel.close_surf(position, screen)
            if self.unit_panel.move_unit(position, screen):
                self.unit_is_moving = True
            if self.unit_panel.settle_city(position, screen, unit, settle_func):
                self.reset_all()
            self.clicked_options[1] = self.unit_panel.clicked

        if self.clicked_options[2]:
            self.city_panel.close_surf(position, screen)
            self.city_panel.return_to_init_surf(position, screen)
            self.city_panel.switch_to_buy_units_districts(position)
            self.clicked_options[2] = self.city_panel.clicked

        all_panels_closed = False
        for option in self.clicked_options:
            all_panels_closed = all_panels_closed or option

        if not all_panels_closed or self.unit_is_moving:
            self.clicked = False
            self.sw = True
            self.end_turn_button.rendered = True

    def update_interface(self, move_func, unit, position, buy_func1, buy_func2):
        if not self.clicked:
            self.clicked = True
            self.update_every_frame = True
            if self.unit_is_moving:
                self.unit_is_moving = False
                move_func(unit[1], unit[2], position[0], position[1])
                self.clicks_unit_is_moving = 0
                self.reset_all()
            if self.district_is_purchased_p and self.bdistrict_p[0] != position[0] and self.bdistrict_p[1] != position[1]:
                self.district_is_purchased_p = False
                self.clicks_district_is_purchased = 0
                self.reset_all()
                buy_func1(self.bdistrict_p[0], self.bdistrict_p[1], position[0], position[1], self.bdistrict_p[4])
            if self.district_is_purchased_g and self.bdistrict_g[0] != position[0] and self.bdistrict_g[1] != position[1]:
                self.district_is_purchased_g = False
                self.clicks_district_is_purchased = 0
                self.reset_all()
                buy_func2(self.bdistrict_g[0], self.bdistrict_g[1], position[0], position[1], self.bdistrict_g[4])

    def set_clicked(self, clicked):
        self.clicked = clicked

    def click_is_out_of_map(self, tile, mouse_x, mouse_y):
        if not 0 <= tile < mouse_x * mouse_y and self.update_every_frame:
            self.set_clicked(False)

    def set_update_every_frame(self, update_every_frame):
        self.update_every_frame = update_every_frame

    def cursor_is_on_ui(self, position):
        if self.clicked_options[0]:
            temp = self.tile_panel.surf.get_rect()
            temp.topleft = (self.tile_panel.center_x, self.tile_panel.center_y)
            if temp.collidepoint(position):
                return True
            if self.tile_panel.close_rect.collidepoint(position):
                return True

        if self.clicked_options[1]:
            temp = self.unit_panel.surf.get_rect()
            temp.topleft = (self.unit_panel.center_x, self.unit_panel.center_y)
            if temp.collidepoint(position):
                return True
            if self.unit_panel.close_rect.collidepoint(position):
                return True
            if self.unit_panel.move_unit_rect.collidepoint(position):
                return True
            if self.unit_panel.settler_rect.collidepoint(position):
                return True

        if self.clicked_options[2]:
            temp = self.city_panel.surf.get_rect()
            temp.topleft = (self.city_panel.center_x, self.city_panel.center_y)
            if temp.collidepoint(position):
                return True
            if self.city_panel.close_rect.collidepoint(position):
                return True
            if self.city_panel.check_if_in_special_rects(position):
                return True
            if not self.city_panel.check_array_is_empty(self.purchasable[3]):
                for key in self.city_panel.update_buttons[0]:
                    if key.check_for_input(position):
                        return True
            if not self.city_panel.check_array_is_empty(self.purchasable[6]):
                for key in self.city_panel.update_buttons[1]:
                    if key.check_for_input(position):
                        return True

        status_rect = pg.rect.Rect(0, 0, self.width, 50)
        if status_rect.collidepoint(position):
            return True

        if self.end_turn_button.rendered:
            temp = self.end_turn_button.surf.get_rect()
            temp.topleft = self.end_turn_button.center
            if temp.collidepoint(position):
                return True

        return False

    def reset_all(self):
        self.clicks = [0, 0, 0, 0, 0, 0]
        self.clicked_options = [False for _ in self.clicked_options]

        self.clicked = False
        self.sw = True
        self.city_panel.clicked = False
        self.tile_panel.clicked = False
        self.unit_panel.clicked = False
        self.end_turn_button.rendered = True
        for i in range(2):
            self.city_panel.buy_units[i] = False
            self.city_panel.buy_districts[i] = False
            self.city_panel.buy_buildings_city_center[i] = False

    def end_turn(self, position, player_end_turn):
        if self.end_turn_button.rendered:
            temp = self.end_turn_button.surf.get_rect()
            temp.topleft = self.end_turn_button.center
            if temp.collidepoint(position):
                print("end turn")

                self.reset_all()
                self.victory = player_end_turn()
                self.load_screen = True
                self.start_time = pg.time.get_ticks()

                for i, district in enumerate(self.city_panel.buy_districts_buttons[0]):
                    district.set_coords(district.x_coord, self.city_panel.heights[0][i])
                    district.update_position()

                for i, district in enumerate(self.city_panel.buy_districts_buttons[1]):
                    district.set_coords(district.x_coord, self.city_panel.heights[1][i])
                    district.update_position()

                for i, building in enumerate(self.city_panel.update_buttons[0]):
                    building.set_coords(building.x_coord, self.city_panel.heights[0][i])

                for i, building in enumerate(self.city_panel.update_buttons[1]):
                    building.set_coords(building.x_coord, self.city_panel.heights[1][i])

                self.city_panel.change_coords = [True, True]

    def move_units(self, unit, position, screen, tile_line, tile_column, move_func, game):
        if not self.unit_is_moving:
            self.unit_is_moving = self.unit_panel.move_unit(position, screen)

        if self.unit_is_moving:
            game.highlight_move_tiles(tile_line, tile_column)

        if self.unit_is_moving and self.clicks_unit_is_moving == 2:
            move_func(unit[1], unit[2], tile_line, tile_column)
            self.unit_is_moving = False
            self.clicks_unit_is_moving = 0
            self.reset_all()

    def count_clicks(self):
        if self.city_panel.buy_units[0]:
            self.clicks[0] += 1
        elif self.city_panel.buy_units[1]:
            self.clicks[1] += 1
        elif self.city_panel.buy_districts[0]:
            self.clicks[2] += 1
        elif self.city_panel.buy_districts[1]:
            self.clicks[3] += 1
        elif self.city_panel.buy_buildings_city_center[0]:
            self.clicks[4] += 1
        elif self.city_panel.buy_buildings_city_center[1]:
            self.clicks[5] += 1

    def buy_units(self, tile_line, tile_column, position, game, city):
        if city is None:
            return
        temp = game.get_player_information()
        production = city[6]
        if self.city_panel.buy_units[0]:
            for i, key in enumerate(self.city_panel.buy_units_buttons[0]):
                if key.check_for_input(position) and self.clicks[0] >= 2:
                    if self.city_panel.units_cost_production[i] <= production and key.hover_color != "#9c9c9c":
                        ret = game.purchase_unit_with_production(tile_line, tile_column, i)
                        self.reset_all()
                        return

        if self.city_panel.buy_units[1]:
            for i, key in enumerate(self.city_panel.buy_units_buttons[1]):
                if key.check_for_input(position) and self.clicks[1] >= 2:
                    if self.city_panel.units_cost_gold[i] <= temp[3] and key.hover_color != "#9c9c9c":
                        ret = game.purchase_unit_with_gold(tile_line, tile_column, i)
                        self.reset_all()
                        return

    def buy_buildings(self, tile_line, tile_column, position, game, city):
        if city is None:
            return

        temp = game.get_player_information()
        production = city[6]
        if self.city_panel.buy_buildings_city_center[0]:
            for i, key in enumerate(self.city_panel.buy_buildings_city_center_buttons[0]):
                if key.check_for_input(position) and self.clicks[4] >= 2 and key.hover_color != "#9c9c9c":
                    if city_center_buildings_costs[i + 1] <= production:
                        ret = game.purchase_building_with_production(tile_line, tile_column, 7, i + 1)
                        print("building_bought")
                        self.reset_all()
                        return

        if self.city_panel.buy_buildings_city_center[1]:
            for i, key in enumerate(self.city_panel.buy_buildings_city_center_buttons[1]):
                if key.check_for_input(position) and self.clicks[5] >= 2 and key.hover_color != "#9c9c9c":
                    if 2 * city_center_buildings_costs[i + 1] <= temp[3]:
                        ret = game.purchase_building_with_production(tile_line, tile_column, 7, i + 1)
                        print("building_bought")
                        self.reset_all()
                        return

    def buy_districts(self, city_line, city_column, position, game, city, tile_line, tile_column):
        if city is None:
            return
        if self.district_is_purchased_p:
            game.highlight_purchase_tiles(self.bdistrict_p[0], self.bdistrict_p[1], self.bdistrict_p[4])
        if self.district_is_purchased_g:
            game.highlight_purchase_tiles(self.bdistrict_g[0], self.bdistrict_g[1], self.bdistrict_g[4])
        temp = game.get_player_information()
        production = city[6]
        if self.city_panel.buy_districts[0]:
            if self.district_is_purchased_p and (self.bdistrict_p[0] != tile_line or self.bdistrict_p[1] != tile_column):
                game.purchase_district_with_production(self.bdistrict_p[0], self.bdistrict_p[1], tile_line, tile_column, self.bdistrict_p[4])
                self.district_is_purchased_p = False
                return
            elif not self.district_is_purchased_p:
                for i, key in enumerate(self.city_panel.buy_districts_buttons[0][::-1]):
                    if key.check_for_input(position) and self.clicks[2] >= 2 and key.hover_color != "#9c9c9c":
                        if district_cost <= production:
                            self.district_is_purchased_p = True
                            self.bdistrict_p = (city_line, city_column, tile_line, tile_column, i)
                            game.highlight_purchase_tiles(self.bdistrict_p[0], self.bdistrict_p[1], self.bdistrict_p[4])
                            self.reset_all()
                            return

        if self.city_panel.buy_districts[1]:
            if self.district_is_purchased_g and (self.bdistrict_g[0] != tile_line or self.bdistrict_g[1] != tile_column):
                game.purchase_district_with_production(self.bdistrict_g[0], self.bdistrict_g[1], tile_line, tile_column, self.bdistrict_g[4])
                self.district_is_purchased_g = False
                return
            elif not self.district_is_purchased_g:
                for i, key in enumerate(self.city_panel.buy_districts_buttons[1][::-1]):
                    if key.check_for_input(position) and self.clicks[3] >= 2 and key.hover_color != "#9c9c9c":
                        if 2 * district_cost <= temp[3]:
                            if not self.district_is_purchased_g:
                                self.district_is_purchased_g = True
                                self.bdistrict_g = (city_line, city_column, tile_line, tile_column, i)
                                game.highlight_purchase_tiles(self.bdistrict_g[0], self.bdistrict_g[1],
                                                              self.bdistrict_g[4])
                                self.reset_all()
                            return


    def buy_district_buildings(self, tile_line, tile_column, position, game, city, purchasable):
        if city is None:
            return
        temp = game.get_player_information()
        production = city[6]
        if not self.city_panel.check_array_is_empty(purchasable[3]):
            for i, key in enumerate(self.city_panel.update_buttons[0][::-1]):
                if key.check_for_input(position) and self.clicks[2] >= 2 and len(purchasable[3][i]) != 0:
                    if self.city_panel.buildings_costs[0][i][purchasable[3][i][-1]]  <= production:
                        ret = game.purchase_building_with_production(tile_line, tile_column, i, purchasable[3][i][-1])
                        print("building_bought")
                        self.reset_all()
                        return

        if not self.city_panel.check_array_is_empty(purchasable[6]):
            for i, key in enumerate(self.city_panel.update_buttons[1][::-1]):
                if key.check_for_input(position) and self.clicks[3] >= 2 and len(purchasable[3][i]) != 0:
                    if self.city_panel.buildings_costs[1][i][purchasable[6][i][-1]] <= temp[3]:
                        ret = game.purchase_building_with_production(tile_line, tile_column, i, purchasable[6][i][-1])
                        print("building_bought")
                        self.reset_all()
                        return

    def draw_loading_screen(self, screen):
        if self.load_screen:
            if pg.time.get_ticks() - self.start_time > 1000:
                self.load_screen = False
                return
            screen.blit(self.loading_screen, (0, 0))
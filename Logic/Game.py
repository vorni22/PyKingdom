import random

import Logic.Player as Player
import Logic.City as City
# import Logic.Resources as Resources
import Logic.Unit as Unit
# import Logic.Tech as Tech
# import Logic.Civic as Civic
import Map_Generation.Map as Map

# class that will be used for integrating the UI and the graphics with the backend of the game
class Game:
    def __init__(self, player_count, map_size_lines, map_size_columns, map_interface):
        self.map_interface = map_interface
        Map.Map.init_map(map_size_lines, map_size_columns, map_interface)
        self.player_count = player_count
        self.defeated_players = 0
        self.current_player = -1
        self.is_player_turn = False
        self.players = []
        self.cities_coordinates = []
        self.units_coordinates = []
        self.districts_coordinates = []
        while Player.Player.player_count < player_count:
            self.players.append(Player.Player(self.players))
        for player in self.players:
            for unit in player.units:
                coord = map_interface.convert_coordinates_to_mine(unit.position_line, unit.position_column)
                unit_id = map_interface.add_unit_on_tile(coord, unit.type, player.player_id)
                unit.unit_id = unit_id
                self.units_coordinates.append((unit.position_line, unit.position_column))

    def start_turn(self):
        if self.current_player == self.player_count - 1:
            self.current_player = 0
            for i in range(self.player_count):
                for unit in self.players[i].units:
                    unit.rest()
                for city in self.players[i].cities:
                    city.recover_health()
        else:
            self.current_player = self.current_player + 1
            while self.players[self.current_player] is None:
                self.current_player = (self.current_player + 1) % self.player_count

        # victory conditions
        if self.defeated_players == self.player_count - 1:
            return 1
        if self.players[self.current_player].resources.science_count >= 1500:
            return 2
        if self.players[self.current_player].resources.culture_count >= 1500:
            return 3
        self.players[self.current_player].reset_units_movements()
        self.is_player_turn = True
        pos = (self.players[self.current_player].capital_line, self.players[self.current_player].capital_column)
        self.map_interface.switch_context(self.current_player, pos)
        return 0

    def end_turn(self):
        self.players[self.current_player].end_turn_resource_calculation()
        return self.start_turn()

    def identify_object(self, tile_line, tile_column) -> list[int]:
        objects = [0, ]
        if (tile_line, tile_column) in self.units_coordinates:
            # code for unit
            objects.append(1)
        if (tile_line, tile_column) in self.cities_coordinates:
            # code for city
            objects.append(2)
        return objects

    def current_player_is_owner(self, tile_line, tile_column) -> dict[int, bool]:
        objects = self.identify_object(tile_line, tile_column)
        ownerships = {}
        if 0 in objects:
            ownerships[0] = self.players[self.current_player].is_tile_owner(tile_line, tile_column)
        if 1 in objects:
            ownerships[1] = self.players[self.current_player].is_unit_owner(tile_line, tile_column)
        if 2 in objects:
            ownerships[2] = self.players[self.current_player].is_city_owner(tile_line, tile_column)
        return ownerships

    def get_city_owner(self, tile_line, tile_column) -> int:
        for player in self.players:
            if player.is_city_owner(tile_line, tile_column):
                return player.player_id
        return -1

    def get_unit_owner(self, tile_line, tile_column) -> int:
        for player in self.players:
            if player.is_unit_owner(tile_line, tile_column):
                return player.player_id
        return -1

    def get_unit_actions(self, tile_line, tile_column):
        possible_actions = []
        # if the player whose turn it currently is doesn't own the unit, they get no actions
        ownerships = self.current_player_is_owner(tile_line, tile_column)
        if 1 in ownerships.keys():
            if not ownerships[1]:
                return possible_actions

        for unit in self.players[self.current_player].units:
            if unit.position_line == tile_line and unit.position_column == tile_column:
                # all units can move, so 0 is code for can_move
                possible_actions.append(0)
                if unit.type_id in [0, 2, 4]:
                    # melee units can cause a melee attack, which is 1
                    possible_actions.append(1)
                elif unit.type_id in [1, 3, 5]:
                    # ranged units can cause a ranged attack, which is 2
                    possible_actions.append(2)
                elif unit.type_id in [6]:
                    # settlers can't attack but can settle a city, code 3
                    # if there's another city nearby, can't settle
                    can_settle = True
                    for city_coords in self.cities_coordinates:
                        if Map.Map.get_shortest_distance(tile_line, tile_column, city_coords[0], city_coords[1]) <= 3:
                            can_settle = False
                            break
                    if can_settle:
                        possible_actions.append(3)
        return possible_actions

    def purchase_unit_with_production(self, tile_line, tile_column, unit_type_id):
        place_line = tile_line
        place_column = tile_column
        if unit_type_id in [4, 5]:
            for city in self.players[self.current_player].cities:
                if city.center_line_location == tile_line and city.center_column_location == tile_column:
                    for tile in city.tiles:
                        if tile.type_id in [2, 3] and (tile.line, tile.column) not in self.units_coordinates:
                            place_line = tile.line
                            place_column = tile.column
                            break

        purchase_result = self.players[self.current_player].build_unit_with_production(place_line, place_column,
                                                                                       tile_line, tile_column,
                                                                                       unit_type_id, 0)
        coords = self.map_interface.convert_coordinates_to_mine(place_line, place_column)
        if purchase_result == 0:
            unit_id = self.map_interface.add_unit_on_tile(coords, Unit.unit_classes[unit_type_id], self.current_player)
            self.players[self.current_player].units[len(self.players[self.current_player].units) - 1].unit_id = unit_id
            self.units_coordinates.append((place_line, place_column))
            return True
        # some error happened, not supposed to be able to call this function if the resources aren't in possession
        return False

    def purchase_unit_with_gold(self, tile_line, tile_column, unit_type_id):
        place_line = tile_line
        place_column = tile_column
        if unit_type_id in [4, 5]:
            for city in self.players[self.current_player].cities:
                if city.center_line_location == tile_line and city.center_column_location == tile_column:
                    for tile in city.tiles:
                        if tile.type_id in [2, 3] and (tile.line, tile.column) not in self.units_coordinates:
                            place_line = tile.line
                            place_column = tile.column
                            break
        purchase_result = self.players[self.current_player].build_unit_with_gold(place_line, place_column,
                                                                                 unit_type_id, 0)
        coords = self.map_interface.convert_coordinates_to_mine(place_line, place_column)
        if purchase_result == 0:
            unit_id = self.map_interface.add_unit_on_tile(coords, Unit.unit_classes[unit_type_id], self.current_player)
            self.players[self.current_player].units[len(self.players[self.current_player].units) - 1].unit_id = unit_id
            self.units_coordinates.append((place_line, place_column))
            return True
        # some error happened, not supposed to be able to call this function if the resources aren't in possession
        return False

    def move_unit(self, tile_line, tile_column, new_tile_line, new_tile_column):
        self.remove_highlight_move_tiles(tile_line, tile_column)
        moved_unit = None
        objects = self.identify_object(new_tile_line, new_tile_column)
        for unit in self.players[self.current_player].units:
            if unit.position_line == tile_line and unit.position_column == tile_column:
                moved_unit = unit
                break
        if moved_unit is None:
            return False
        # if it's a settler, it can only move, so cancel any movements on tiles where other players / cities are
        is_settler = (moved_unit.type_id == 6)
        # check if movement is valid
        can_move = (Map.Map.get_unit_shortest_distance(tile_line, tile_column, new_tile_line, new_tile_column)
                    <= moved_unit.remaining_movement)
        can_ranged_attack = (Map.Map.get_shortest_distance(tile_line, tile_column, new_tile_line, new_tile_column)
                             <= moved_unit.range)
        # if the unit can cause a ranged attack, do it and finish this unit's turn
        if can_ranged_attack:
            if 1 in objects:
                unit_owner = self.get_unit_owner(new_tile_line, new_tile_column)
                if unit_owner != self.current_player:
                    for unit in self.players[unit_owner].units:
                        if unit.position_line == new_tile_line and unit.position_column == new_tile_column:
                            unit.calculate_ranged_combat_with_unit(moved_unit)
                            if unit.health_percentage <= 0:
                                self.map_interface.clr_unit(unit.unit_id)
                                self.players[unit_owner].delete_units(new_tile_line, new_tile_column)
                            moved_unit.remaining_movement = 0
                            moved_unit.range = 0
                            unit.health_percentage = round(unit.health_percentage)
                            return True
            if 2 in objects:
                city_owner = self.get_city_owner(new_tile_line, new_tile_column)
                if city_owner != self.current_player:
                    for city in self.players[city_owner].cities:
                        if (city.center_line_location == new_tile_line and
                            city.center_column_location == new_tile_column):
                            city.ranged_combat(moved_unit)
                            moved_unit.remaining_movement = 0
                            moved_unit.range = 0
                            city.health_percentage = max(round(city.health_percentage), 0)
                            return True
        # check if unit can move to the position and if there is a unit or city there, attack it
        # before attacking, check if the next-to-last tile on the path can be moved to, and if it can,
        # move there before attacking
        # melee attacks will finish a units turn
        if not can_move:
            return False
        if is_settler and (1 in objects or 2 in objects):
            return False
        shortest_path = Map.Map.get_unit_shortest_path(tile_line, tile_column, new_tile_line, new_tile_column)
        next_to_last_tile = (shortest_path[len(shortest_path) - 2] // Map.Map.columns,
                             shortest_path[len(shortest_path) - 2] % Map.Map.columns)
        if (1 in objects and ((next_to_last_tile not in self.units_coordinates
            and next_to_last_tile not in self.cities_coordinates) or len(shortest_path) == 2)):
            unit_owner = self.get_unit_owner(new_tile_line, new_tile_column)
            if unit_owner == self.current_player:
                return False
            for unit in self.players[unit_owner].units:
                if unit.position_line == new_tile_line and unit.position_column == new_tile_column:
                    unit.calculate_melee_combat_with_unit(moved_unit)
                    moved_unit.calculate_melee_combat_with_unit(unit)
                    unit.health_percentage = round(unit.health_percentage)
                    moved_unit.health_percentage = round(moved_unit.health_percentage)
                    if unit.health_percentage <= 0:
                        self.players[unit_owner].delete_units(new_tile_line, new_tile_column)
                        self.__render_movement(moved_unit, tile_line, tile_column, new_tile_line, new_tile_column)
                    else:
                        self.__render_movement(moved_unit, tile_line, tile_column, next_to_last_tile[0],
                                               next_to_last_tile[1])
                    if moved_unit.health_percentage <= 0:
                        self.map_interface.clr_unit(moved_unit.unit_id)
                        self.players[self.current_player].delete_units(moved_unit.position_line,
                                                                       moved_unit.position_column)
                    moved_unit.remaining_movement = 0
                    return True
        if (2 in objects and ((next_to_last_tile not in self.units_coordinates
            and next_to_last_tile not in self.cities_coordinates) or len(shortest_path) == 2)):
            city_owner = self.get_city_owner(new_tile_line, new_tile_column)
            if city_owner != self.current_player:
                for city in self.players[city_owner].cities:
                    if city.center_line_location == new_tile_line and city.center_column_location == new_tile_column:
                        city.melee_combat(moved_unit)
                        moved_unit.calculate_melee_combat_with_city(city)
                        city.health_percentage = round(city.health_percentage)
                        moved_unit.health_percentage = round(moved_unit.health_percentage)
                        if city.health_percentage <= 0:
                            ret = self.players[city_owner].delete_city(new_tile_line, new_tile_column)
                            if ret == 1:
                                for captured_city in self.players[city_owner].cities:
                                    for tile in captured_city.tiles:
                                        coord = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
                                        self.map_interface.remove_owner(coord)
                                        self.map_interface.add_tile_owner(coord, self.current_player)
                                    self.players[self.current_player].cities.append(captured_city)
                                for unit in self.players[city_owner].units:
                                    self.map_interface.clr_unit(unit.unit_id)
                                self.players[city_owner] = None
                                self.defeated_players += 1
                            else:
                                self.players[self.current_player].cities.append(city)
                            if moved_unit.health_percentage <= 0:
                                moved_unit.health_percentage = 1
                            self.__render_movement(moved_unit, tile_line, tile_column, new_tile_line, new_tile_column)
                        if moved_unit.health_percentage <= 0:
                            self.map_interface.clr_unit(moved_unit.unit_id)
                            self.players[self.current_player].delete_units(moved_unit.position_line,
                                                                           moved_unit.position_column)
                        moved_unit.remaining_movement = 0
                        return True
        elif 1 in objects:
            return False
        self.__render_movement(moved_unit, tile_line, tile_column, new_tile_line, new_tile_column)
        return True

    def __render_movement(self, moved_unit, tile_line, tile_column, new_tile_line, new_tile_column):
        self.players[self.current_player].move_unit(tile_line, tile_column, new_tile_line, new_tile_column)
        coords = self.map_interface.convert_coordinates_to_mine(new_tile_line, new_tile_column)
        self.map_interface.move_unit(moved_unit.unit_id, coords)
        for coordinate_pair in self.units_coordinates:
            if coordinate_pair[0] == tile_line and coordinate_pair[1] == tile_column:
                self.units_coordinates.remove(coordinate_pair)
                self.units_coordinates.append((new_tile_line, new_tile_column))

    def highlight_move_tiles(self, tile_line, tile_column):
        if self.get_unit_owner(tile_line, tile_column) != self.current_player:
            return False
        moved_unit = None
        for unit in self.players[self.current_player].units:
            if unit.position_line == tile_line and unit.position_column == tile_column:
                moved_unit = unit
                break
        reachable_tiles = Map.Map.get_unit_reachable_tiles(tile_line, tile_column, moved_unit.remaining_movement)
        for tile in reachable_tiles:
            if tile in self.units_coordinates or tile in self.cities_coordinates:
                continue
            coords = self.map_interface.convert_coordinates_to_mine(tile[0], tile[1])
            self.map_interface.add_tile_selector(coords)

    def remove_highlight_move_tiles(self, tile_line, tile_column):
        if self.get_unit_owner(tile_line, tile_column) != self.current_player:
            return False
        moved_unit = None
        for unit in self.players[self.current_player].units:
            if unit.position_line == tile_line and unit.position_column == tile_column:
                moved_unit = unit
                break
        reachable_tiles = Map.Map.get_unit_reachable_tiles(tile_line, tile_column, moved_unit.remaining_movement)
        for tile in reachable_tiles:
            coords = self.map_interface.convert_coordinates_to_mine(tile[0], tile[1])
            self.map_interface.rmv_tile_selector(coords)

    def highlight_purchase_tiles(self, tile_line, tile_column, district_id):
        if self.get_city_owner(tile_line, tile_column) != self.current_player:
            return False
        selected_city = None
        for city in self.players[self.current_player].cities:
            if city.center_line_location == tile_line and city.center_column_location == tile_column:
                selected_city = city
                break
        for tile in selected_city.tiles:
            if ((tile.line, tile.column) in self.districts_coordinates
                or tile not in self.players[self.current_player].tiles
                or district_id == 3 and tile.type_id != 2
                or district_id != 3 and tile.type_id in [2, 3]):
                continue
            coords = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
            self.map_interface.add_tile_selector(coords)

    def remove_highlight_purchase_tiles(self, tile_line, tile_column):
        if self.get_city_owner(tile_line, tile_column) != self.current_player:
            return False
        selected_city = None
        for city in self.players[self.current_player].cities:
            if city.center_line_location == tile_line and city.center_column_location == tile_column:
                selected_city = city
                break
        for tile in selected_city.tiles:
            coords = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
            self.map_interface.rmv_tile_selector(coords)

    def settle_city(self, tile_line, tile_column):
        settler = None
        for unit in self.players[self.current_player].units:
            if unit.position_line == tile_line and unit.position_column == tile_column:
                settler = unit
        self.map_interface.clr_unit(settler.unit_id)
        self.units_coordinates.remove((tile_line, tile_column))
        self.players[self.current_player].delete_units(tile_line, tile_column)
        city_name = random.randint(0, len(City.city_names))
        City.city_names.pop(city_name)
        self.players[self.current_player].add_cities(City.city_names[city_name], tile_line, tile_column)
        self.cities_coordinates.append((tile_line, tile_column))
        self.districts_coordinates.append((tile_line, tile_column))
        coords = self.map_interface.convert_coordinates_to_mine(tile_line, tile_column)
        self.map_interface.add_object_on_tile(coords, "City Center")
        for tile in self.players[self.current_player].tiles:
            coords = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
            self.map_interface.add_tile_owner(coords, self.current_player)

    def get_city_actions(self, tile_line, tile_column):
        purchasable_units = [[], [], [], [], [], [], []]
        purchasable_districts = []
        purchasable_buildings = [[], [], [], [], [], [], [], []]
        purchasable_units_gold = [[], [], [], [], [], [], []]
        purchasable_districts_gold = []
        purchasable_buildings_gold = [[], [], [], [], [], [], [], []]

        ownerships = self.current_player_is_owner(tile_line, tile_column)
        if 2 in ownerships.keys():
            if not ownerships[2]:
                return (False, purchasable_units, purchasable_districts, purchasable_buildings,
                        purchasable_units_gold, purchasable_districts_gold, purchasable_buildings_gold)

        for city in self.players[self.current_player].cities:
            if city.center_line_location == tile_line and city.center_column_location == tile_column:
                campus = city.get_district_by_type(0)
                if not campus:
                    purchasable_districts.append(0)
                    purchasable_districts_gold.append(0)
                elif len(campus.buildings) == 0:
                    if city.city_resources.production_count >= City.campus_buildings_costs[0]:
                        purchasable_buildings[0].extend([0])
                    if self.players[self.current_player].resources.gold_count >= City.campus_buildings_costs[0] * 2:
                        purchasable_buildings_gold[0].extend([0])
                elif len(campus.buildings) == 1:
                    if city.city_resources.production_count >= City.campus_buildings_costs[1]:
                        purchasable_buildings[0].extend([1])
                    if self.players[self.current_player].resources.gold_count >= City.campus_buildings_costs[1]:
                        purchasable_buildings_gold[0].extend([1])
                else:
                    purchasable_buildings[0] = []
                    purchasable_buildings_gold[0] = []
                theatre_square = city.get_district_by_type(1)
                if not theatre_square:
                    purchasable_districts.append(1)
                    purchasable_districts_gold.append(1)
                elif len(theatre_square.buildings) == 0:
                    if city.city_resources.production_count >= City.theatre_square_buildings_costs[0]:
                        purchasable_buildings[1].extend([0])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.theatre_square_buildings_costs[0] * 2):
                        purchasable_buildings_gold[1].extend([0])
                elif len(theatre_square.buildings) == 1:
                    if city.city_resources.production_count >= City.theatre_square_buildings_costs[1]:
                        purchasable_buildings[1].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.theatre_square_buildings_costs[1] * 2):
                        purchasable_buildings_gold[1].extend([1])
                else:
                    purchasable_buildings[1] = []
                    purchasable_buildings_gold[1] = []

                commercial_hub = city.get_district_by_type(2)
                if not commercial_hub:
                    purchasable_districts.append(2)
                    purchasable_districts_gold.append(2)
                elif len(commercial_hub.buildings) == 0:
                    if city.city_resources.production_count >= City.commercial_hub_buildings_costs[0]:
                        purchasable_buildings[2].extend([0])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.commercial_hub_buildings_costs[0] * 2):
                        purchasable_buildings_gold[2].extend([0])
                elif len(commercial_hub.buildings) == 1:
                    if city.city_resources.production_count >= City.commercial_hub_buildings_costs[1]:
                        purchasable_buildings[2].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.commercial_hub_buildings_costs[1] * 2):
                        purchasable_buildings_gold[2].extend([1])
                else:
                    purchasable_buildings[2] = []
                    purchasable_buildings_gold[2] = []

                harbour = city.get_district_by_type(3)
                if not harbour:
                    purchasable_districts.append(3)
                    purchasable_districts_gold.append(3)
                elif len(harbour.buildings) == 0:
                    if city.city_resources.production_count >= City.harbour_buildings_costs[0]:
                        purchasable_buildings[3].extend([0])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.harbour_buildings_costs[0] * 2):
                        purchasable_buildings_gold[3].extend([0])
                elif len(harbour.buildings) == 1:
                    if city.city_resources.production_count >= City.harbour_buildings_costs[1]:
                        purchasable_buildings[3].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.harbour_buildings_costs[1] * 2):
                        purchasable_buildings_gold[3].extend([1])
                else:
                    purchasable_buildings[3] = []
                    purchasable_buildings_gold[3] = []

                industrial_zone = city.get_district_by_type(4)
                if not industrial_zone:
                    purchasable_districts.append(4)
                    purchasable_districts_gold.append(4)
                elif len(industrial_zone.buildings) == 0:
                    if city.city_resources.production_count >= City.industrial_zone_buildings_costs[0]:
                        purchasable_buildings[4].extend([0])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.industrial_zone_buildings_costs[0] * 2):
                        purchasable_buildings_gold[4].extend([0])
                elif len(industrial_zone.buildings) == 1:
                    if city.city_resources.production_count >= City.industrial_zone_buildings_costs[1]:
                        purchasable_buildings[4].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.industrial_zone_buildings_costs[1] * 2):
                        purchasable_buildings_gold[4].extend([1])
                else:
                    purchasable_buildings[0] = []
                    purchasable_buildings_gold[0] = []

                neighborhood = city.get_district_by_type(5)
                if not neighborhood:
                    purchasable_districts.append(5)
                    purchasable_districts_gold.append(5)
                elif len(neighborhood.buildings) == 0:
                    if city.city_resources.production_count >= City.neighborhood_buildings_costs[0]:
                        purchasable_buildings[5].extend([0])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.neighborhood_buildings_costs[0] * 2):
                        purchasable_buildings_gold[5].extend([0])
                else:
                    purchasable_buildings[5] = []
                    purchasable_buildings_gold[5] = []

                aqueduct = city.get_district_by_type(6)
                if not aqueduct:
                    purchasable_districts.append(6)
                    purchasable_districts_gold.append(6)

                city_center = city.get_district_by_type(7)
                if ("Monument" not in city_center.buildings and city.city_resources.production_count >=
                        City.city_center_buildings_costs[1]):
                    purchasable_buildings[7].extend([1])
                if ("Monument" not in city_center.buildings and self.players[self.current_player].resources.gold_count
                    >= City.city_center_buildings_costs[1] * 2):
                    purchasable_buildings_gold[7].extend([1])
                if ("Granary" not in city_center.buildings and city.city_resources.production_count >=
                    City.city_center_buildings_costs[2]):
                    purchasable_buildings[7].extend([2])
                if ("Granary" not in city_center.buildings and self.players[self.current_player].resources.gold_count
                    >= City.city_center_buildings_costs[2] * 2):
                    purchasable_buildings_gold[7].extend([2])
                if ("Water Mill" not in city_center.buildings and city.city_resources.production_count >=
                    City.city_center_buildings_costs[3]):
                    purchasable_buildings[7].extend([3])
                if ("Water Mill" not in city_center.buildings and self.players[self.current_player].resources.gold_count
                    >= City.city_center_buildings_costs[3] * 2):
                    purchasable_buildings_gold[7].extend([3])
                if ("Sewer" not in city_center.buildings and city.city_resources.production_count >=
                    City.city_center_buildings_costs[4]):
                    purchasable_buildings[7].extend([4])
                if ("Sewer" not in city_center.buildings and self.players[self.current_player].resources.gold_count >=
                    City.city_center_buildings_costs[4] * 2):
                    purchasable_buildings_gold[7].extend([4])

                if city.city_resources.production_count < City.district_cost:
                    purchasable_districts = []
                if self.players[self.current_player].resources.gold_count < City.district_cost * 2:
                    purchasable_districts_gold = []

                if city.city_resources.production_count >= Unit.melee_units_costs[0]:
                    purchasable_units[0].extend([0])
                if city.city_resources.production_count >= Unit.ranged_units_costs[0]:
                    purchasable_units[1].extend([0])
                if city.city_resources.production_count >= Unit.cavalry_units_costs[0]:
                    purchasable_units[2].extend([0])
                if city.city_resources.production_count >= Unit.siege_units_costs[0]:
                    purchasable_units[3].extend([0])
                if city.city_resources.production_count >= Unit.naval_melee_units_costs[0]:
                    purchasable_units[4].extend([0])
                if city.city_resources.production_count >= Unit.naval_ranged_units_costs[0]:
                    purchasable_units[5].extend([0])
                if city.city_resources.production_count > Unit.civilian_units_costs:
                    purchasable_units[6].extend([0])

                if self.players[self.current_player].resources.gold_count >= Unit.melee_units_costs[0] * 2:
                    purchasable_units_gold[0].extend([0])
                if self.players[self.current_player].resources.gold_count >= Unit.ranged_units_costs[0] * 2:
                    purchasable_units_gold[1].extend([0])
                if self.players[self.current_player].resources.gold_count >= Unit.cavalry_units_costs[0] * 2:
                    purchasable_units_gold[2].extend([0])
                if self.players[self.current_player].resources.gold_count >= Unit.siege_units_costs[0] * 2:
                    purchasable_units_gold[3].extend([0])
                if self.players[self.current_player].resources.gold_count >= Unit.naval_melee_units_costs[0] * 2:
                    purchasable_units_gold[4].extend([0])
                if self.players[self.current_player].resources.gold_count >= Unit.naval_ranged_units_costs[0] * 2:
                    purchasable_units_gold[5].extend([0])

                if (tile_line, tile_column) in self.units_coordinates:
                    purchasable_units = [[], [], [], [], purchasable_units[4], purchasable_units[5], []]
                    purchasable_units_gold = [[], [], [], [], purchasable_units_gold[4],
                                              purchasable_units_gold[5], []]
                if not city.is_coastal:
                    purchasable_units[4] = []
                    purchasable_units[5] = []
                    purchasable_units_gold[4] = []
                    purchasable_units_gold[5] = []

        print(purchasable_buildings[7])
        return (True, purchasable_units, purchasable_districts, purchasable_buildings,
               purchasable_units_gold, purchasable_districts_gold, purchasable_buildings_gold)

    def purchase_building_with_production(self, tile_line, tile_column, district_id, building_id):
        print(tile_line, tile_column, district_id, building_id)
        self.players[self.current_player].build_building_with_production(tile_line, tile_column,
                                                                         district_id, building_id)

    def purchase_building_with_gold(self, tile_line, tile_column, district_id, building_id):
        self.players[self.current_player].build_building_with_gold(tile_line, tile_column,
                                                                   district_id, building_id)

    def purchase_district_with_production(self, city_tile_line, city_tile_column, tile_line, tile_column, district_id):
        self.remove_highlight_purchase_tiles(city_tile_line, city_tile_column)
        if (tile_line, tile_column) in self.districts_coordinates:
            return False
        tile = Map.Map.get_tile(tile_line, tile_column)
        if tile not in self.players[self.current_player].tiles:
            return False
        if district_id == 3 and tile.type_id != 2:
            return False
        if district_id != 3 and tile.type_id in [2, 3]:
            return False
        self.players[self.current_player].build_district_with_production(city_tile_line, city_tile_column, district_id,
                                                                         tile_line, tile_column, self.players)
        self.districts_coordinates.append((tile_line, tile_column))
        coords = self.map_interface.convert_coordinates_to_mine(tile_line, tile_column)
        self.map_interface.add_object_on_tile(coords, City.district_types[district_id])
        for tile in self.players[self.current_player].tiles:
            coords = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
            self.map_interface.add_tile_owner(coords, self.current_player)

    def purchase_district_with_gold(self, city_tile_line, city_tile_column, tile_line, tile_column, district_id):
        self.remove_highlight_purchase_tiles(city_tile_line, city_tile_column)
        if (tile_line, tile_column) in self.districts_coordinates:
            return False
        tile = Map.Map.get_tile(tile_line, tile_column)
        if tile not in self.players[self.current_player].tiles:
            return False
        if district_id == 3 and tile.type_id != 2:
            return False
        if district_id != 3 and tile.type_id in [2, 3]:
            return False
        self.players[self.current_player].build_district_with_gold(city_tile_line, city_tile_column,district_id,
                                                                         tile_line, tile_column, self.players)
        self.districts_coordinates.append((tile_line, tile_column))
        coords = self.map_interface.convert_coordinates_to_mine(city_tile_line, city_tile_column)
        self.map_interface.add_object_on_tile(coords, City.district_types[district_id])
        for tile in self.players[self.current_player].tiles:
            coords = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
            self.map_interface.add_tile_owner(coords, self.current_player)

    def get_city_information(self, city_tile_line, city_tile_column):
        for city in self.players[self.current_player].cities:
            if city_tile_line == city.center_line_location and city_tile_column == city.center_column_location:
                player_resources_per_turn, city_resources_per_turn = city.get_resources()
                food_per_turn = city_resources_per_turn.food_per_turn_count
                production_per_turn = city_resources_per_turn.production_per_turn_count
                gold_per_turn = player_resources_per_turn.gold_per_turn_count
                culture_per_turn = player_resources_per_turn.culture_per_turn_count
                science_per_turn = player_resources_per_turn.science_per_turn_count
                total_food = city.city_resources.food_count
                total_production = city.city_resources.production_count
                housing = city.housing
                population = city.population
                health = city.health_percentage
                combat_strength = city.melee_combat_strength
                city_name = city.city_name
                return (food_per_turn, production_per_turn, gold_per_turn, culture_per_turn, science_per_turn,
                        total_food, total_production, housing, population, health, combat_strength, city_name)

    def get_unit_information(self, unit_line, unit_column):
        for i in range(self.player_count):
            for unit in self.players[self.current_player].units:
                if unit.position_line == unit_line and unit.position_column == unit_column:
                    unit_health = unit.health_percentage
                    melee_strength = unit.melee_strength
                    ranged_strength = unit.ranged_strength
                    movement = unit.remaining_movement
                    unit_name = unit.name
                    return unit_health, melee_strength, ranged_strength, movement, unit_name

    def get_player_information(self):
        total_science = self.players[self.current_player].resources.science_count
        science_per_turn = self.players[self.current_player].resources_per_turn.science_per_turn_count
        total_culture = self.players[self.current_player].resources.culture_count
        culture_per_turn = self.players[self.current_player].resources_per_turn.culture_per_turn_count
        total_gold = self.players[self.current_player].resources.gold_count
        gold_per_turn = self.players[self.current_player].resources_per_turn.gold_per_turn_count
        player_number = self.current_player + 1
        return (player_number, total_science, total_culture, total_gold,
                science_per_turn, culture_per_turn, gold_per_turn)

    @staticmethod
    def get_tile(tile_line, tile_column):
        tile = Map.Map.get_tile(tile_line, tile_column)
        tile_type = tile.type_id
        tile_basic_resource = tile.basic_resource_id
        # basic resource id, -1 for no basic resource or basic resource not known by the player
        if tile_basic_resource == 7:
            tile_basic_resource = -1
        tile_strategic_resource = tile.strategic_resource_id
        # strategic resource id, -1 for no strategic resource or strategic resource not known by the player
        if tile_strategic_resource == 4:
            tile_strategic_resource = -1
        tile_luxury_resource = tile.luxury_resource_id
        # luxury resource id, -1 for no luxury resource
        if tile_luxury_resource == 5:
            tile_luxury_resource = -1
        tile_feature_id = tile.feature_id
        # feature id, -1 for no feature
        if tile_feature_id == 4:
            tile_feature_id = -1
        food_yield = tile.city_resources.food_per_turn_count
        production_yield = tile.city_resources.production_per_turn_count
        science_yield = tile.resources.science_per_turn_count
        culture_yield = tile.resources.culture_per_turn_count
        gold_yield = tile.resources.gold_per_turn_count

        return (tile_type, tile_basic_resource, tile_strategic_resource, tile_luxury_resource, tile_feature_id,
                food_yield, production_yield, science_yield, culture_yield, gold_yield)
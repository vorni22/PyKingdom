import random

import Logic.Player as Player
import Logic.City as City
import Logic.Resources as Resources
import Logic.Unit as Unit
import Logic.Tech as Tech
import Logic.Civic as Civic
import Map_Generation.Map as Map

# class that will be used for integrating the UI and the graphics with the backend of the game
class Game:
    def __init__(self, player_count, map_size_lines, map_size_columns, map_interface):
        self.map_interface = map_interface
        Map.Map.init_map(map_size_lines, map_size_columns, map_interface)
        self.player_count = player_count
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
        else:
            self.current_player = self.current_player + 1
        self.players[self.current_player].reset_units_movements()
        self.is_player_turn = True
        # Do not touch yet, not fully implemented
        # self.map_interface.switch_context(self.current_player, None)

    def end_turn(self):
        self.players[self.current_player].end_turn_resource_calculation()
        self.start_turn()
        self.is_player_turn = False

    def identify_object(self, tile_line, tile_column) -> list[int]:
        objects = [0, ]
        if (tile_line, tile_column) in self.units_coordinates:
            # code for unit
            objects.append(1)
        elif (tile_line, tile_column) in self.cities_coordinates:
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
        purchase_result = self.players[self.current_player].build_unit_with_production(tile_line, tile_column,
                                                                                       unit_type_id, 0)
        coords = self.map_interface.convert_coordinates_to_mine(tile_line, tile_column)
        if purchase_result == 0:
            unit_id = self.map_interface.add_unit_on_tile(coords, Unit.unit_classes[unit_type_id], self.current_player)
            self.players[self.current_player].units[len(self.players[self.current_player].units) - 1].unit_id = unit_id
            return True
        # some error happened, not supposed to be able to call this function if the resources aren't in possession
        return False

    def purchase_unit_with_gold(self, tile_line, tile_column, unit_type_id):
        purchase_result = self.players[self.current_player].build_unit_with_gold(tile_line, tile_column,
                                                                                 unit_type_id, 0)
        coords = self.map_interface.convert_coordinates_to_mine(tile_line, tile_column)
        if purchase_result == 0:
            unit_id = self.map_interface.add_unit_on_tile(coords, Unit.unit_classes[unit_type_id], self.current_player)
            self.players[self.current_player].units[len(self.players[self.current_player].units) - 1].unit_id = unit_id
            return True
        # some error happened, not supposed to be able to call this function if the resources aren't in possession
        return False

    def move_unit(self, tile_line, tile_column, new_tile_line, new_tile_column):
        # add stuff for triggering attack if there is an enemy city or unit on the new tile

        move_result = self.players[self.current_player].move_unit(tile_line, tile_column,
                                                                  new_tile_line, new_tile_column)
        moved_unit = None
        for unit in self.players[self.current_player].units:
            if unit.position_line == tile_line and unit.position_column == tile_column:
                moved_unit = unit
        coords = self.map_interface.convert_coordinates_to_mine(new_tile_line, new_tile_column)
        if move_result == 0:
            self.map_interface.move_unit(moved_unit.unit_id, coords)
            return True
        return False

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
        purchasable_buildings = [[], [], [], [], [], [], []]
        purchasable_units_gold = [[], [], [], [], [], [], []]
        purchasable_districts_gold = []
        purchasable_buildings_gold = [[], [], [], [], [], [], []]

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
                else:
                    if city.city_resources.production_count >= City.campus_buildings_costs[1]:
                        purchasable_buildings[0].extend([1])
                    if self.players[self.current_player].resources.gold_count >= City.campus_buildings_costs[1]:
                        purchasable_buildings_gold[0].extend([1])

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
                else:
                    if city.city_resources.production_count >= City.theatre_square_buildings_costs[1]:
                        purchasable_buildings[1].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.theatre_square_buildings_costs[1] * 2):
                        purchasable_buildings_gold[1].extend([1])

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
                else:
                    if city.city_resources.production_count >= City.commercial_hub_buildings_costs[1]:
                        purchasable_buildings[2].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.commercial_hub_buildings_costs[1] * 2):
                        purchasable_buildings_gold[2].extend([1])

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
                else:
                    if city.city_resources.production_count >= City.harbour_buildings_costs[1]:
                        purchasable_buildings[3].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.harbour_buildings_costs[1] * 2):
                        purchasable_buildings_gold[3].extend([1])

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
                else:
                    if city.city_resources.production_count >= City.industrial_zone_buildings_costs[1]:
                        purchasable_buildings[4].extend([1])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.industrial_zone_buildings_costs[1] * 2):
                        purchasable_buildings_gold[4].extend([1])

                neighborhood = city.get_district_by_type(5)
                if not neighborhood:
                    purchasable_districts.append(5)
                    purchasable_districts_gold.append(5)
                else:
                    if city.city_resources.production_count >= City.neighborhood_buildings_costs[0]:
                        purchasable_buildings[5].extend([0])
                    if (self.players[self.current_player].resources.gold_count >=
                        City.neighborhood_buildings_costs[0] * 2):
                        purchasable_buildings_gold[5].extend([0])

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

        return (True, purchasable_units, purchasable_districts, purchasable_buildings,
               purchasable_units_gold, purchasable_districts_gold, purchasable_buildings_gold)

    def purchase_building_with_production(self, tile_line, tile_column, district_id, building_id):
        self.players[self.current_player].build_building_with_production(tile_line, tile_column,
                                                                         district_id, building_id)

    def purchase_building_with_gold(self, tile_line, tile_column, district_id, building_id):
        self.players[self.current_player].build_building_with_gold(tile_line, tile_column,
                                                                   district_id, building_id)

    def purchase_district_with_production(self, city_tile_line, city_tile_column, tile_line, tile_column, district_id):
        if (tile_line, tile_column) in self.districts_coordinates:
            return False
        self.players[self.current_player].build_district_with_production(city_tile_line, city_tile_column,district_id,
                                                                         tile_line, tile_column)
        self.districts_coordinates.append((tile_line, tile_column))
        coords = self.map_interface.convert_coordinates_to_mine(city_tile_line, city_tile_column)
        self.map_interface.add_object_on_tile(coords, City.district_types[district_id])
        for tile in self.players[self.current_player].tiles:
            coords = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
            self.map_interface.add_tile_owner(coords, self.current_player)

    def purchase_district_with_gold(self, city_tile_line, city_tile_column, tile_line, tile_column, district_id):
        if (tile_line, tile_column) in self.districts_coordinates:
            return False
        self.players[self.current_player].build_district_with_gold(city_tile_line, city_tile_column,district_id,
                                                                         tile_line, tile_column)
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
        for unit in self.players[self.current_player].units:
            if unit.position_line == unit_line and unit.position_column == unit_column:
                unit_health = unit.health_percentage
                melee_strength = unit.melee_strength
                ranged_strength = unit.ranged_strength
                movement = unit.remaining_movement
                unit_name = unit.name
                return unit_health, melee_strength, ranged_strength, movement, unit_name

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
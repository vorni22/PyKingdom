import random

import Logic.Player as Player
import Logic.City as City
import Logic.Resources as Resources
import Logic.Unit as Unit
import Logic.Tech as Tech
import Logic.Civic as Civic
import Map_Generation.Map as Map
from Logic.Tile import tile_basic_resources, tile_strategic_resources, tile_luxury_resources

# class that will be used for integrating the UI with the backend of the game
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
        while Player.Player.player_count < player_count:
            self.players.append(Player.Player(self.players))
        for player in self.players:
            for unit in player.units:
                coord = map_interface.convert_coordinates_to_mine(unit.position_line, unit.position_column)
                unit_id = map_interface.add_unit_on_tile(coord, unit.type)
                unit.unit_id = unit_id

    def start_turn(self):
        if self.current_player == self.player_count - 1:
            self.current_player = 0
        else:
            self.current_player = self.current_player + 1
        self.players[self.current_player].reset_units_movements()

    def end_turn(self):
        self.players[self.current_player].end_turn_resource_calculation()
        self.start_turn()

    def identify_object(self, tile_line, tile_column) -> list[int]:
        objects = [0, ]
        if (tile_line, tile_column) in self.units_coordinates:
            # code for unit
            objects.append(1)
        elif (tile_line, tile_column) in self.cities_coordinates:
            # code for city
            objects.append(2)
        return objects

    def current_player_is_owner(self, tile_line, tile_column) -> list[dict[int, bool]]:
        objects = self.identify_object(tile_line, tile_column)
        ownerships = []
        if 0 in objects:
            ownerships.append({0: self.players[self.current_player].is_tile_owner(tile_line, tile_column)})
        if 1 in objects:
            ownerships.append({1: self.players[self.current_player].is_unit_owner(tile_line, tile_column)})
        if 2 in objects:
            ownerships.append({2: self.players[self.current_player].is_city_owner(tile_line, tile_column)})
        return ownerships

    def get_unit_actions(self, tile_line, tile_column):
        possible_actions = []
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

    def move_unit(self, tile_line, tile_column, new_tile_line, new_tile_column):
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
        for tile in self.players[self.current_player].cities[len(self.cities_coordinates) - 1]:
            coords = self.map_interface.convert_coordinates_to_mine(tile.line, tile.column)
            self.map_interface.add_tile_owner(coords, self.current_player)

    def get_city_actions(self, tile_line, tile_column):
        purchasable_units = [[], [], [], [], [], [], []]
        purchasable_districts = []
        purchasable_buildings = [[], [], [], [], [], [], []]
        for city in self.players[self.current_player].cities:
            if city.position_line == tile_line and city.position_column == tile_column:
                campus = city.get_district_by_type(0)
                if not campus:
                    purchasable_districts.append(0)
                elif len(campus.buildings) == 0:
                    purchasable_buildings[0].extend([0])
                else:
                    purchasable_buildings[0].extend([1])

                theatre_square = city.get_district_by_type(1)
                if not theatre_square:
                    purchasable_districts.extend([1])
                elif len(theatre_square.buildings) == 0:
                    purchasable_buildings[1].extend([0])
                else:
                    purchasable_buildings[1].extend([1])

                commercial_hub = city.get_district_by_type(2)
                if not commercial_hub:
                    purchasable_districts.append(0)
                elif len(commercial_hub.buildings) == 0:
                    purchasable_buildings[2].extend([0])
                else:
                    purchasable_buildings[2].extend([1])

                harbour = city.get_district_by_type(3)
                if not harbour:
                    purchasable_districts.append(0)
                elif len(harbour.buildings) == 0:
                    purchasable_buildings[3].extend([0])
                else:
                    purchasable_buildings[3].extend([1])

                industrial_zone = city.get_district_by_type(4)
                if not industrial_zone:
                    purchasable_districts.append(0)
                elif len(industrial_zone.buildings) == 0:
                    purchasable_buildings[4].extend([0])
                else:
                    purchasable_buildings[4].extend([1])

                neighborhoods = city.get_district_by_type(5)
                purchasable_districts.append(5)
                for _ in range(len(neighborhoods)):
                    purchasable_buildings[5].extend([0])

                aqueduct = city.get_district_by_type(6)
                if not aqueduct:
                    purchasable_districts.append(6)

                city_center = city.get_district_by_type(7)
                purchasable_buildings[7].extend([0, 1, 2, 3, 4])
                for building in city_center.buildings:
                    purchasable_buildings[7].remove(building)
                for i in range(0, len(purchasable_units)):
                    purchasable_units[i].extend([0])
        return purchasable_units, purchasable_districts, purchasable_buildings

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
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
    def __init__(self, player_count, map_size_lines, map_size_columns):
        Map.Map.init_map(map_size_lines, map_size_columns)
        self.player_count = player_count
        self.current_player = -1
        self.is_player_turn = False
        self.players = []
        self.cities_coordinates = []
        self.units_coordinates = []
        while Player.Player.player_count < player_count:
            self.players.append(Player.Player(self.players))

    def start_turn(self):
        if self.current_player == self.current_player - 1:
            self.current_player = 0
        else:
            self.current_player = self.current_player + 1
        self.players[self.current_player].reset_units_movements()

    def end_turn(self):
        self.players[self.current_player].end_turn_resource_calculation()

    def identify_object(self, tile_line, tile_column):
        objects = [0, ]
        if (tile_line, tile_column) in self.units_coordinates:
            # code for unit
            objects.append(1)
        elif (tile_line, tile_column) in self.cities_coordinates:
            # code for city
            objects.append(2)
        return objects

    def current_player_is_owner(self, object_id, tile_line, tile_column):
        if object_id == 1:
            return self.players[self.current_player].is_unit_owner(tile_line, tile_column)
        elif object_id == 2:
            return self.players[self.current_player].is_city_owner(tile_line, tile_column)

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

    def settle_city(self, tile_line, tile_column):
        self.players[self.current_player].delete_units(tile_line, tile_column)
        self.units_coordinates.remove((tile_line, tile_column))
        city_name = random.randint(0, len(City.city_names))
        City.city_names.pop(city_name)
        self.players[self.current_player].add_cities(City.city_names[city_name], tile_line, tile_column)
        self.cities_coordinates.append((tile_line, tile_column))

    def get_city_actions(self, tile_line, tile_column):
        purchasable_units = []
        purchasable_districts = []
        purchasable_buildings = [[], [], [], [], [], [], []]
        for city in self.players[self.current_player].cities:
            if city.position_line == tile_line and city.position_column == tile_column:
                campus = city.get_district_by_type(0)
                if not campus:
                    purchasable_districts.append(0)
                elif len(campus.buildings) == 0:
                    purchasable_buildings[0].append(0)
                else:
                    purchasable_buildings[0].append(1)

                theatre_square = city.get_district_by_type(1)
                if not theatre_square:
                    purchasable_districts.append(1)
                elif len(theatre_square.buildings) == 0:
                    purchasable_buildings[1].append(0)
                else:
                    purchasable_buildings[1].append(1)

                commercial_hub = city.get_district_by_type(2)
                if not commercial_hub:
                    purchasable_districts.append(0)
                elif len(commercial_hub.buildings) == 0:
                    purchasable_buildings[2].append(0)
                else:
                    purchasable_buildings[2].append(1)

                harbour = city.get_district_by_type(3)
                if not harbour:
                    purchasable_districts.append(0)
                elif len(harbour.buildings) == 0:
                    purchasable_buildings[3].append(0)
                else:
                    purchasable_buildings[3].append(1)

                industrial_zone = city.get_district_by_type(4)
                if not industrial_zone:
                    purchasable_districts.append(0)
                elif len(industrial_zone.buildings) == 0:
                    purchasable_buildings[4].append(0)
                else:
                    purchasable_buildings[4].append(1)

                neighborhoods = city.get_district_by_type(5)
                purchasable_districts.append(5)
                for _ in range(len(neighborhoods)):
                    purchasable_buildings[5].append(0)

                aqueduct = city.get_district_by_type(6)
                if not aqueduct:
                    purchasable_districts.append(6)

                city_center = city.get_district_by_type(7)
                purchasable_buildings[7].extend([0, 1, 2, 3, 4])
                for building in city_center.buildings:
                    purchasable_buildings[7].remove(building)
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
        science_yield = tile.resources.science_resource_per_turn_count
        culture_yield = tile.resources.culture_per_turn_count
        gold_yield = tile.resources.gold_resource_per_turn_count

        return (tile_type, tile_basic_resource, tile_strategic_resource, tile_luxury_resource, tile_feature_id,
                food_yield, production_yield, science_yield, culture_yield, gold_yield)

    def get_owned_techs(self):
        pass

import Logic.City as City
import Logic.Resources as Resources
import Logic.Unit as Unit
import Logic.Tech as Tech
import Logic.Civic as Civic
import Map_Generation.Map as Map
import random


# Holds information about a player
# @param player_id: the id of the player
# @param resources: the total resources owned by the player (not necessarily all ever earned)
# @param resources_per_turn: the amount of resources that should be earned by the player this turn
# to be updated at the start of the turn
# @param units: list of all the units the players owns. Each unit can be moved only by the owner player
# @param cities: list of all the cities the player owns. Each city can only be interacted with only by the owner player
# @param tiles: list of all tiles of all cities owned by the player - each player has a border color, with will be
# displayed around each tile owned by the player
# @param capital_line and capital_column: the position of the capital. The capital is the first city the player settles.
# If another player captures the capital - all cities of this players will be passed to the victor, and the initial
# owner will be defeated
class Player:
    player_count = 0
    def __init__(self, other_players):
        self.player_id = Player.player_count
        Player.player_count += 1

        self.resources = Resources.Resources(0, 0, 0)
        self.resources_per_turn = Resources.ResourcesPerTurn(0, 0, 0)
        self.tech_tree = Tech.TechTree()
        self.civic_tree = Civic.CivicTree()
        self.cities = []
        self.units = []
        self.tiles = []
        self.has_capital = False
        self.capital_line = None
        self.capital_column = None
        self.set_starting_position(other_players)

    def set_starting_position(self, other_players):
        while True:
            self.capital_line = random.randint(3, Map.Map.lines - 3)
            self.capital_column = random.randint(3, Map.Map.columns - 3)
            # ensure at least 3 tiles between players
            good_start = True
            for player in other_players:
                if Map.Map.get_shortest_distance(player.capital_line, player.capital_column,
                                                 self.capital_line, self.capital_column) < 3:
                    good_start = False
            if not good_start:
                continue
            if Map.Map.get_tile(self.capital_line, self.capital_column).type_id in [0, 1]:
                # add starting settler
                self.add_units(0, 6, self.capital_line, self.capital_column)
                # search for nearby good tile and give the player a warrior
                if Map.Map.get_tile(self.capital_line + 1, self.capital_column).type_id in [0, 1]:
                    self.add_units(0, 0, self.capital_line + 1, self.capital_column)
                elif Map.Map.get_tile(self.capital_line - 1, self.capital_column).type_id in [0, 1]:
                    self.add_units(0, 0, self.capital_line - 1, self.capital_column)
                elif Map.Map.get_tile(self.capital_line, self.capital_column + 1).type_id in [0, 1]:
                    self.add_units(0, 0, self.capital_line, self.capital_column + 1)
                elif Map.Map.get_tile(self.capital_line, self.capital_column - 1).type_id in [0, 1]:
                    self.add_units(0, 0, self.capital_line, self.capital_column - 1)
                else:
                    # this is pretty bad, as it's going to mean one of the units must be moved by player to settle
                    self.add_units(0, 0, self.capital_line, self.capital_column)
                return

    def add_resources(self):
        self.resources.science_count += self.resources_per_turn.science_per_turn_count
        self.resources.culture_count += self.resources_per_turn.culture_per_turn_count
        self.resources.gold_count += self.resources_per_turn.gold_per_turn_count

    def add_cities(self, city_name, city_line, city_column):
        self.cities.append(City.City(city_name, city_line, city_column))
        # if this is the first city placed, make it the capital and bring the player's starting camera position here
        if len(self.cities) == 1:
            self.cities[0].is_capital = True
            self.capital_line = city_line
            self.capital_column = city_column
        self.tiles.extend(self.cities[len(self.cities) - 1].tiles)

    def delete_city(self, city_line, city_column):
        for city in self.cities:
            if city.center_line_location == city_line and city.center_column_location == city_column:
                if city.is_capital:
                    # Player was defeated and is going to be removed
                    return 1
                self.cities.remove(city)
                return 0

    def add_units(self, unit_name_id, unit_type_id, unit_line, unit_column):
        self.units.append(Unit.Unit(unit_type_id, unit_name_id, unit_line, unit_column))

    def delete_units(self, location_line, location_column):
        for unit in self.units:
            if unit.position_line == location_line and unit.position_column == location_column:
                self.units.remove(unit)

    def end_turn_resource_calculation(self):
        self.resources_per_turn.reset_resources_per_turn()
        for city in self.cities:
            self.resources_per_turn += city.end_turn_update()

        self.add_resources()

    def is_city_owner(self, city_line, city_column):
        for city in self.cities:
            if city.center_line_location == city_line and city.center_column_location == city_column:
                return True
        return False

    def is_unit_owner(self, unit_line, unit_column):
        for unit in self.units:
            if unit.position_line == unit_line and unit.position_column == unit_column:
                return True
        return False

    def is_tile_owner(self, tile_line, tile_column):
        for tile in self.tiles:
            if tile.line == tile_line and tile.column == tile_column:
                return True
        return False

    def build_district_with_production(self, city_line, city_column, district_name_id,
                       district_location_line, district_location_column, players_list):
        for city in self.cities:
            if city.center_line_location == city_line and city.center_column_location == city_column:
                target_tile = Map.Map.get_tile(district_location_line, district_location_column)
                if target_tile not in city.tiles:
                    return False
                city.build_district_with_production(district_name_id, district_location_line, district_location_column)
                new_tiles = self.tiles + list(set(city.tiles) - set(self.tiles))
                for player in players_list:
                    if player.player_id != self.player_id:
                        new_tiles = list(set(new_tiles) - set(player.tiles))
                self.tiles = new_tiles

    def build_district_with_gold(self, city_line, city_column, district_name_id,
                       district_location_line, district_location_column, players_list):
        for city in self.cities:
            if city.center_line_location == city_line and city.center_column_location == city_column:
                target_tile = Map.Map.get_tile(district_location_line, district_location_column)
                if target_tile not in city.tiles:
                    return False
                city.add_district(district_name_id, district_location_line, district_location_column)
                new_tiles = self.tiles + list(set(city.tiles) - set(self.tiles))
                for player in players_list:
                    if player.player_id != self.player_id:
                        new_tiles = list(set(new_tiles) - set(player.tiles))
                self.tiles = new_tiles
                self.resources.gold_count -= City.district_cost * 2

    def build_building_with_production(self, city_line, city_column, district_type_id, building_name_id):
        for city in self.cities:
            if city.center_line_location == city_line and city.center_column_location == city_column:
                return city.build_building_with_production(building_name_id, district_type_id)

    def build_building_with_gold(self, city_line, city_column, district_type_id, building_name_id):
        if self.resources.gold_count == 0:
            return 1
        for city in self.cities:
            if city.center_line_location == city_line and city.center_column_location == city_column:
                district = city.get_district_by_type(district_type_id)
                if district.district_type == City.district_types[0]:
                    if self.resources.gold_count < City.campus_buildings_costs[building_name_id] * 2:
                        remaining_gold = City.campus_buildings_costs[building_name_id] * 2 - self.resources.gold_count
                        if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                        else:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
                    else:
                        self.resources.gold_count -= City.campus_buildings_costs[building_name_id] * 2
                elif district.district_type == City.district_types[1]:
                    if self.resources.gold_count < City.theatre_square_buildings_costs[building_name_id] * 2:
                        remaining_gold = (City.theatre_square_buildings_costs[building_name_id] * 2 -
                                          self.resources.gold_count)
                        if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                        else:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
                    else:
                        self.resources.gold_count -= City.theatre_square_buildings_costs[building_name_id] * 2
                elif district.district_type == City.district_types[2]:
                    if self.resources.gold_count < City.commercial_hub_buildings_costs[building_name_id] * 2:
                        remaining_gold = (City.commercial_hub_buildings_costs[building_name_id] * 2 -
                                          self.resources.gold_count)
                        if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                        else:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
                    else:
                        self.resources.gold_count -= City.commercial_hub_buildings_costs[building_name_id] * 2
                elif district.district_type == City.district_types[3]:
                    if self.resources.gold_count < City.harbour_buildings_costs[building_name_id] * 2:
                        remaining_gold = (City.harbour_buildings_costs[building_name_id] * 2 -
                                         self.resources.gold_count)
                        if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                        else:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
                    else:
                        self.resources.gold_count -= City.harbour_buildings_costs[building_name_id] * 2
                elif district.district_type == City.district_types[4]:
                    if self.resources.gold_count < City.industrial_zone_buildings_costs[building_name_id] * 2:
                        remaining_gold = (City.industrial_zone_buildings_costs[building_name_id] * 2 -
                                          self.resources.gold_count)
                        if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                        else:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                    else:
                        self.resources.gold_count -= City.industrial_zone_buildings_costs[building_name_id] * 2
                elif district.district_type == City.district_types[5]:
                    if self.resources.gold_count < City.neighborhood_buildings_costs[building_name_id] * 2:
                        remaining_gold = (City.neighborhood_buildings_costs[building_name_id] * 2 -
                                          self.resources.gold_count)
                        if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                        else:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
                    else:
                        self.resources.gold_count -= City.neighborhood_buildings_costs[building_name_id] * 2
                elif district.district_type == City.district_types[6]:
                    raise ValueError("No buildings for aqueducts")
                else:
                    if self.resources.gold_count < City.city_center_buildings_costs[building_name_id] * 2:
                        remaining_gold = (City.city_center_buildings_costs[building_name_id] * 2 -
                                          self.resources.gold_count)
                        if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count
                        else:
                            return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
                    else:
                        self.resources.gold_count -= City.city_center_buildings_costs[building_name_id] * 2
                district.add_building(building_name_id)
                return 0

    def build_unit_with_production(self, unit_line, unit_column, city_line, city_column, unit_type_id, unit_name_id):
        for city in self.cities:
            if city.center_line_location == city_line and city.center_column_location == city_column:
                ret_code = city.build_unit_with_production(unit_type_id, unit_name_id)
                if ret_code == 0:
                    self.add_units(unit_name_id, unit_type_id, unit_line, unit_column)
                return ret_code

    def build_unit_with_gold(self, unit_line, unit_column, unit_type_id, unit_name_id):
        if self.resources.gold_count == 0:
            return 1
        if unit_type_id == 0:
            if self.resources.gold_count < Unit.melee_units_costs[unit_name_id] * 2:
                remaining_gold = (Unit.melee_units_costs[unit_name_id] * 2 -
                                  self.resources.gold_count)
                if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count
                else:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
            else:
                self.resources.gold_count -= Unit.melee_units_costs[unit_name_id] * 2
        elif unit_type_id == 1:
            if self.resources.gold_count < Unit.ranged_units_costs[unit_name_id] * 2:
                remaining_gold = (Unit.ranged_units_costs[unit_name_id] * 2 -
                                  self.resources.gold_count)
                if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count
                else:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
            else:
                self.resources.gold_count -= Unit.ranged_units_costs[unit_name_id] * 2
        elif unit_type_id == 2:
            if self.resources.gold_count < Unit.cavalry_units_costs[unit_name_id] * 2:
                remaining_gold = (Unit.cavalry_units_costs[unit_name_id] * 2 -
                                  self.resources.gold_count)
                if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count
                else:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
            else:
                self.resources.gold_count -= Unit.cavalry_units_costs[unit_name_id] * 2
        elif unit_type_id == 3:
            if self.resources.gold_count < Unit.siege_units_costs[unit_name_id] * 2:
                remaining_gold = (Unit.siege_units_costs[unit_name_id] * 2 -
                                  self.resources.gold_count)
                if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count
                else:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
            else:
                self.resources.gold_count -= Unit.siege_units_costs[unit_name_id] * 2
        elif unit_type_id == 4:
            if self.resources.gold_count < Unit.naval_melee_units_costs[unit_name_id] * 2:
                remaining_gold = (Unit.naval_melee_units_costs[unit_name_id] * 2 -
                                  self.resources.gold_count)
                if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count
                else:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
            else:
                self.resources.gold_count -= Unit.naval_melee_units_costs[unit_name_id] * 2
        elif unit_type_id == 5:
            if self.resources.gold_count < Unit.naval_ranged_units_costs[unit_name_id] * 2:
                remaining_gold = (Unit.naval_ranged_units_costs[unit_name_id] * 2 -
                                  self.resources.gold_count)
                if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count
                else:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
            else:
                self.resources.gold_count -= Unit.naval_ranged_units_costs[unit_name_id] * 2
        elif unit_type_id == 6:
            if self.resources.gold_count < Unit.civilian_units_costs * 2:
                remaining_gold = (Unit.civilian_units_costs * 2 -
                                  self.resources.gold_count)
                if remaining_gold % self.resources_per_turn.gold_per_turn_count == 0:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count
                else:
                    return remaining_gold // self.resources_per_turn.gold_per_turn_count + 1
            else:
                self.resources.gold_count -= Unit.civilian_units_costs * 2
        self.add_units(unit_name_id, unit_type_id, unit_line, unit_column)
        return 0

    def move_unit(self, unit_position_line, unit_position_column, unit_new_line, unit_new_column):
        for unit in self.units:
            if unit.position_line == unit_position_line and unit.position_column == unit_position_column:
                return unit.move(unit_new_line, unit_new_column)

    def reset_units_movements(self):
        for unit in self.units:
            unit.reset_movement()

    def buy_tech(self, tech_id: int):
        for pred in self.tech_tree.G.predecessors(self.tech_tree.G[tech_id]):
            if not pred.owned:
                return -1
        if self.resources.science_count < self.tech_tree.G[tech_id].cost:
            remaining_science = self.resources.science_count - self.tech_tree.G[tech_id].cost
            if remaining_science % self.resources_per_turn.science_per_turn_count == 0:
                return remaining_science // self.resources_per_turn.science_per_turn_count
            else:
                return remaining_science // self.resources_per_turn.science_per_turn_count + 1
        else:
            self.resources.science_count -= self.tech_tree.G[tech_id].cost
        self.tech_tree.G[tech_id].owned = True
        return 0

    def buy_civic(self, civic_id: int):
        for pred in self.civic_tree.G.predecessors(self.civic_tree.G[civic_id]):
            if not pred.owned:
                return -1
        if self.resources.culture_count < self.civic_tree.G[civic_id].cost:
            remaining_culture = self.resources.culture_count - self.civic_tree.G[civic_id].cost
            if remaining_culture % self.resources_per_turn.culture_per_turn_count == 0:
                return remaining_culture // self.resources_per_turn.culture_per_turn_count
            else:
                return remaining_culture // self.resources_per_turn.culture_per_turn_count + 1
        else:
            self.resources.culture_count -= self.civic_tree.G[civic_id].cost
        self.civic_tree.G[civic_id].owned = True
        return 0
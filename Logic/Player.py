import Logic.City as City
import Logic.Resources as Resources
import Logic.Unit as Unit

# Holds information about a player
# @param player_id: the id of the player
# @param resources: the total resources owned by the player (not necessarily all ever earned)
# @param resources_per_turn: the amount of resources that should be earned by the player this turn
# to be updated at the start of the turn
class Player:
    player_count = 0
    def __init__(self):
        self.player_id = Player.player_count
        Player.player_count += 1

        self.resources = Resources.Resources(0, 0, 0)
        self.resources_per_turn = Resources.ResourcesPerTurn(0, 0, 0)
        self.cities = []
        self.units = []

    def add_resources(self):
        self.resources.science_count += self.resources_per_turn.science_per_turn_count
        self.resources.culture_count += self.resources_per_turn.culture_per_turn_count
        self.resources.gold_count += self.resources_per_turn.gold_per_turn_count

    def add_cities(self, city_name, city_line, city_column):
        self.cities.append(City.City(city_name, city_line, city_column))

    def end_turn(self):
        self.resources_per_turn.reset_resources_per_turn()
        for city in self.cities:
            self.resources_per_turn += city.end_turn_update()

        self.add_resources()

    def build_district(self, city_line, city_column, district_name_id,
                       district_location_line, district_location_column):
        for city in self.cities:
            if city.city_line == city_line and city.city_column == city_column:
                return city.build_district(district_name_id, district_location_line, district_location_column)

    def build_building_with_production(self, city_line, city_column, district_location_line, district_location_column,
                                       building_name_id):
        for city in self.cities:
            if city.city_line == city_line and city.city_column == city_column:
                return city.build_building_with_production(building_name_id, city.get_district_id(district_location_line,
                                                                                           district_location_column))

    def build_building_with_gold(self, city_line, city_column, district_location_line, district_location_column,
                                 building_name_id):
        for city in self.cities:
            if city.city_line == city_line and city.city_column == city_column:
                district = city.districts[city.get_district_id(district_location_line, district_location_column)]
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

    def build_unit_with_production(self, city_line, city_column, unit_type_id, unit_name_id):
        for city in self.cities:
            if city.city_line == city_line and city.city_column == city_column:
                return city.build_unit_with_production(unit_type_id, unit_name_id, self)

    def build_unit_with_gold(self, city_line, city_column, unit_type_id, unit_name_id):
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
        self.units.append(Unit.Unit(unit_name_id, unit_type_id, city_line, city_column))
        return 0

    def move_unit(self, unit_position_line, unit_position_column, unit_new_line, unit_new_column):
        for unit in self.units:
            if unit.position_line == unit_position_line and unit.position_column == unit_position_column:
                return unit.move(unit_new_line, unit_new_column)
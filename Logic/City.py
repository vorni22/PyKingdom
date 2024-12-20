import Logic.Resources as Resources
from Map_Generation import Map as Map
import Logic.Unit as Unit

district_types = ['Campus', 'Theatre Square', 'Commercial Hub', 'Harbour', 'Industrial Zone',
                  'Neighborhood', 'Aqueduct', 'City Center']

campus_buildings = ['Library', 'University']
theatre_square_buildings = ['Amphitheatre', 'Museum']
commercial_hub_buildings = ['Market', 'Bank']
harbour_buildings = ['Lighthouse', 'Shipyard']
industrial_zone_buildings = ['Workshop', 'Factory']
neighborhood_buildings = ['Food Market']
city_center_buildings = ['Palace', 'Monument', 'Granary', 'Water Mill', 'Sewer']

city_names = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "London", "Paris", "Berlin", "Madrid", "Rome",
    "Tokyo", "Osaka", "Seoul", "Shanghai", "Beijing",
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
    "Mexico City", "São Paulo", "Rio de Janeiro", "Buenos Aires", "Santiago",
    "Cairo", "Lagos", "Johannesburg", "Nairobi", "Casablanca",
    "Sydney", "Melbourne", "Brisbane", "Perth", "Auckland",
    "Moscow", "Saint Petersburg", "Istanbul", "Dubai", "Tehran",
    "Bangkok", "Kuala Lumpur", "Singapore", "Jakarta", "Manila",
    "Toronto", "Vancouver", "Montreal", "Lima", "Bogotá"
]

district_cost = 120

campus_buildings_costs = [80, 120]
theatre_square_buildings_costs = [80, 120]
commercial_hub_buildings_costs = [80, 120]
harbour_buildings_costs = [80, 120]
industrial_zone_buildings_costs = [80, 120]
neighborhood_buildings_costs = [100]
city_center_buildings_costs = [0, 40, 60, 60, 100]

# Holds information about a district
# @param district_type: what type of district is this one. Should be part of the district_types list
# @param buildings: list of buildings that have been built in this district. Buildings are specific to each district
# and a building of tier 2 requires a tier 1 building to be built first
# @param location_line: the line on which the district is situated
# @param location_column: the column on which the district is situated
class District:
    def __init__(self, district_type_id, location_line, location_column):
        self.district_type_id = district_type_id
        self.district_type = district_types[district_type_id]
        self.buildings = []
        self.location_line = location_line
        self.location_column = location_column

    def add_building(self, building_id):
        if self.district_type_id == 0:
            self.buildings.append(campus_buildings[building_id])
        elif self.district_type_id == 1:
            self.buildings.append(theatre_square_buildings[building_id])
        elif self.district_type_id == 2:
            self.buildings.append(commercial_hub_buildings[building_id])
        elif self.district_type_id == 3:
            self.buildings.append(harbour_buildings[building_id])
        elif self.district_type_id == 4:
            self.buildings.append(industrial_zone_buildings[building_id])
        elif self.district_type_id == 5:
            self.buildings.append(neighborhood_buildings[building_id])
        elif self.district_type_id == 6:
            raise TypeError("Invalid building type: Aqueducts have no buildings")
        elif self.district_type_id == 7:
            self.buildings.append(city_center_buildings[building_id])


    def calculate_yields(self):
        resources = Resources.ResourcesPerTurn(0, 0, 0)
        city_resources = Resources.CityResourcesPerTurn(0, 0)

        if self.district_type == district_types[0]:
            if len(self.buildings) == 0:
                resources.science_per_turn_count += 2
            elif len(self.buildings) == 1:
                resources.science_per_turn_count += 4
            else:
                resources.science_per_turn_count += 8
        elif self.district_type == district_types[1]:
            if len(self.buildings) == 0:
                resources.culture_per_turn_count += 2
            elif len(self.buildings) == 1:
                resources.culture_per_turn_count += 4
            else:
                resources.culture_per_turn_count += 8
        elif self.district_type == district_types[2]:
            if len(self.buildings) == 0:
                resources.gold_per_turn_count += 4
            elif len(self.buildings) == 1:
                resources.gold_per_turn_count += 8
            else:
                resources.gold_per_turn_count += 16
        elif self.district_type == district_types[3]:
            if len(self.buildings) == 0:
                resources.gold_per_turn_count += 2
                city_resources.food_per_turn_count += 1
            elif len(self.buildings) == 1:
                resources.gold_per_turn_count += 4
                city_resources.food_per_turn_count += 1
                city_resources.production_per_turn_count += 2
            else:
                resources.gold_per_turn_count += 16
                city_resources.food_per_turn_count += 1
                city_resources.production_per_turn_count += 2
        elif self.district_type == district_types[4]:
            if len(self.buildings) == 0:
                city_resources.production_per_turn_count += 2
            elif len(self.buildings) == 1:
                city_resources.production_per_turn_count += 4
            else:
                city_resources.production_per_turn_count += 8
        elif self.district_type == district_types[5]:
            if len(self.buildings) == 1:
                city_resources.food_per_turn_count += 4
        elif self.district_type == district_types[7]:
            if city_center_buildings[0] in self.buildings:
                resources.gold_per_turn_count += 5
                resources.science_per_turn_count += 2.5
                resources.culture_per_turn_count += 1.25
            if city_center_buildings[1] in self.buildings:
                resources.culture_per_turn_count += 2
            if city_center_buildings[2] in self.buildings:
                city_resources.food_per_turn_count += 1
            if city_center_buildings[3] in self.buildings:
                city_resources.food_per_turn_count += 3
                city_resources.production_per_turn_count += 1
        return resources, city_resources


# Holds information about a city
# @param city_name: the name of the city
# @param districts: list of districts built in the city. Each city starts with the city center and
# can only build one of each district, except for neighborhoods
# @param housing: shows how many people the city can hold. Going beyond is possible, but heavily punished
# @param population: shows how many people the city holds. Population determines how many tiles are worked
# @param city_resources: food and production the city accumulated
# @param city_resources_per_turn: food and production the city should earn this turn
# @param resources_per_turn: science, culture and gold that the player gains from this city this turn
# @param center_line_location: the line of the map on which the city center is located
# @param center_column_location: the column of the map on which the city center is located
class City:
    def __init__(self, city_name, center_line_location, center_column_location):
        self.city_name = city_name
        self.districts = [District(7, center_line_location, center_column_location)]
        self.districts[0].add_building(0)
        self.housing = 3
        self.population = 1
        self.tiles = [Map.Map.get_tile(center_line_location, center_column_location)]
        self.add_tiles(center_line_location, center_column_location)
        self.city_resources = Resources.CityResources(0, 0)
        self.city_resources_per_turn = Resources.CityResourcesPerTurn(0, 0)
        self.resources_per_turn = Resources.ResourcesPerTurn(0, 0, 0)
        self.center_line_location = center_line_location
        self.center_column_location = center_column_location
        self.health_percentage = 100
        self.melee_combat_strength = 15
        self.is_capital = False

    def add_tiles(self, line, column):
        ref = Map.Map.get_tile(line, column - 1)
        if ref not in self.tiles:
            self.tiles.append(ref)
        ref = Map.Map.get_tile(line, column + 1)
        if ref not in self.tiles:
            self.tiles.append(ref)
        ref = Map.Map.get_tile(line + 1, column)
        if ref not in self.tiles:
            self.tiles.append(ref)
        ref = Map.Map.get_tile(line - 1, column)
        if ref not in self.tiles:
            self.tiles.append(ref)
        if line % 2:
            ref = Map.Map.get_tile(line + 1, column + 1)
            if ref not in self.tiles:
                self.tiles.append(ref)
            ref = Map.Map.get_tile(line - 1, column + 1)
            if ref not in self.tiles:
                self.tiles.append(ref)
        else:
            ref = Map.Map.get_tile(line + 1, column - 1)
            if ref not in self.tiles:
                self.tiles.append(ref)
            ref = Map.Map.get_tile(line - 1, column - 1)
            if ref not in self.tiles:
                self.tiles.append(ref)

    def add_district(self, district_type_id, location_line, location_column):
        self.districts.append(District(district_type_id, location_line, location_column))
        self.add_tiles(location_line, location_column)
        self.melee_combat_strength += 5

    def get_district_by_type(self, district_type_id) -> District | None:
        for district in self.districts:
            if district.district_type_id == district_type_id:
                return district
        return None

    def get_district_id(self, district_location_line, district_location_column):
        for i, district in enumerate(self.districts):
            if (district.location_line == district_location_line and
                    district.location_column == district_location_column):
                return i

    def calculate_yields_districts(self):
        total_resources_per_turn = Resources.ResourcesPerTurn(0, 0, 0)
        total_city_resources_per_turn = Resources.CityResourcesPerTurn(0, 0)
        self.housing = 3
        for district in self.districts:
            resources, city_resources = district.calculate_yields()
            total_resources_per_turn += resources
            total_city_resources_per_turn += city_resources
            if district.district_type == district_types[5]:
                self.housing += 5
            if district.district_type == district_types[6]:
                self.housing += 2
            if district.district_type == district_types[7]:
                if city_center_buildings[2] in district.buildings:
                    self.housing += 2
                if city_center_buildings[4] in district.buildings:
                    self.housing += 4
        return total_resources_per_turn, total_city_resources_per_turn

    def calculate_yields_tiles(self):
        total_resources_per_turn = Resources.ResourcesPerTurn(0, 0, 0)
        total_city_resources_per_turn = Resources.CityResourcesPerTurn(0, 0)
        for tile in self.tiles:
            total_resources_per_turn += tile.resources
            total_city_resources_per_turn += tile.city_resources
        return total_resources_per_turn, total_city_resources_per_turn

    def end_turn_update(self):
        self.resources_per_turn, self.city_resources_per_turn = self.calculate_yields_tiles()
        temp_resources_per_turn, temp_city_resources_per_turn = self.calculate_yields_districts()
        self.resources_per_turn += temp_resources_per_turn
        self.city_resources_per_turn += temp_city_resources_per_turn

        self.resources_per_turn += Resources.ResourcesPerTurn(self.population, self.population, self.population)

        if self.housing - self.population == 1:
            self.city_resources_per_turn.food_per_turn_count *= 0.75
        elif self.housing - self.population == 0:
            self.city_resources_per_turn.food_per_turn_count *= 0.5
        elif self.housing - self.population < 0:
            self.city_resources_per_turn.food_per_turn_count *= 0.15
        if district_types[6] in self.districts:
            self.city_resources_per_turn.food_per_turn_count *= 1.25

        self.city_resources.food_count += self.city_resources_per_turn.food_per_turn_count
        self.city_resources_per_turn.production_per_turn_count += self.city_resources_per_turn.production_per_turn_count

        self.health_percentage = min(100, self.health_percentage + 20)

        return self.resources_per_turn

    def health_strength_loss(self):
        return 0.1 * (100 - self.health_percentage)

    def melee_combat(self, unit):
        diff = (self.melee_combat_strength - self.health_strength_loss() -
                unit.melee_combat_strength - unit.health_strength_loss())

        if diff > 0:
            self.health_percentage -= 0.4 * diff - 3
        else:
            self.health_percentage -= 2.5 * (-diff) - 5

    def ranged_combat(self, unit):
        diff = (self.melee_combat_strength + 10 - self.health_strength_loss() -
                unit.ranged_combat_strength + unit.health_strength_loss())
        if unit.type == Unit.unit_classes[3]:
            diff -= 10

        if diff > 0:
            self.health_percentage -= 0.4 * diff - 3
        else:
            self.health_percentage -= 2.5 * (-diff) - 5

    def build_district_with_production(self, district_type_id, district_location_line, district_location_column):
        self.add_district(district_type_id, district_location_line, district_location_column)
        self.city_resources.production_count -= district_cost

    def build_building_with_production(self, building_name_id, district_type_id):
        district = self.get_district_by_type(district_type_id)
        if district.district_type_id == 0:
            if self.city_resources.production_count < campus_buildings_costs[building_name_id]:
                remaining_production = self.city_resources.production_count - campus_buildings_costs[building_name_id]
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= campus_buildings_costs[building_name_id]
        elif district.district_type_id == 1:
            if self.city_resources.production_count < theatre_square_buildings_costs[building_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        theatre_square_buildings_costs[building_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= theatre_square_buildings_costs[building_name_id]
        elif district.district_type_id == 2:
            if self.city_resources.production_count < commercial_hub_buildings_costs[building_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        commercial_hub_buildings_costs[building_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= commercial_hub_buildings_costs[building_name_id]
        elif district.district_type_id == 3:
            if self.city_resources.production_count < harbour_buildings_costs[building_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        harbour_buildings_costs[building_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= harbour_buildings_costs[building_name_id]
        elif district.district_type_id == 4:
            if self.city_resources.production_count < industrial_zone_buildings_costs[building_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        industrial_zone_buildings_costs[building_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= industrial_zone_buildings_costs[building_name_id]
        elif district.district_type_id == 5:
            if self.city_resources.production_count < neighborhood_buildings_costs[building_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        neighborhood_buildings_costs[building_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= neighborhood_buildings_costs[building_name_id]
        elif district.district_type_id == 6:
            raise ValueError('Aqueducts do not have buildings')
        elif district.district_type_id == 7:
            if self.city_resources.production_count < city_center_buildings_costs[building_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        city_center_buildings_costs[building_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= city_center_buildings_costs[building_name_id]

        district.add_building(building_name_id)
        return 0

    def build_unit_with_production(self, unit_type_id, unit_name_id):
        if unit_type_id == 0:
            if self.city_resources.production_count < Unit.melee_units_costs[unit_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        Unit.melee_units_costs[unit_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= Unit.melee_units_costs[unit_name_id]
        elif unit_type_id == 1:
            if self.city_resources.production_count < Unit.ranged_units_costs[unit_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        Unit.ranged_units_costs[unit_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= Unit.ranged_units_costs[unit_name_id]
        elif unit_type_id == 2:
            if self.city_resources.production_count < Unit.cavalry_units_costs[unit_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        Unit.cavalry_units_costs[unit_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= Unit.cavalry_units_costs[unit_name_id]
        elif unit_type_id == 3:
            if self.city_resources.production_count < Unit.siege_units_costs[unit_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        Unit.siege_units_costs[unit_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= Unit.siege_units_costs[unit_name_id]
        elif unit_type_id == 4:
            if self.city_resources.production_count < Unit.naval_melee_units_costs[unit_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        Unit.naval_melee_units_costs[unit_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= Unit.naval_melee_units_costs[unit_name_id]
        elif unit_type_id == 5:
            if self.city_resources.production_count < Unit.ranged_units_costs[unit_name_id]:
                remaining_production = (self.city_resources.production_count -
                                        Unit.ranged_units_costs[unit_name_id])
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= Unit.naval_ranged_units_costs[unit_name_id]
        elif unit_type_id == 6:
            if self.city_resources.production_count < Unit.civilian_units_costs:
                remaining_production = (self.city_resources.production_count -
                                        Unit.civilian_units_costs)
                if remaining_production % self.city_resources_per_turn.production_per_turn_count == 0:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count
                else:
                    return remaining_production // self.city_resources_per_turn.production_per_turn_count + 1
            else:
                self.city_resources.production_count -= Unit.civilian_units_costs

        return 0

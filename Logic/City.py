import Resources
from Map_Generation import Map as Map

district_types = ['Campus', 'Theatre Square', 'Commercial Hub', 'Harbour', 'Industrial Zone',
                  'Neighborhood', 'Aqueduct', 'City Center']

campus_buildings = ['Library', 'University']
theatre_square_buildings = ['Amphitheatre', 'Museum']
commercial_hub_buildings = ['Market', 'Bank']
harbour_buildings = ['Lighthouse', 'Shipyard']
industrial_zone_buildings = ['Workshop', 'Factory']
neighborhood_buildings = ['Food Market']
city_center_buildings = ['Palace', 'Monument', 'Granary', 'Water Mill', 'Sewer']

# Holds information about a district
# @param district_type: what type of district is this one. Should be part of the district_types list
# @param buildings: list of buildings that have been built in this district. Buildings are specific to each district
# and a building of tier 2 requires a tier 1 building to be built first
class District:
    def __init__(self, district_type, location_line, location_column):
        if district_type not in district_types:
            raise TypeError("Invalid district type")
        self.district_type = district_type
        self.buildings = []
        self.location_line = location_line
        self.location_column = location_column

    def add_building(self, building_id):
        if self.district_type == district_types[0]:
            self.buildings.append(campus_buildings[building_id])
        elif self.district_type == district_types[1]:
            self.buildings.append(theatre_square_buildings[building_id])
        elif self.district_type == district_types[2]:
            self.buildings.append(commercial_hub_buildings[building_id])
        elif self.district_type == district_types[3]:
            self.buildings.append(harbour_buildings[building_id])
        elif self.district_type == district_types[4]:
            self.buildings.append(industrial_zone_buildings[building_id])
        elif self.district_type == district_types[5]:
            self.buildings.append(neighborhood_buildings[building_id])
        elif self.district_type == district_types[6]:
            raise TypeError("Invalid building type: Aqueducts have no buildings")
        elif self.district_type == district_types[7]:
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
# @param center_line_location: the line of the map on which the city center is located
# @param center_column_location: the column of the map on which the city center is located
class City:
    def __init__(self, city_name, center_line_location, center_column_location):
        self.city_name = city_name
        self.districts = [District(district_types[7], center_line_location, center_column_location)]
        self.housing = 3
        self.population = 1
        self.tiles = [Map.Map.get_tile(center_line_location, center_column_location)]
        self.add_tiles(center_line_location, center_column_location)
        self.city_resources = Resources.CityResources(0, 0)
        self.city_resources_per_turn = Resources.CityResourcesPerTurn(0, 0)
        self.resources_per_turn = Resources.ResourcesPerTurn(0, 0, 0)
        self.center_line_location = center_line_location
        self.center_column_location = center_column_location

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
            ref = Map.Map.get_tile(line + 1, column - 1)
            if ref not in self.tiles:
                self.tiles.append(ref)
            ref = Map.Map.get_tile(line - 1, column - 1)
            if ref not in self.tiles:
                self.tiles.append(ref)
        else:
            ref = Map.Map.get_tile(line + 1, column + 1)
            if ref not in self.tiles:
                self.tiles.append(ref)
            ref = Map.Map.get_tile(line - 1, column + 1)
            if ref not in self.tiles:
                self.tiles.append(ref)

    def add_district(self, district_name_id, location_line, location_column):
        if district_types[district_name_id] in self.districts and district_name_id != 5:
            raise ValueError("Can only build one district of this type in a city")
        self.districts.append(District(district_types[district_name_id], location_line, location_column))
        self.add_tiles(location_line, location_column)

    def add_building(self, building_name_id, district_id):
        self.districts[district_id].add_building(building_name_id)

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


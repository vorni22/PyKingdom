import Resources

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
    def __init__(self, district_type):
        if district_type not in district_types:
            raise TypeError("Invalid district type")
        self.district_type = district_type
        self.buildings = []

    def add_building(self, building):
        if self.district_type == district_types[0]:
            if building not in campus_buildings:
                raise TypeError("Invalid building type")
        elif self.district_type == district_types[1]:
            if building not in theatre_square_buildings:
                raise TypeError("Invalid building type")
        elif self.district_type == district_types[2]:
            if building not in commercial_hub_buildings:
                raise TypeError("Invalid building type")
        elif self.district_type == district_types[3]:
            if building not in harbour_buildings:
                raise TypeError("Invalid building type")
        elif self.district_type == district_types[4]:
            if building not in industrial_zone_buildings:
                raise TypeError("Invalid building type")
        elif self.district_type == district_types[5]:
            if building not in neighborhood_buildings:
                raise TypeError("Invalid building type")
        elif self.district_type == district_types[6]:
            raise TypeError("Invalid building type: Aqueducts have no buildings")
        elif self.district_type == district_types[7]:
            if building not in city_center_buildings:
                raise TypeError("Invalid building type")

        if building == campus_buildings[1] and len(self.buildings) == 0:
            raise ValueError("Tier 1 building must be built first")
        elif building == theatre_square_buildings[1] and len(self.buildings) == 0:
            raise ValueError("Tier 1 building must be built first")
        elif building == commercial_hub_buildings[1] and len(self.buildings) == 0:
            raise ValueError("Tier 1 building must be built first")
        elif building == harbour_buildings[1] and len(self.buildings) == 0:
            raise ValueError("Tier 1 building must be built first")
        elif building == industrial_zone_buildings[1] and len(self.buildings) == 0:
            raise ValueError("Tier 1 building must be built first")

        self.buildings.append(building)

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
class City:
    def __init__(self, city_name):
        self.city_name = city_name
        self.districts = [District(district_types[7])]
        self.housing = 3
        self.population = 1
        self.city_resources = Resources.CityResources(0, 0)
        self.city_resources_per_turn = Resources.CityResourcesPerTurn(0, 0)

    def add_district(self, district_name_id):
        if district_types[district_name_id] in self.districts and district_name_id != 5:
            raise ValueError("Can only build one district of this type in a city")
        self.districts.append(District(district_types[district_name_id]))

    def add_building(self, building_name, district_id):
        self.districts[district_id].add_building(building_name)

    def calculate_yields_districts(self):
        total_resources_per_turn = Resources.ResourcesPerTurn(0, 0, 0)
        total_city_resources_per_turn = Resources.CityResourcesPerTurn(0, 0)
        self.housing = 3
        has_aqueduct = False
        for district in self.districts:
            resources, city_resources = district.calculate_yields()
            total_resources_per_turn += resources
            total_city_resources_per_turn += city_resources
            if district.district_type == district_types[5]:
                self.housing += 5
            if district.district_type == district_types[6]:
                self.housing += 2
                has_aqueduct = True
            if district.district_type == district_types[7]:
                if city_center_buildings[2] in district.buildings:
                    self.housing += 2
                if city_center_buildings[4] in district.buildings:
                    self.housing += 4
        if self.housing - self.population == 1:
            total_city_resources_per_turn.food_per_turn_count *= 0.75
        elif self.housing - self.population == 0:
            total_city_resources_per_turn.food_per_turn_count *= 0.5
        elif self.housing - self.population < 0:
            total_city_resources_per_turn.food_per_turn_count *= 0.15
        if has_aqueduct:
            total_city_resources_per_turn.food_per_turn_count *= 1.25
        return total_resources_per_turn, total_city_resources_per_turn


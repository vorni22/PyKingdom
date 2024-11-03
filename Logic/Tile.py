import Logic.Resources as Resources

tile_types = ['Plains', 'Grassland', 'Shallow Water', 'Ocean', 'Mountain', 'Tundra', None]
tile_basic_resources = ['Banana', 'Wheat', 'Rice', 'Maize', 'Stone', 'Fish', 'Crabs', None]
tile_features = ['Woods', 'Rainforests', 'Marsh', 'Coral Reef', None]
tile_strategic_resources = ['Horses', 'Iron', 'Niter', 'Coal', None]
tile_luxury_resources = ['Mercury', 'Silk', 'Cocoa', 'Turtles', 'Coffee', 'Ivory', 'Furs', None]

# Holds information about a tile on the map
# @param line: the line on the map on which the tile is situated
# @param column: the column on the map on which te tile is situated
# @param type: the type of tile this tile is. Tiles can be Ocean, Shallow Water, Grassland, Plains or Mountains
# depending on their altitude (increasing in this order). Mountains may not have features or resources. Fish, Crabs,
# Whales and Coral Reefs may be found only on shallow water tiles. Every other resource or feature may only be found
# on grassland or plains tiles (equal chances)
# @param basic_resource: the basic resource on the tile (if the tile has one) only one of basic, strategic or luxury
# resources can be present on a tile
# @param strategic_resource: the strategic resource on the tile (if the tile has one) only one of basic, strategic or
# luxury resources can be present on a tile
# @param luxury: the luxury resource on the tile (if the tile has one) only one of basic, strategic or luxury
# resources can be present on a tile
# @param feature: the feature of the tile (if the tile has one). A tile can have both a resource and a feature
# @param resources: how much science, culture and gold the tile yields to the player when worked
# @param city_resources: how much food and production the tile yields to the city when worked
# @param movement_cost: how much movement must a unit have remaining to be able to move to this tile.
# The first move of a unit is special and ignores this cost
# Mountains may never be passed - equivalent to having infinite movement cost
class Tile:
    def __init__(self, line, column, type_id, basic_resource_id, feature_id, strategic_resource_id, luxury_resource_id):
        self.line = line
        self.column = column
        self.type = tile_types[type_id]
        self.basic_resource = tile_basic_resources[basic_resource_id]
        self.feature = tile_features[feature_id]
        self.strategic_resource = tile_strategic_resources[strategic_resource_id]
        self.luxury_resource = tile_luxury_resources[luxury_resource_id]
        self.resources = Resources.ResourcesPerTurn(0, 0, 0)
        self.city_resources = Resources.CityResourcesPerTurn(0, 0)
        self.movement_cost = 1
        self.calculate_tile_yields()

    def calculate_tile_yields(self):
        if self.type == tile_types[0]:
            self.city_resources.food_per_turn_count += 1
            self.city_resources.production_per_turn_count += 1
        elif self.type == tile_types[1]:
            self.city_resources.food_per_turn_count += 2
        elif self.type == tile_types[2]:
            self.city_resources.food_per_turn_count += 1
            self.resources.gold_per_turn_count += 1
        elif self.type == tile_types[3]:
            self.city_resources.food_per_turn_count += 1
        elif self.type == tile_types[4]:
            self.city_resources.production_per_turn_count += 2
            self.movement_cost = "Unpassable"
        elif self.type == tile_types[5]:
            raise TypeError("Tile must have a type")

        if self.basic_resource == tile_basic_resources[0]:
            self.city_resources.food_per_turn_count += 1
        elif self.basic_resource == tile_basic_resources[1]:
            self.city_resources.food_per_turn_count += 1
        elif self.basic_resource == tile_basic_resources[2]:
            self.city_resources.food_per_turn_count += 1
        elif self.basic_resource == tile_basic_resources[3]:
            self.resources.gold_per_turn_count += 2
        elif self.basic_resource == tile_basic_resources[4]:
            self.city_resources.production_per_turn_count += 1
        elif self.basic_resource == tile_basic_resources[5]:
            self.city_resources.food_per_turn_count += 1
        elif self.basic_resource == tile_basic_resources[6]:
            self.resources.gold_per_turn_count += 2

        if self.strategic_resource == tile_strategic_resources[0]:
            self.city_resources.food_per_turn_count += 1
            self.city_resources.production_per_turn_count += 1
        elif self.strategic_resource == tile_strategic_resources[1]:
            self.resources.science_per_turn_count += 1
        elif self.strategic_resource == tile_strategic_resources[2]:
            self.city_resources.food_per_turn_count += 1
            self.city_resources.production_per_turn_count += 1
        elif self.strategic_resource == tile_strategic_resources[3]:
            self.city_resources.production_per_turn_count += 2

        if self.luxury_resource == tile_luxury_resources[0]:
            self.resources.science_per_turn_count += 1
        elif self.basic_resource == tile_luxury_resources[1]:
            self.resources.culture_per_turn_count += 1
        elif self.basic_resource == tile_luxury_resources[2]:
            self.resources.gold_per_turn_count += 3
        elif self.basic_resource == tile_luxury_resources[3]:
            self.resources.science_per_turn_count += 1
        elif self.basic_resource == tile_luxury_resources[4]:
            self.resources.culture_per_turn_count += 1
        elif self.basic_resource == tile_luxury_resources[5]:
            self.resources.gold_per_turn_count += 1
            self.city_resources.production_per_turn_count += 1
        elif self.basic_resource == tile_luxury_resources[6]:
            self.resources.gold_per_turn_count += 1
            self.city_resources.food_per_turn_count += 1

        if self.feature == tile_features[0]:
            self.city_resources.production_per_turn_count += 1
            self.movement_cost = 2
        elif self.feature == tile_features[1]:
            self.city_resources.food_per_turn_count += 1
            self.movement_cost = 2
        elif self.feature == tile_features[2]:
            self.city_resources.food_per_turn_count += 1
            self.movement_cost = 2
        elif self.feature == tile_features[3]:
            self.resources.science_per_turn_count += 1


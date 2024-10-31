# Holds information about total resources owned by the player at any given point
# @param science_count: total amount of science the player has
# @param culture_count: total amount of culture the player has
# @param gold_count: total amount of gold the player has
class Resources:
    def __init__(self, science_count, culture_count, gold_count):
        self.science_count = science_count
        self.culture_count = culture_count
        self.gold_count = gold_count

    def __iadd__(self, other):
        self.science_count += other.science_count
        self.culture_count += other.culture_count
        self.gold_count += other.gold_count

# Holds information about resources that should be gained by the player this turn
# @param science_per_turn_count science that should be gained this turn
# @param culture_per_turn_count culture that should be gained this turn
# @param gold_per_turn_count gold that should be gained this turn
class ResourcesPerTurn:
    def __init__(self, science_per_turn_count, culture_per_turn_count, gold_per_turn_count):
        self.science_per_turn_count = science_per_turn_count
        self.culture_per_turn_count = culture_per_turn_count
        self.gold_per_turn_count = gold_per_turn_count

    def reset_resources_per_turn(self):
        self.science_per_turn_count = 0
        self.culture_per_turn_count = 0
        self.gold_per_turn_count = 0

    def __iadd__(self, other):
        self.science_per_turn_count += other.science_per_turn_count
        self.culture_per_turn_count += other.culture_per_turn_count
        self.gold_per_turn_count += other.gold_per_turn_count

# Holds information about the city-specific resources held by this city
# @param production_count: total production the city accumulated
# @param food_count: total food the city accumulated
class CityResources:
    def __init__(self, production_count, food_count):
        self.production_count = production_count
        self.food_count = food_count

    def __iadd__(self, other):
        self.production_count += other.production_count
        self.food_count += other.food_count

# Holds information about the city-specific resources that should be gained by the city this turn
# @param production_per_turn_count: production the city should earn this turn
# @param food_per_turn_count: food the city should earn this turn
class CityResourcesPerTurn:
    def __init__(self, production_per_turn_count, food_per_turn_count):
        self.production_per_turn_count = production_per_turn_count
        self.food_per_turn_count = food_per_turn_count

    def __iadd__(self, other):
        self.production_per_turn_count += other.production_per_turn_count
        self.food_per_turn_count += other.food_per_turn_count

import Logic.City as City
import Logic.Resources as Resources

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
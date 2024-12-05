import Logic.Player as Player
import Logic.City as City
import Logic.Resources as Resources
import Logic.Unit as Unit
import Logic.Tech as Tech
import Logic.Civic as Civic
import Map_Generation.Map as Map

class Game:
    def __init__(self, player_count, map_size_lines, map_size_columns):
        Map.Map.init_map(map_size_lines, map_size_columns)
        self.player_count = player_count
        self.players = []
        self.cities_coordinates = []
        self.units_coordinates = []
        while Player.Player.player_count < player_count:
            self.players.append(Player.Player())

    def identify_object(self, tile_line, tile_column):
        if (tile_line, tile_column) in self.units_coordinates:
            return 1
        elif (tile_line, tile_column) in self.cities_coordinates:
            return 2
        else:
            return 0

    def is_owner(self, object_id, player_id, tile_line, tile_column):
        if object_id == 1:
            return self.players[player_id].is_unit_owner(tile_line, tile_column)
        elif object_id == 2:
            return self.players[player_id].is_city_owner(tile_line, tile_column)
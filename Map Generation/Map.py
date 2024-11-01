import Logic.Tile

# Holds information about the map. Should be generated once using init_map, then information should be accessed directly
# from the class container via get_tile
# @param lines: the number of lines the map has
# @param columns: the number of columns the map has
# @param tiles: 2d list of tiles. Tiles are generated using the init_tiles once, and then remained stored in the Map
# class, which acts as a singleton container for all the map related information

class Map:
    lines = 0
    columns = 0
    tiles = []

    @staticmethod
    def init_map(lines, columns):
        Map.lines = lines
        Map.columns = columns
        Map.init_tiles()

    @staticmethod
    def init_tiles():
        # TODO Add implementation for map tiles generation, type attribution, resource and feature distribution, to be
        #  done after the map heights distribution
        pass

    @staticmethod
    def get_tile(line, column):
        return Map.tiles[line][column]
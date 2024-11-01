import Logic.Tile

class Map:
    def __init__(self, lines, columns):
        self.lines = lines
        self.columns = columns
        self.tiles = []
        self.init_tiles()

    def init_tiles(self):
        # TODO Add implementation for map tiles generation, type attribution, resource and feature distribution, to be
        #  done after the map heights distribution
        pass

    def get_tile(self, line, column):
        return self.tiles[line][column]
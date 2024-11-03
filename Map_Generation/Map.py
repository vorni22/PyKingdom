# from Logic.Tile import Tile as tile
import networkx as nx
import numpy as np

# Holds information about the map. Should be generated once using init_map, then information should be accessed directly
# from the class container via get_tile
# @param lines: the number of lines the map has
# @param columns: the number of columns the map has
# @param tiles: 2d list of tiles. Tiles are generated using the init_tiles once, and then remained stored in the Map
# class, which acts as a singleton container for all the map related information
# @param G: Graph containing the entire map, where each node is a tile and the edges are the traversal costs
# @param shortest_distances: vector of dictionaries, each dictionary shortest_distances[u] contains a pair v:distance,
# meaning that the shortest distance from u to v is distance. The distance from u to v may be different from the
# distance between v to u.

class Map:
    lines = 0
    columns = 0
    tiles = []
    G = nx.DiGraph()
    shortest_distances = []

    @staticmethod
    def init_map(lines, columns):
        Map.lines = lines
        Map.columns = columns
        Map.init_tiles()
        Map.init_graph()

    @staticmethod
    def init_tiles():
        # TODO Add implementation for map tiles generation, type attribution, resource and feature distribution, to be
        #  done after the map heights distribution
        pass

    @staticmethod
    def init_graph():
        for i, j in np.ndindex(Map.lines, Map.columns):
            if j > 0:
                Map.G.add_edge(i * Map.columns + j, i * Map.columns + j - 1, weight=1)
            if j < Map.columns - 1:
                Map.G.add_edge(i * Map.columns + j, i * Map.columns + j + 1, weight=1)
            if i < Map.lines - 1:
                Map.G.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j, weight=1)
            if i > 0:
                Map.G.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j, weight=1)
            if i % 2:
                if i < Map.lines - 1 and j < Map.columns - 1:
                    Map.G.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j + 1, weight=1)
                if i > 0 and j < Map.columns - 1:
                    Map.G.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j + 1, weight=1)
            else:
                if i < Map.lines - 1 and j > 0:
                    Map.G.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j - 1, weight=1)
                if i > 0 and j > 0:
                    Map.G.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j - 1, weight=1)
        for i in range(0, Map.lines * Map.columns):
            Map.shortest_distances.append(nx.single_source_dijkstra_path_length(Map.G, i))
    @staticmethod
    def get_shortest_distance(start_line, start_col, end_line, end_col):
        return Map.shortest_distances[start_line * Map.columns + start_col][end_line * Map.columns + end_col]

    @staticmethod
    def get_tile(line, column):
        return Map.tiles[line][column]
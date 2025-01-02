from typing import Optional

import networkx as nx
import numpy as np


import Logic.Tile as Tile
# Holds information about the map. Should be generated once using init_map, then information should be accessed directly
# from the class container via get_tile
# @param lines: the number of lines the map has
# @param columns: the number of columns the map has
# @param tiles: list of tiles. Tiles are generated using the init_tiles once, and then remained stored in the Map
# class, which acts as a singleton container for all the map related information
# @param G: Graph containing the entire map, where each node is a tile and the edges are the connections between tiles
# @param shortest_distances: vector of dictionaries, each dictionary shortest_distances[u] contains a pair v:distance,
# which represents the distance in tiles, not accounting for actual movement cost
# @param G_unit_distance: Graph containing the entire map, where each node is a tile and the edges are distances between
# tiles
# @param unit_shortest_distances: vector of dictionaries, each dictionary unit_shortest_distances[u] contains a pair
# v:distance, which represents the distance which a unit needs to traverse to get from u to v. Note that this isn't
# symmetric, unit_shortest_distances[u][v] may be different from unit_shortest_distances[v][u]
# Movement cost to mountains, as well as movement cost from land to water and vice versa is infinite,
# meaning that passing is impossible
# @param unit_shortest_paths: list of all the shortest paths on the map. unit_shortest_paths[v] holds a dictionary,
# where each element unit_shortest_paths[v][u] represents a list of all nodes (tile coordinates) on the shortest path
# from u to v. The paths keep in mind the movement cost of each tile.
class Map:
    lines = 0
    columns = 0
    tiles = []
    tile_first_init = False
    G = nx.DiGraph()
    G_unit_distance = nx.DiGraph()
    shortest_distances = []
    unit_shortest_distances = []
    unit_shortest_paths = []

    @staticmethod
    def init_map(lines, columns, map_interface):
        Map.lines = lines
        Map.columns = columns
        Map.init_tiles(map_interface)
        Map.init_graph()
        Map.init_unit_graph()

    @staticmethod
    def update_tile(map_interface, map_interface_id):
        if not Map.tile_first_init:
            return

        column = map_interface_id // Map.lines
        line = map_interface_id % Map.lines
        this_map_id = line * Map.columns + column

        resource_name = map_interface.builder.resource_type[map_interface_id]

        tile_basic_resources_id = -1
        if resource_name in Tile.tile_basic_resources:
            tile_basic_resources_id = Tile.tile_basic_resources.index(resource_name)

        tile_features_id = -1
        if resource_name in Tile.tile_features:
            tile_features_id = Tile.tile_features.index(resource_name)

        tile_strategic_resources_id = -1
        if resource_name in Tile.tile_strategic_resources:
            tile_strategic_resources_id = Tile.tile_strategic_resources.index(resource_name)

        tile_luxury_resources_id = -1
        if resource_name in Tile.tile_luxury_resources:
            tile_luxury_resources_id = Tile.tile_luxury_resources.index(resource_name)

        tile = Tile.Tile(line, column,
                         map_interface.builder.types[map_interface_id],
                         tile_basic_resources_id,
                         tile_features_id,
                         tile_strategic_resources_id,
                         tile_luxury_resources_id)

        Map.tiles[this_map_id] = tile

    @staticmethod
    def init_tiles(map_interface):
        if not map_interface.activated:
            return

        Map.tiles = [Optional[Tile]] * (Map.lines * Map.columns)
        Map.tile_first_init = True

        for column in range(map_interface.size_x):
            for line in range(map_interface.size_y):
                map_interface_id = column * map_interface.size_y + line
                Map.update_tile(map_interface, map_interface_id)


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
    def init_unit_graph():
        for i, j in np.ndindex(Map.lines, Map.columns):
            if j > 0:
                if (Map.get_tile(i, j - 1).movement_cost == 'Unpassable'
                    or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i, j - 1).type_id in [2, 3])
                    or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i, j - 1).type_id in [0, 1, 4, 5])
                    ):
                    Map.G_unit_distance.add_edge(i * Map.columns + j, i * Map.columns + j - 1,
                                                 weight=float('inf'))
                else:
                    Map.G_unit_distance.add_edge(i * Map.columns + j, i * Map.columns + j - 1,
                                                 weight=Map.get_tile(i, j - 1).movement_cost)
            if j < Map.columns - 1:
                if (Map.get_tile(i, j + 1).movement_cost == 'Unpassable'
                    or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i, j + 1).type_id in [2, 3])
                    or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i, j + 1).type_id in [0, 1, 4, 5])
                    ):
                    Map.G_unit_distance.add_edge(i * Map.columns + j, i * Map.columns + j + 1,
                                                 weight=float('inf'))
                else:
                    Map.G_unit_distance.add_edge(i * Map.columns + j, i * Map.columns + j + 1,
                                                 weight=Map.get_tile(i, j + 1).movement_cost)
            if i < Map.lines - 1:
                if (Map.get_tile(i + 1, j).movement_cost == 'Unpassable'
                    or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i + 1, j).type_id in [2, 3])
                    or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i + 1, j).type_id in [0, 1, 4, 5])
                    ):
                    Map.G_unit_distance.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j,
                                                 weight=float('inf'))
                else:
                    Map.G_unit_distance.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j,
                                                 weight=Map.get_tile(i + 1, j).movement_cost)
            if i > 0:
                if (Map.get_tile(i - 1, j).movement_cost == 'Unpassable'
                    or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i - 1, j).type_id in [2, 3])
                    or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i - 1, j).type_id in [0, 1, 4, 5])
                    ):
                    Map.G_unit_distance.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j,
                                                 weight=float('inf'))
                else:
                    Map.G_unit_distance.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j,
                                                 weight=Map.get_tile(i - 1, j).movement_cost)
            if i % 2:
                if i < Map.lines - 1 and j < Map.columns - 1:
                    if (Map.get_tile(i + 1, j + 1).movement_cost == 'Unpassable'
                        or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i + 1, j + 1).type_id in [2, 3])
                        or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i + 1, j + 1).type_id in [0, 1, 4, 5])
                        ):
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j + 1,
                                                     weight=float('inf'))
                    else:
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j + 1,
                                                     weight=Map.get_tile(i + 1, j + 1).movement_cost)
                if i > 0 and j < Map.columns - 1:
                    if (Map.get_tile(i - 1, j + 1).movement_cost == 'Unpassable'
                        or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i - 1, j + 1).type_id in [2, 3])
                        or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i - 1, j + 1).type_id in [0, 1, 4, 5])
                        ):
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j + 1,
                                                     weight=float('inf'))
                    else:
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j + 1,
                                                     weight=Map.get_tile(i - 1, j + 1).movement_cost)
            else:
                if i < Map.lines - 1 and j > 0:
                    if (Map.get_tile(i + 1, j - 1).movement_cost == 'Unpassable'
                        or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i + 1, j - 1).type_id in [2, 3])
                        or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i + 1, j - 1).type_id in [0, 1, 4, 5])
                        ):
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j - 1,
                                                     weight=float('inf'))
                    else:
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i + 1) * Map.columns + j - 1,
                                                     weight=Map.get_tile(i + 1, j - 1).movement_cost)
                if i > 0 and j > 0:
                    if (Map.get_tile(i - 1, j - 1).movement_cost == 'Unpassable'
                        or (Map.get_tile(i, j).type_id in [0, 1, 4, 5] and Map.get_tile(i - 1, j - 1).type_id in [2, 3])
                        or (Map.get_tile(i, j).type_id in [2, 3] and Map.get_tile(i - 1, j - 1).type_id in [0, 1, 4, 5])
                        ):
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j - 1,
                                                     weight=float('inf'))
                    else:
                        Map.G_unit_distance.add_edge(i * Map.columns + j, (i - 1) * Map.columns + j - 1,
                                                     weight=Map.get_tile(i - 1, j - 1).movement_cost)
        Map.unit_shortest_distances = dict(nx.all_pairs_dijkstra_path_length(Map.G_unit_distance, weight='weight'))
        Map.unit_shortest_paths = dict(nx.all_pairs_dijkstra_path(Map.G_unit_distance, weight='weight'))
        # for i in range(0, Map.lines * Map.columns):
        #    Map.unit_shortest_distances.append(nx.single_source_dijkstra_path_length(Map.G_unit_distance, i))

    @staticmethod
    def get_unit_shortest_distance(start_line, start_col, end_line, end_col):
        return Map.unit_shortest_distances[start_line * Map.columns + start_col][end_line * Map.columns + end_col]

    @staticmethod
    def get_unit_reachable_tiles(start_line, start_col, max_distance):
        source = start_line * Map.columns + start_col
        reachable_nodes = nx.single_source_dijkstra_path_length(Map.G_unit_distance,
                                                                source, max_distance, weight='weight')
        reachable_tiles_coordinates = [(x // Map.columns, x % Map.columns) for x in reachable_nodes.keys()]
        return reachable_tiles_coordinates

    @staticmethod
    def get_unit_shortest_path(start_line, start_col, end_line, end_col):
        return Map.unit_shortest_paths[start_line * Map.columns + start_col][end_line * Map.columns + end_col]

    @staticmethod
    def get_tile(line, column) -> Tile.Tile:
        return Map.tiles[line * Map.columns + column]
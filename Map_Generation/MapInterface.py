import networkx as nx
import pygame as pg
import pyrr

from Logic.Game import Game
from Map_Generation.AssetsManager import AssetsManager
from Map_Generation.Map import Map
from Map_Generation.MapBuilder import *

player_colors = [
    [0.941, 0.047, 0.047],
    [1.000, 0.467, 0.200],
    [1.000, 0.953, 0.200],
    [0.071, 0.800, 0.302],
    [0.200, 0.510, 0.922],
    [0.784, 0.075, 0.851],
    [0.337, 0.980, 0.925],
    [0.553, 1.000, 0.576]
]

class MapInterface:
    size_x = 0
    size_y = 0
    vbo = None
    fbo = None
    shape = None

    owner = []
    units = []
    unit_types = dict()
    unit_pos = dict()
    unit_player = dict()
    next_unit_id = 0

    first_frame = True
    activated = False
    assets = None
    color_palette = None
    builder = None

    selected_tile = -1

    tile_border = []

    visibility = []
    active_player = -1

    def __init__(self, vbo, shader, fbo):
        self.camera_manager = None
        self.seed = 0
        self.num_players = 0
        self.vbo = vbo
        self.fbo = fbo
        self.shader = shader
        self.next_unit_id = 0
        self.activated = False

        random.shuffle(player_colors)

        Shader.close_all_shaders()

    def id_convertor(self, external_id):
        line = external_id // self.size_x
        column = external_id % self.size_x
        return self.convert_coordinates_to_mine(line, column)

    def convert_coordinates_to_mine(self, line, column):
        if not self.activated:
            return -1
        return column * self.size_y + line

    def activate(self, size_x, size_y, num_players, seed, camera_manager):
        if self.activated:
            return None

        self.activated = True
        self.camera_manager = camera_manager

        if num_players > 8:
            num_players = 8

        self.num_players = num_players
        self.size_x = size_x
        self.size_y = size_y

        # == -1 invisible
        # >= 0 -> reference count:
        #   == 0 - shadowed
        #   >= 1 - visible
        for i in range(num_players):
            self.visibility.append([-1] * (size_x * size_y))

        self.owner = [-1] * (size_x * size_y)
        for i in range(size_x * size_y):
            self.tile_border.append([-1, -1, -1, -1, -1, -1])

        self.shader.use_shader()

        angles = [0, 60, -60, 0, 60, -60]
        l = R - 0.2
        positions = [[-(l + 0.1) * np.cos(np.radians(30)), 0.0, 0.0],
                     [-l * np.cos(np.radians(60)), 0.0, -l * np.cos(np.radians(30))],
                     [l * np.cos(np.radians(60)), 0.0, -l * np.cos(np.radians(30))],
                     [(l + 0.1) * np.cos(np.radians(30)), 0.0, 0.0],
                     [l * np.cos(np.radians(60)), 0.0, l * np.cos(np.radians(30))],
                     [-l * np.cos(np.radians(60)), 0.0, l * np.cos(np.radians(30))]]

        for side in range(6):
            side_mat = pyrr.matrix44.create_identity(dtype=np.float32)
            side_mat = pyrr.matrix44.multiply(
                m1=side_mat,
                m2=pyrr.matrix44.create_from_scale(
                    scale=np.array([0.8, 1.0, 0.8]),
                    dtype=np.float32
                )
            )
            side_mat = pyrr.matrix44.multiply(
                m1=side_mat,
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.array([0.0, 0.0, np.radians(angles[side])]),
                    dtype=np.float32
                )
            )
            side_mat = pyrr.matrix44.multiply(
                m1=side_mat,
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(positions[side]),
                    dtype=np.float32
                )
            )

            self.shader.set_mat4(f"side_mat[{side}]", side_mat)

        for i in range(8):
            color = player_colors[i]
            self.shader.set_3float(f"player_color[{i}]", color[0], color[1], color[2])

        self.color_palette = ColorPalette(self.shader)
        self.assets = AssetsManager(self.vbo, self.color_palette, self.shader, size_x * size_y)
        self.units = [0] * (size_y  * size_x)

        self.seed = seed
        self.builder = MapMesh(self.size_x, self.size_y, 0.0, 2.0, 10, self.vbo, self.shader, self.assets, self.seed)
        self.color_palette.flush_texture_to_shader()

        ret = Game(num_players, size_y, size_x, self)

        return ret
        # return None

    def __apply_vis(self, visibility, tile_id):
        if self.activated is False:
            return

        if visibility < 0:
            self.set_visibility(tile_id, 0.0)
        elif visibility == 0:
            self.set_visibility(tile_id, 0.7)
        else:
            self.set_visibility(tile_id, 1.0)

    def switch_context(self, player_id, player_position):
        if self.active_player == player_id or self.activated is False:
            return

        self.active_player = player_id

        x_real, y_real = self.builder.real_coords(player_position[1], player_position[0])
        self.camera_manager.camera.pos = [x_real, 15, y_real + 15]

        for tile_id in range(self.size_x * self.size_y):
            visibility = self.visibility[player_id][tile_id]

            self.__apply_vis(visibility, tile_id)

    def clr_object_on_tile(self, tile_id):
        if not self.activated:
            return

        self.builder.clear_object_on_tile(tile_id)

    def add_object_on_tile(self, tile_id, asset_name):
        if not self.activated:
            return

        self.builder.add_object_on_tile(tile_id, asset_name)

    def add_visibility_source_here(self, tile_id, player_id):
        if not self.activated:
            return

        x_id = tile_id // self.size_y
        y_id = tile_id % self.size_y
        source_node = y_id * self.size_x + x_id

        nodes_at_distance = [
            node for node, dist in nx.single_source_shortest_path_length(Map.G, source_node).items()
            if dist <= 3
        ]

        for external_id in nodes_at_distance:
            my_id = self.id_convertor(external_id)

            if self.visibility[player_id][my_id] < 0:
                self.visibility[player_id][my_id] = 0

            self.visibility[player_id][my_id] += 1

            if self.active_player == player_id:
                self.__apply_vis(self.visibility[player_id][my_id], my_id)


    def rmv_visibility_source_here(self, tile_id, player_id):
        if not self.activated:
            return

        x_id = tile_id // self.size_y
        y_id = tile_id % self.size_y
        source_node = y_id * self.size_x + x_id

        nodes_at_distance = [
            node for node, dist in nx.single_source_shortest_path_length(Map.G, source_node).items()
            if dist <= 3
        ]

        for external_id in nodes_at_distance:
            my_id = self.id_convertor(external_id)

            if self.visibility[player_id][my_id] > 0:
                self.visibility[player_id][my_id] -= 1

            if self.active_player == player_id:
                self.__apply_vis(self.visibility[player_id][my_id], my_id)

    def __add_unit__(self, tile_id, unit_name, player_id, unit_id):
        if self.activated is False:
            return -1

        if self.units[tile_id] != 0:
            self.clr_unit(self.units[tile_id])

        self.assets.add_instance_of_at(unit_name, tile_id, self.builder.heights[tile_id], player_id)

        self.units[tile_id] = unit_id
        self.unit_pos[unit_id] = tile_id
        self.unit_types[unit_id] = unit_name
        self.unit_player[unit_id] = player_id

        self.add_visibility_source_here(tile_id, player_id)

        return unit_id

    def add_unit_on_tile(self, tile_id, unit_name, player_id):
        if self.activated is False:
            return -1

        self.next_unit_id += 1
        unit_id = self.next_unit_id

        return self.__add_unit__(tile_id, unit_name, player_id, unit_id)

    def clr_unit(self, unit_id):
        if self.activated is False or unit_id not in self.unit_pos:
            return

        tile_id = self.unit_pos[unit_id]
        if self.units[tile_id] == 0:
            return

        self.assets.remove_instance_of_at(self.unit_types[unit_id], tile_id)
        self.units[tile_id] = 0
        self.unit_pos.pop(unit_id)
        self.unit_types.pop(unit_id)

        self.rmv_visibility_source_here(tile_id, self.unit_player[unit_id])

        self.unit_player.pop(unit_id)

    def move_unit(self, unit_id, new_tile_id):
        if unit_id not in self.unit_pos or self.activated is False:
            return -1

        unit_name = self.unit_types[unit_id]
        player_id = self.unit_player[unit_id]

        self.clr_unit(unit_id)
        self.__add_unit__(new_tile_id, unit_name, player_id, unit_id)

    def __add_border_on_side(self, tile_id, side, player_id):
        if tile_id < 0 or tile_id >= self.size_x * self.size_y or not self.activated:
            return

        if self.tile_border[tile_id][side] != -1:
            return

        self.tile_border[tile_id][side] = player_id

        wall_id = tile_id | (side << 12) | (player_id << 15)
        self.assets.add_instance_of_at("Wall", wall_id, self.builder.heights[tile_id], -1.0)

    def __remove_border_on_side(self, tile_id, side):
        if tile_id < 0 or tile_id >= self.size_x * self.size_y or not self.activated:
            return

        if self.tile_border[tile_id][side] == -1:
            return

        player_id = self.tile_border[tile_id][side]
        self.tile_border[tile_id][side] = -1

        wall_id = tile_id | (side << 12) | (player_id << 15)
        self.assets.remove_instance_of_at("Wall", wall_id)

    def add_tile_selector(self, tile_id):
        self.builder.set_visibility(tile_id, 1.1)

    def rmv_tile_selector(self, tile_id):
        self.__apply_vis(self.visibility[self.active_player][tile_id], tile_id)

    def add_tile_owner(self, tile_id, player_id):
        if not self.activated or self.owner[tile_id] != -1 or self.owner[player_id] == player_id:
            return

        self.owner[tile_id] = player_id

        x = tile_id // self.size_y
        y = tile_id % self.size_y

        self.add_visibility_source_here(tile_id, player_id)

        # side 0
        x_id = x - 1; y_id = y
        nid = x_id * self.size_y + y_id
        if self.owner[nid] != player_id:
            self.__add_border_on_side(tile_id, 0, player_id)
        else:
            self.__remove_border_on_side(nid, 3)

        # side 1
        x_id = x - (y & 1 == 0); y_id = y - 1
        nid = x_id * self.size_y + y_id
        if self.owner[nid] != player_id:
            self.__add_border_on_side(tile_id, 1, player_id)
        else:
            self.__remove_border_on_side(nid, 4)

        # side 2
        x_id = x + 1 - (y & 1 == 0); y_id = y - 1
        nid = x_id * self.size_y + y_id
        if self.owner[nid] != player_id:
            self.__add_border_on_side(tile_id, 2, player_id)
        else:
            self.__remove_border_on_side(nid, 5)

        # side 3
        x_id = x + 1; y_id = y
        nid = x_id * self.size_y + y_id
        if self.owner[nid] != player_id:
            self.__add_border_on_side(tile_id, 3, player_id)
        else:
            self.__remove_border_on_side(nid, 0)

        # side 4
        x_id = x + 1 - (y & 1 == 0); y_id = y + 1
        nid = x_id * self.size_y + y_id
        if self.owner[nid] != player_id:
            self.__add_border_on_side(tile_id, 4, player_id)
        else:
            self.__remove_border_on_side(nid, 1)

        # side 5
        x_id = x - (y & 1 == 0); y_id = y + 1
        nid = x_id * self.size_y + y_id
        if self.owner[nid] != player_id:
            self.__add_border_on_side(tile_id, 5, player_id)
        else:
            self.__remove_border_on_side(nid, 2)

    def remove_owner(self, tile_id):
        if not self.activated or self.owner[tile_id] == -1:
            return

        for i in range(6):
            self.__remove_border_on_side(tile_id, i)

        self.rmv_visibility_source_here(tile_id, self.owner[tile_id])

        self.owner[tile_id] = -1

        x = tile_id // self.size_y
        y = tile_id % self.size_y

        # side 0
        x_id = x - 1; y_id = y
        nid = x_id * self.size_y + y_id
        player_id = self.owner[nid]
        if self.owner[nid] != -1:
            self.__add_border_on_side(nid, 3, player_id)

        # side 1
        x_id = x - (y & 1 == 0); y_id = y - 1
        nid = x_id * self.size_y + y_id
        player_id = self.owner[nid]
        if self.owner[nid] != -1:
            self.__add_border_on_side(nid, 4, player_id)

        # side 2
        x_id = x + 1 - (y & 1 == 0); y_id = y - 1
        nid = x_id * self.size_y + y_id
        player_id = self.owner[nid]
        if self.owner[nid] != -1:
            self.__add_border_on_side(nid, 5, player_id)

        # side 3
        x_id = x + 1; y_id = y
        nid = x_id * self.size_y + y_id
        player_id = self.owner[nid]
        if self.owner[nid] != -1:
            self.__add_border_on_side(nid, 0, player_id)

        # side 4
        x_id = x + 1 - (y & 1 == 0); y_id = y + 1
        nid = x_id * self.size_y + y_id
        player_id = self.owner[nid]
        if self.owner[nid] != -1:
            self.__add_border_on_side(nid, 1, player_id)

        # side 5
        x_id = x - (y & 1 == 0); y_id = y + 1
        nid = x_id * self.size_y + y_id
        player_id = self.owner[nid]
        if self.owner[nid] != -1:
            self.__add_border_on_side(nid, 2, player_id)


    def highlight_tile(self, tile_id):
        self.shader.set_float("highlight_id", tile_id)

    def set_visibility(self, tile_id, vis: float):
        self.builder.set_visibility(tile_id, vis)

    def tile_on_mouse(self, mouse_x, mouse_y):
        #return self.builder.get_tile_on_mouse(mouse_x, mouse_y, self.fbo)
        return self.selected_tile

    def __first_frame(self):
        self.first_frame = False

    def every_frame(self, tile_on_mouse_func):
        # DO NOT MODIFY
        if not self.activated:
            return

        if self.first_frame:
            self.__first_frame()

        glBindVertexArray(self.builder.mesh.vbo.vao)
        self.builder.draw(self.active_player)

        screen_size = pg.display.get_surface().get_size()
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_y = screen_size[1] - mouse_y

        tile_now = self.builder.get_tile_on_mouse(mouse_x, mouse_y, self.fbo)
        if 0 <= tile_now < self.size_x * self.size_y:
            self.selected_tile = tile_now

        if tile_on_mouse_func(pg.mouse.get_pos()):
            self.selected_tile = -1
            self.highlight_tile(-1)

        if self.size_y * self.size_x >= tile_now >= 0 > self.visibility[self.active_player][tile_now] and self.active_player != -1:
            self.selected_tile = -1
            self.highlight_tile(-1)

        # DO NOT MODIFY ENDS HERE

        # TEST LOGIC STARTS HERE
        pixel = self.tile_on_mouse(mouse_x, mouse_y)

        if 0 <= pixel < self.size_x * self.size_y:
            self.highlight_tile(pixel)

        # TEST LOGIC ENDS HERE

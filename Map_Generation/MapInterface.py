import time
import random
from math import radians

import pygame as pg
import pyrr
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
from select import select

from Graphics.ColorPalette import ColorPalette
from Graphics.Shaders import Shader
from Logic.Game import Game
from Map_Generation.AssetsManager import AssetsManager
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
    unit_count = 0

    first_frame = True
    activated = False
    assets = None
    color_palette = None
    builder = None

    selected_tile = -1

    tile_border = []

    def __init__(self, vbo, shader, fbo):
        self.seed = 0
        self.num_players = 0
        self.vbo = vbo
        self.fbo = fbo
        self.shader = shader
        self.unit_count = 0
        self.activated = False

        random.shuffle(player_colors)

        Shader.close_all_shaders()

    def id_convertor(self, external_id):
        line = external_id // self.size_x
        column = external_id % self.size_y
        return self.convert_coordinates_to_mine(line, column)

    def convert_coordinates_to_mine(self, line, column):
        if not self.activated:
            return -1
        return column * self.size_y + line

    def activate(self, size_x, size_y, num_players, seed):
        if self.activated:
            return None

        self.activated = True

        if num_players > 8:
            num_players = 8

        self.num_players = num_players
        self.size_x = size_x
        self.size_y = size_y

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

        #return Game(num_players, size_y, size_x, self)
        return None

    def clr_object_on_tile(self, tile_id):
        self.builder.clear_object_on_tile(tile_id)

    def add_object_on_tile(self, tile_id, asset_name):
        self.builder.add_object_on_tile(tile_id, asset_name)

    def add_unit_on_tile(self, tile_id, unit_name):
        if self.activated is False:
            return

        if self.units[tile_id] != 0:
            self.clr_unit(self.units[tile_id])

        self.assets.add_instance_of_at(unit_name, tile_id, self.builder.heights[tile_id])
        self.unit_count += 1
        unit_id = self.unit_count
        self.units[tile_id] = unit_id
        self.unit_pos[unit_id] = tile_id
        self.unit_types[unit_id] = unit_name

        return unit_id

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

    def move_unit(self, unit_id, new_tile_id):
        if unit_id not in self.unit_pos:
            return False

        unit_name = self.unit_types[unit_id]
        self.clr_unit(unit_id)
        self.add_unit_on_tile(new_tile_id, unit_name)

    def __add_border_on_side(self, tile_id, side, player_id):
        if tile_id < 0 or tile_id >= self.size_x * self.size_y or not self.activated:
            return

        if self.tile_border[tile_id][side] != -1:
            return

        self.tile_border[tile_id][side] = player_id

        wall_id = tile_id | (side << 12) | (player_id << 15)
        self.assets.add_instance_of_at("Wall", wall_id, self.builder.heights[tile_id])

    def __remove_border_on_side(self, tile_id, side):
        if tile_id < 0 or tile_id >= self.size_x * self.size_y or not self.activated:
            return

        if self.tile_border[tile_id][side] == -1:
            return

        player_id = self.tile_border[tile_id][side]
        self.tile_border[tile_id][side] = -1

        wall_id = tile_id | (side << 12) | (player_id << 15)
        self.assets.remove_instance_of_at("Wall", wall_id)

    def add_tile_owner(self, tile_id, player_id):
        if not self.activated or self.owner[tile_id] != -1 or self.owner[player_id] == player_id:
            return

        self.owner[tile_id] = player_id

        x = tile_id // self.size_y
        y = tile_id % self.size_y

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

    def highlight_tile(self, tile_id):
        self.shader.set_float("highlight_id", tile_id)

    def set_visibility(self, tile_id, vis: float):
        self.builder.set_visibility(tile_id, vis)

    def tile_on_mouse(self, mouse_x, mouse_y):
        #return self.builder.get_tile_on_mouse(mouse_x, mouse_y, self.fbo)
        return self.selected_tile

    def __first_frame(self):
        self.first_frame = False

    def every_frame(self):
        # DO NOT MODIFY
        if not self.activated:
            return

        if self.first_frame:
            self.__first_frame()

        glBindVertexArray(self.builder.mesh.vbo.vao)
        self.builder.draw()

        screen_size = pg.display.get_surface().get_size()
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_y = screen_size[1] - mouse_y

        tile_now = self.builder.get_tile_on_mouse(mouse_x, mouse_y, self.fbo)
        if 0 <= tile_now < self.size_x * self.size_y:
            self.selected_tile = tile_now
        # DO NOT MODIFY ENDS HERE

        # TEST LOGIC STARTS HERE
        pixel = self.tile_on_mouse(mouse_x, mouse_y)

        if 0 <= pixel < self.size_x * self.size_y:
            self.highlight_tile(pixel)

        # TEST LOGIC ENDS HERE

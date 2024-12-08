import time
import random
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
from Graphics.ColorPalette import ColorPalette
from Graphics.Shaders import Shader
from Map_Generation.AssetsManager import AssetsManager
from Map_Generation.MapBuilder import MapMesh


class MapInterface:
    size_x = 0
    size_y = 0
    vbo = None
    fbo = None
    shape = None

    units = []
    unit_types = dict()
    unit_pos = dict()
    unit_count = 0

    first_frame = True
    activated = False
    assets = None
    color_palette = None
    builder = None

    def __init__(self, size_x, size_y, vbo, shader, fbo):
        self.size_x = size_x
        self.size_y = size_y
        self.vbo = vbo
        self.fbo = fbo
        self.shader = shader
        self.color_palette = ColorPalette(self.shader)
        self.assets = AssetsManager(vbo, self.color_palette, shader, size_x * size_y)
        self.units = [0] * (size_y  * size_x)
        self.unit_count = 0
        self.activated = False

        Shader.close_all_shaders()

    def activate(self):
        if self.activated:
            return

        self.activated = True
        seed = random.randint(0, 0xffff)
        self.builder = MapMesh(self.size_x, self.size_y, 0.0, 2.0, 10, self.vbo, self.shader, self.assets, seed)
        self.color_palette.flush_texture_to_shader()

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

    def highlight_tile(self, tile_id):
        self.shader.set_float("highlight_id", tile_id)

    def tile_on_mouse(self, mouse_x, mouse_y):
        return self.builder.get_tile_on_mouse(mouse_x, mouse_y, self.fbo)

    def __first_frame(self):
        self.first_frame = False

    def every_frame(self):
        if not self.activated:
            return

        if self.first_frame:
            self.__first_frame()

        glBindVertexArray(self.builder.mesh.vbo.vao)
        self.builder.draw()

        # LOGIC STARTS HERE
        screen_size = pg.display.get_surface().get_size()
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_y = screen_size[1] - mouse_y

        pixel = self.tile_on_mouse(mouse_x, mouse_y)

        if 0 <= pixel < self.size_x * self.size_y:
            self.highlight_tile(pixel)

        # LOGIC ENDS HERE

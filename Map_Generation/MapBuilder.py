import random
import numpy as np
from OpenGL.GL import *
from perlin_noise import PerlinNoise
from Logic.Tile import tile_types
from Graphics.Buffers import DynamicVBO
from Graphics.Mesh import Mesh
from Graphics.Mesh import Vertex
from Graphics.Shaders import Shader

R = 1.0
dR = 0.3

x_axis = np.array([1.0, 0.0, 0.0])
y_axis = np.array([0.0, 1.0, 0.0])
z_axis = np.array([0.0, 0.0, 1.0])
diag_a1 = np.array([np.cos(np.radians(60)), 0.0, np.sin(np.radians(60))])

color_palet = np.array([
    [0.41, 0.74, 0.06],     # pale green
    [0.06, 0.74, 0.1],      # green
    [0.74, 0.74, 0.32],     # pale yellow
    [0.47, 0.47, 0.33],     # gray
    [0.4, 0.43, 0.43],      # brown
    [0.63, 0.78, 0.76],     # white
    [0.0, 0.2, 0.5]         # blue
])

tile_colors = {'Plains': 0,
               'Grassland': 1,
               'Shallow Water': 2,
               'Ocean': 3,
               'Mountain': 4,
               'Peaks': 5,
}

class MapMesh:
    def __init__(self, size_x, size_y, y_min, y_max, divs, vbo: DynamicVBO):
        self.size_x = size_x
        self.size_y = size_y
        self.y_min = y_min
        self.y_max = y_max
        self.mesh = Mesh(vbo)
        self.divs = divs

        self.loaded = [False] * (size_x * size_y)
        self.heights = [0.0] * (size_x * size_y)
        self.types = [0] * (size_x * size_y)

        self.len_x = R * np.cos(np.radians(30))
        self.len_y = R * np.sin(np.radians(30))
        self.noise = PerlinNoise(octaves = 1, seed = random.randint(0, 0xffff))

        for y in range(size_y):
            for x in range(size_x):
                self.pick_type(x, y)

        for y in range(0, size_y):
            for x in range(0, size_x):
                real_index = x * size_y + y
                self.loaded[real_index] = True
                self.add_hex(x, y, self.mesh, y & 1 == 0)

        # add water plane
        self.water_lvl = (y_max / divs) * 1.8
        self.water = Mesh(vbo)
        for y in range(0, size_y):
            for x in range(0, size_x):
                self.add_hex(x, y, self.water, y & 1 == 0, True)

        self.water.flush()
        self.water.update_matrices()
        self.water.activate()

        self.mesh.flush()
        self.mesh.update_matrices()
        self.mesh.activate()

    def __value(self, val: float, steps: int)->float:
        dv = (self.y_max - self.y_min) / steps
        ret = 0.0
        for i in range(steps):
            if ret <= val <= ret + dv:
                return ret
            ret += dv
        return ret

    @staticmethod
    def paraboloid_up(x1, x2, x):
        n = x2
        a = 1
        m = -1 / pow(x1 - x2, 2)
        return a + m * pow(x - n, 2)

    @staticmethod
    def paraboloid_down(x1, x2, x):
        n = x1
        a = 1
        m = -1 / pow(x2 - x1, 2)
        return a + m * pow(x - n, 2)

    @staticmethod
    def continental(x, s):
        if x <= 4:
            return MapMesh.paraboloid_up(0, 8, x)
        if x >= s - 5:
            return MapMesh.paraboloid_down(s - 9, s - 1, x)
        return 1.0
        #return (pow(s / 2.0, 2) - pow(x - s / 2.0, 2)) / pow(s / 2.0, 2)

    def pick_type(self, x_id: int, y_id: int):
        x_offset = 0
        if y_id & 1:
            x_offset = self.len_x + 0.5 * dR
        x = x_offset + (2 * self.len_x + dR) * x_id
        y = (self.len_y + R + dR * np.sqrt(3.0) / 2.0) * y_id

        value = (1.0 + self.noise([x / (self.size_y * 0.2), y / (self.size_y * 0.2)])) * 0.5
        value = 1.2 * value * value
        value *= MapMesh.continental(x_id, self.size_x) * MapMesh.continental(y_id, self.size_y) * self.y_max

        lvl = int(np.floor(value / (self.y_max / self.divs)))

        if lvl == 0:
            tile_type = 3
        elif lvl == 1:
            tile_type = 2
        elif 2 <= lvl <= 3:
            tile_type = 1
        elif lvl == 4:
            tile_type = 0
        elif lvl == 5:
            tile_type = 4
        else:
            tile_type = 5

        self.heights[x_id * self.size_y + y_id] = self.__value(value, self.divs)
        self.types[x_id * self.size_y + y_id] = tile_type

    def draw(self, shader: Shader):
        glEnable(GL_CULL_FACE)
        shader.set_float("opacity", 1.0)
        self.mesh.draw(shader)

        glDisable(GL_CULL_FACE)
        shader.set_float("opacity", 0.7)
        self.water.draw(shader)

    def add_hex(self, x_id, y_id, mesh, even_tile: bool, water_tile = False):
        x_offset = 0
        if not even_tile:
            x_offset = self.len_x + 0.5 * dR

        central_id = x_id * self.size_y + y_id
        x = x_offset + (2 * self.len_x + dR) * x_id
        y = (self.len_y + R + dR * np.sqrt(3) / 2) * y_id
        h = self.heights[x_id * self.size_y + y_id]
        if water_tile:
            h = self.water_lvl

        dx = R * np.cos(np.radians(30))
        dy = R * 0.5

        color = [tile_colors[tile_types[self.types[x_id * self.size_y + y_id]]], central_id, 0]
        if water_tile:
            color = [6, central_id, 0]

        # main hexagon
        center = Vertex([x, h, y], [0.0, 1.0, 0.0], color)
        p1 = Vertex([x + dx, h, y + dy], [0.0, 1.0, 0.0], color)
        p2 = Vertex([x, h, y + R], [0.0, 1.0, 0.0], color)
        p3 = Vertex([x - dx, h, y + dy], [0.0, 1.0, 0.0], color)
        p4 = Vertex([x - dx, h, y - dy], [0.0, 1.0, 0.0], color)
        p5 = Vertex([x, h, y - R], [0.0, 1.0, 0.0], color)
        p6 = Vertex([x + dx, h, y - dy], [0.0, 1.0, 0.0], color)

        mesh.push_triangle(center, p2, p1)
        mesh.push_triangle(center, p3, p2)
        mesh.push_triangle(center, p4, p3)
        mesh.push_triangle(center, p5, p4)
        mesh.push_triangle(center, p6, p5)
        mesh.push_triangle(center, p1, p6)

        if x_id != self.size_x - 1:
            #(x + 1, y)
            real_id = (x_id + 1) * self.size_y + y_id
            other_color = [tile_colors[tile_types[self.types[real_id]]], real_id, 0]
            p11 = np.array(p1.position)
            p66 = np.array(p6.position)
            nh = self.heights[real_id]
            if water_tile:
                nh = self.water_lvl
                other_color = [6, real_id, 0]
            m1 = np.array([x + dx + dR, nh, y + dy])
            m2 = np.array([x + dx + dR, nh, y])
            m3 = np.array([x + dx + dR, nh, y - dy])
            d1 = p11 - m2
            d2 = m1 - m2
            norm = np.cross(d1, d2)
            norm = norm / np.linalg.norm(norm)
            mesh.push_triangle_pos(m2, p11, m1, other_color, color, other_color, norm)
            mesh.push_triangle_pos(m2, m3, p66, other_color, other_color, color, norm)
            mesh.push_triangle_pos(m2, p66, p11, other_color, color, color, norm)

        other_x = x_id
        if not even_tile:
            other_x = x_id + 1

        if other_x != self.size_x:
            #(x + 1, y + 1)
            if y_id != self.size_y - 1:
                real_id = other_x * self.size_y + y_id + 1
                other_color = [tile_colors[tile_types[self.types[real_id]]], real_id, 0]
                p11 = np.array(p1.position)
                p22 = np.array(p2.position)
                nh = self.heights[real_id]
                if water_tile:
                    nh = self.water_lvl
                    other_color = [6, real_id, 0]
                m1 = np.array([x + 0.5 * dR, nh, y + R + dR * np.sqrt(3.0) / 2.0])
                m3 = np.array([x + dx + 0.5 * dR, nh, y + self.len_y + dR * np.sqrt(3.0) / 2.0])
                m2 = (m1 + m3) * 0.5
                d1 = p22 - m2
                d2 = m1 - m2
                norm = np.cross(d1, d2)
                norm = norm / np.linalg.norm(norm)
                mesh.push_triangle_pos(m2, p22, m1, other_color, color, other_color, norm)
                mesh.push_triangle_pos(m2, m3, p11, other_color, other_color, color, norm)
                mesh.push_triangle_pos(m2, p11, p22, other_color, color, color, norm)

                #corner
                if x_id != self.size_x - 1:
                    tmp = (x_id + 1) * self.size_y + y_id
                    tmp_col = [tile_colors[tile_types[self.types[tmp]]], tmp, 0]
                    tmp_h = self.heights[tmp]
                    if water_tile:
                        tmp_h = self.water_lvl
                        tmp_col = [6, tmp, 0]
                    n1 = np.array([x + dx + dR, tmp_h, y + dy])
                    d1 = n1 - m3
                    d2 = p11 - m3
                    norm = np.cross(d1, d2)
                    norm = norm / np.linalg.norm(norm)
                    mesh.push_triangle_pos(m3, n1, p11, other_color, tmp_col, color, norm)
            if y_id != 0:
                real_id = other_x * self.size_y + y_id - 1
                other_color = [tile_colors[tile_types[self.types[real_id]]], real_id, 0]
                p66 = np.array(p6.position)
                p55 = np.array(p5.position)
                nh = self.heights[real_id]
                if water_tile:
                    nh = self.water_lvl
                    other_color = [6, real_id, 0]
                m1 = np.array([x + dx + 0.5 * dR, nh, y - self.len_y - dR * np.sqrt(3.0) / 2.0])
                m3 = np.array([x + 0.5 * dR, nh, y - R - dR * np.sqrt(3.0) / 2.0])
                m2 = (m1 + m3) * 0.5
                d1 = p66 - m2
                d2 = m1 - m2
                norm = np.cross(d1, d2)
                norm = norm / np.linalg.norm(norm)
                mesh.push_triangle_pos(m2, p66, m1, other_color, color, other_color, norm)
                mesh.push_triangle_pos(m2, m3, p55, other_color, other_color, color, norm)
                mesh.push_triangle_pos(m2, p55, p66, other_color, color, color, norm)

                # corner
                if x_id != self.size_x - 1:
                    tmp = (x_id + 1) * self.size_y + y_id
                    tmp_col = [tile_colors[tile_types[self.types[tmp]]], tmp, 0]
                    tmp_h = self.heights[tmp]
                    if water_tile:
                        tmp_h = self.water_lvl
                        tmp_col = [6, tmp, 0]
                    n1 = np.array([x + dx + dR, tmp_h, y - dy])
                    d1 = p66 - m1
                    d2 = n1 - m1
                    norm = np.cross(d1, d2)
                    norm = norm / np.linalg.norm(norm)
                    mesh.push_triangle_pos(m1, p66, n1, other_color, color, tmp_col, norm)



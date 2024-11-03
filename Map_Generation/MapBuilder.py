import random
import numpy as np
from pyrr.plane import normal
from pyrr.rectangle import height

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

class MapMesh:
    def __init__(self, size_x, size_y, vbo: DynamicVBO):
        self.size_x = size_x
        self.size_y = size_y
        self.mesh = Mesh(vbo)
        # self.add_hex(0, 0, 0)

        self.loaded = [False] * (size_x * size_y)
        self.heights = [0.0] * (size_x * size_y)
        self.colors = [[0.0, 0.0, 0.0]] * (size_x * size_y)

        for y in range(size_y):
            for x in range(size_x):
                real_id = x * size_x + y
                self.heights[real_id] = random.uniform(0, 1)
                self.colors[real_id] = [random.uniform(0.1, 1), random.uniform(0.1, 1), random.uniform(0.1, 1)]

        self.len_x = R * np.cos(np.radians(30))
        self.len_y = R * np.sin(np.radians(30))
        for y in range(0, size_y):
            for x in range(0, size_x):
                real_index = x * size_y + y
                self.loaded[real_index] = True
                self.add_hex(x, y, y & 1 == 0)

        self.mesh.flush()
        self.mesh.update_matrices()
        self.mesh.activate()

    def draw(self, shader: Shader):
        self.mesh.draw(shader)

    def add_hex(self, x_id, y_id, even_tile: bool):
        x_offset = 0
        if not even_tile:
            x_offset = self.len_x + 0.5 * dR

        x = x_offset + (2 * self.len_x + dR) * x_id
        y = (self.len_y + R + dR * np.sqrt(3) / 2) * y_id
        h = self.heights[x_id * self.size_y + y_id]

        dx = R * np.cos(np.radians(30))
        dy = R * 0.5

        color = self.colors[x_id * self.size_y + y_id]

        # main hexagon
        center = Vertex([x, h, y], [0.0, 1.0, 0.0], color)
        p1 = Vertex([x + dx, h, y + dy], [0.0, 1.0, 0.0], color)
        p2 = Vertex([x, h, y + R], [0.0, 1.0, 0.0], color)
        p3 = Vertex([x - dx, h, y + dy], [0.0, 1.0, 0.0], color)
        p4 = Vertex([x - dx, h, y - dy], [0.0, 1.0, 0.0], color)
        p5 = Vertex([x, h, y - R], [0.0, 1.0, 0.0], color)
        p6 = Vertex([x + dx, h, y - dy], [0.0, 1.0, 0.0], color)

        self.mesh.push_triangle(center, p2, p1)
        self.mesh.push_triangle(center, p3, p2)
        self.mesh.push_triangle(center, p4, p3)
        self.mesh.push_triangle(center, p5, p4)
        self.mesh.push_triangle(center, p6, p5)
        self.mesh.push_triangle(center, p1, p6)

        if x_id != self.size_x - 1:
            #(x + 1, y)
            real_id = (x_id + 1) * self.size_y + y_id
            other_color = self.colors[real_id]
            p11 = np.array(p1.position)
            p66 = np.array(p6.position)
            m1 = np.array([x + dx + dR, self.heights[real_id], y + dy])
            m2 = np.array([x + dx + dR, self.heights[real_id], y])
            m3 = np.array([x + dx + dR, self.heights[real_id], y - dy])
            d1 = p11 - m2
            d2 = m1 - m2
            norm = np.cross(d1, d2)
            norm = norm / np.linalg.norm(norm)
            self.mesh.push_triangle_pos(m2, p11, m1, other_color, color, other_color, norm)
            self.mesh.push_triangle_pos(m2, m3, p66, other_color, other_color, color, norm)
            self.mesh.push_triangle_pos(m2, p66, p11, other_color, color, color, norm)

        other_x = x_id
        if not even_tile:
            other_x = x_id + 1

        if other_x != self.size_x:
            #(x + 1, y + 1)
            if y_id != self.size_y - 1:
                real_id = other_x * self.size_y + y_id + 1
                other_color = self.colors[real_id]
                p11 = np.array(p1.position)
                p22 = np.array(p2.position)
                m1 = np.array([x + 0.5 * dR, self.heights[real_id], y + R + dR * np.sqrt(3.0) / 2.0])
                m3 = np.array([x + dx + 0.5 * dR, self.heights[real_id], y + self.len_y + dR * np.sqrt(3.0) / 2.0])
                m2 = (m1 + m3) * 0.5
                d1 = p22 - m2
                d2 = m1 - m2
                norm = np.cross(d1, d2)
                norm = norm / np.linalg.norm(norm)
                self.mesh.push_triangle_pos(m2, p22, m1, other_color, color, other_color, norm)
                self.mesh.push_triangle_pos(m2, m3, p11, other_color, other_color, color, norm)
                self.mesh.push_triangle_pos(m2, p11, p22, other_color, color, color, norm)

                #corner
                if x_id != self.size_x - 1:
                    tmp = (x_id + 1) * self.size_y + y_id
                    n1 = np.array([x + dx + dR, self.heights[tmp], y + dy])
                    tmp_col = self.colors[tmp]
                    d1 = n1 - m3
                    d2 = p11 - m3
                    norm = np.cross(d1, d2)
                    norm = norm / np.linalg.norm(norm)
                    self.mesh.push_triangle_pos(m3, n1, p11, other_color, tmp_col, color, norm)
            if y_id != 0:
                real_id = other_x * self.size_y + y_id - 1
                other_color = self.colors[real_id]
                p66 = np.array(p6.position)
                p55 = np.array(p5.position)
                m1 = np.array([x + dx + 0.5 * dR, self.heights[real_id], y - self.len_y - dR * np.sqrt(3.0) / 2.0])
                m3 = np.array([x + 0.5 * dR, self.heights[real_id], y - R - dR * np.sqrt(3.0) / 2.0])
                m2 = (m1 + m3) * 0.5
                d1 = p66 - m2
                d2 = m1 - m2
                norm = np.cross(d1, d2)
                norm = norm / np.linalg.norm(norm)
                self.mesh.push_triangle_pos(m2, p66, m1, other_color, color, other_color, norm)
                self.mesh.push_triangle_pos(m2, m3, p55, other_color, other_color, color, norm)
                self.mesh.push_triangle_pos(m2, p55, p66, other_color, color, color, norm)

                # corner
                if x_id != self.size_x - 1:
                    tmp = (x_id + 1) * self.size_y + y_id
                    n1 = np.array([x + dx + dR, self.heights[tmp], y - dy])
                    tmp_col = self.colors[tmp]
                    d1 = p66 - m1
                    d2 = n1 - m1
                    norm = np.cross(d1, d2)
                    norm = norm / np.linalg.norm(norm)
                    self.mesh.push_triangle_pos(m1, p66, n1, other_color, color, tmp_col, norm)



import numpy as np
from Graphics.Buffers import DynamicVBO
from Graphics.Mesh import Mesh
from Graphics.Mesh import Vertex
from Graphics.Shaders import Shader

R = 1.0

class MapMesh:
    def __init__(self, size_x, size_y, vbo: DynamicVBO):
        self.size_x = size_x
        self.size_y = size_y
        self.mesh = Mesh(vbo)
        self.add_hex(0, 0, 0, 0)
        self.mesh.flush()
        self.mesh.update_matrices()
        self.mesh.activate()

    def draw(self, shader: Shader):
        self.mesh.draw(shader)

    def add_hex(self, x, y, this_h, delta_hs: list[int]):
        dx = R * np.cos(np.radians(30))
        dy = R * 0.5

        # main hexagon
        center = Vertex([x, 0, y], [0.0, 1.0, 0.0], [0.2, 0.4, 0.5])
        p1 = Vertex([x + dx, 0, y + dy], [0.0, 1.0, 0.0], [0.2, 0.4, 0.5])
        p2 = Vertex([x, 0, y + R], [0.0, 1.0, 0.0], [0.2, 0.4, 0.5])
        p3 = Vertex([x - dx, 0, y + dy], [0.0, 1.0, 0.0], [0.2, 0.4, 0.5])
        p4 = Vertex([x - dx, 0, y - dy], [0.0, 1.0, 0.0], [0.2, 0.4, 0.5])
        p5 = Vertex([x, 0, y - R], [0.0, 1.0, 0.0], [0.2, 0.4, 0.5])
        p6 = Vertex([x + dx, 0, y - dy], [0.0, 1.0, 0.0], [0.2, 0.4, 0.5])

        self.mesh.push_triangle(center, p2, p1)
        self.mesh.push_triangle(center, p3, p2)
        self.mesh.push_triangle(center, p4, p3)
        self.mesh.push_triangle(center, p5, p4)
        self.mesh.push_triangle(center, p6, p5)
        self.mesh.push_triangle(center, p1, p6)



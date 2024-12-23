import pyrr
from OpenGL.GL import *
import numpy as np
from numpy import dtype

from Graphics.Buffers import DynamicVBO
from Graphics.Shaders import Shader

class Vertex:
    def __init__(self, position, normal, color):
        self.position = position
        self.normal = normal
        self.color = color
    def to_list(self):
        return [self.position[0], self.position[1], self.position[2],
                self.normal[0], self.normal[1], self.normal[2],
                self.color[0], self.color[1], self.color[2]]

    def copy(self):
        return Vertex(self.position, self.normal, self.color)

class Mesh:
    def __init__(self, vbo_ref:DynamicVBO):
        self.vbo = vbo_ref
        self.mem_id = -1
        self.vertices = []

        self.position = np.array([0.0, 0.0, 0.0])
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.scale = np.array([1.0, 1.0, 1.0])

        self.model_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        self.normal_matrix = pyrr.matrix33.create_identity(dtype=np.float32)

        self.update_matrices()

    def update_matrices(self):
        self.update_model_matrix()
        self.update_normal_matrix()

    def update_model_matrix(self):
        self.model_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        self.model_matrix = pyrr.matrix44.multiply(
            m1=self.model_matrix,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=self.rotation,
                dtype=np.float32
            )
        )
        self.model_matrix = pyrr.matrix44.multiply(
            m1=self.model_matrix,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),
                dtype=np.float32
            )
        )
        self.model_matrix = pyrr.matrix44.multiply(
            m1=self.model_matrix,
            m2=pyrr.matrix44.create_from_scale(
                scale=self.scale,
                dtype=np.float32
            )
        )

    def update_normal_matrix(self):
        inverse_model_matrix = pyrr.matrix44.inverse(self.model_matrix)
        normal_matrix = np.transpose(inverse_model_matrix)
        self.normal_matrix = (normal_matrix[:3, :3]).flatten()

    def apply_transform_only(self, shader):
        shader.set_mat4("model", self.model_matrix)
        shader.set_mat3("normMatrix", self.normal_matrix)

    def get_location(self):
        if self.mem_id != -1:
            return self.vbo.get_block_locations(self.mem_id)
        return None, None

    def draw(self, shader:Shader):
        if self.mem_id != -1:
            shader.set_mat4("model", self.model_matrix)
            shader.set_mat3("normMatrix", self.normal_matrix)
            self.vbo.draw_vertices(self.mem_id)

    def set_vertices(self, vertices):
        self.vertices = vertices.copy()

    def push_vertex(self, vertex:Vertex):
        self.vertices.append(vertex.to_list())

    def push_triangle(self, p1:Vertex, p2:Vertex, p3:Vertex):
        self.vertices.extend(p1.to_list())
        self.vertices.extend(p2.to_list())
        self.vertices.extend(p3.to_list())

    def push_triangle_pos(self, p1:np.array, p2:np.array, p3:np.array, color1, color2, color3, norm):
        v1 = Vertex(p1, norm, color1)
        v2 = Vertex(p2, norm, color2)
        v3 = Vertex(p3, norm, color3)
        self.push_triangle(v1, v2, v3)

    def pop_vertex(self):
        for i in range(9):
            self.vertices.pop()

    def set_vertex(self, vert_id:int, vertex:Vertex):
        real_id = vert_id * self.vbo.size_of_vertex
        if real_id >= len(self.vertices):
            return
        self.vertices[real_id] = vertex.position[0]
        self.vertices[real_id + 1] = vertex.position[1]
        self.vertices[real_id + 2] = vertex.position[2]
        self.vertices[real_id + 3] = vertex.normal[0]
        self.vertices[real_id + 4] = vertex.normal[1]
        self.vertices[real_id + 5] = vertex.normal[2]
        self.vertices[real_id + 6] = vertex.color[0]
        self.vertices[real_id + 7] = vertex.color[1]
        self.vertices[real_id + 8] = vertex.color[2]

    def flush(self):
        if len(self.vertices) == 0:
            return

        if self.mem_id == -1:
            self.mem_id = self.vbo.add_vertices(np.array(self.vertices, dtype=np.float32))
        else:
            self.vbo.free_vertices(self.mem_id)
            self.mem_id = self.vbo.add_vertices(np.array(self.vertices, dtype=np.float32))

    def activate(self):
        if self.mem_id != -1:
            self.vbo.set_vertices_status(self.mem_id, True)

    def deactivate(self):
        if self.mem_id != -1:
            self.vbo.set_vertices_status(self.mem_id, False)

import os

import numpy as np
from Graphics.ColorPalette import ColorPalette
from plyfile import PlyData
from Graphics.Mesh import Vertex, Mesh


class Asset:
    def __init__(self):
        self.i = 0

class AssetsManager:
    def __init__(self, vbo, color_palette):
        self.vbo = vbo
        dir = "./Assets"
        files = AssetsManager.__find_ply_files(dir)
        self.color_palette = color_palette

        self.meshes = dict()

        pox_x = 0
        for file in files:
            file_name = os.path.splitext(os.path.basename(file))[0]
            triangles = self.read_ply(file)
            mesh = self.__get_mesh_at(triangles, [0, 0, 0], -1)
            mesh.flush()
            self.meshes[file_name] = mesh

    def __get_mesh_at(self, triangles, position, tile_id):
        mesh = Mesh(self.vbo)
        for triangle in triangles:
            v1 = triangle[0]
            v2 = triangle[1]
            v3 = triangle[2]
            v1.color[1] = tile_id
            v2.color[1] = tile_id
            v3.color[1] = tile_id
            mesh.push_triangle(v1, v2, v3)
        mesh.flush()
        mesh.rotation = [np.radians(90.0), 0, 0]
        mesh.position = position
        mesh.activate()
        mesh.update_matrices()
        return mesh

    @staticmethod
    def __find_ply_files(root_dir):
        ply_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for file in filenames:
                if file.endswith('.ply'):
                    ply_files.append(os.path.join(dirpath, file))
        return ply_files

    def read_ply(self, ply_file):
        ply_data = PlyData.read(ply_file)

        vertices = ply_data['vertex']
        positions = np.array([(0.7 * v['x'], 0.7 * v['y'], 0.7 * v['z']) for v in vertices], dtype=np.float32)
        normals = np.array([(v['nx'], v['ny'], v['nz']) for v in vertices], dtype=np.float32)
        colors = np.array([(v['red'] / 256.0, v['green'] / 256.0, v['blue'] / 256.0) for v in vertices], dtype=np.float32)

        faces = ply_data['face']
        triangles = [face[0] for face in faces]

        final_vertices = []

        for i in range(len(positions)):
            color = [self.color_palette.identify_color(colors[i]), -1, 0]
            final_vertices.append(Vertex(positions[i], normals[i], color))

        vert = []

        for triangle in triangles:
            v1 = final_vertices[triangle[0]]
            v2 = final_vertices[triangle[1]]
            v3 = final_vertices[triangle[2]]
            vert.append((v1, v2, v3))

        return vert
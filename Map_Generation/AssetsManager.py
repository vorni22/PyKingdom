import os
from plyfile import PlyData
from Graphics.Mesh import *
from OpenGL.GL import *

from Logic.City import district_types
from Logic.Unit import unit_classes


class Asset:
    def __init__(self):
        self.i = 0

class AssetsManager:
    def __init__(self, vbo, color_palette, shader, total_tiles):
        self.vbo = vbo
        dir = "./Assets"
        files = AssetsManager.__find_ply_files(dir)
        self.color_palette = color_palette
        self.meshes = dict()
        self.tile_ids_draw = dict()
        self.asset_id = dict()
        self.width = total_tiles
        self.height = len(files)
        self.shader = shader
        self.__prepare_resource_texture()

        count = 0
        for file in files:
            file_name = os.path.splitext(os.path.basename(file))[0]

            scale = 0.6
            if file_name == 'Rainforest' or file_name == 'Coral Reef' or file_name == 'Fish' or file_name == 'Banana':
                scale = 0.5

            h = 0
            if file_name == 'Harbour':
                h = -0.01
                scale = 1.15
            triangles = self.read_ply(file, scale)
            mesh = self.__get_mesh_at(triangles, [0, h, 0], -1)
            mesh.flush()
            self.meshes[file_name] = mesh
            self.tile_ids_draw[file_name] = []
            self.asset_id[file_name] = count
            count += 1

    def __prepare_resource_texture(self):
        self.resource_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.resource_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RG32F, self.width, self.height, 0, GL_RG, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def __bind_texture(self):
        self.shader.use_shader()
        texture_location = glGetUniformLocation(self.shader.shader, "uResourcesTexture")

        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.resource_texture)
        glUniform1i(texture_location, 2)

    def remove_instance_of_at(self, asset_name, tile_id):
        if asset_name not in self.meshes:
            return

        pos = -1
        i = 0
        for pairs in self.tile_ids_draw[asset_name]:
            if pairs[0] == tile_id:
                pos = i
                break
            i+=1

        if pos == -1:
            return

        self.tile_ids_draw[asset_name].pop(pos)
        x = 0
        count = len(self.tile_ids_draw[asset_name])
        y = self.asset_id[asset_name]
        glBindTexture(GL_TEXTURE_2D, self.resource_texture)
        glTexSubImage2D(
            GL_TEXTURE_2D,  # Texture target
            0,  # Mipmap level (0 for base level)
            x,  # X position of the pixel
            y,  # Y position of the pixel
            count,  # Width of the region (1 pixel)
            1,  # Height of the region (1 pixel)
            GL_RG,  # Format of the data
            GL_FLOAT,  # Data type
            self.tile_ids_draw[asset_name]  # Pixel data
        )

    def add_instance_of_at(self, asset_name, tile_id, h):
        if asset_name not in self.meshes:
            return
        x = len(self.tile_ids_draw[asset_name])
        y = self.asset_id[asset_name]
        self.tile_ids_draw[asset_name].append((tile_id, h))
        glBindTexture(GL_TEXTURE_2D, self.resource_texture)
        data = np.array([tile_id, h], dtype=np.float32)
        glTexSubImage2D(
            GL_TEXTURE_2D,  # Texture target
            0,  # Mipmap level (0 for base level)
            x,  # X position of the pixel
            y,  # Y position of the pixel
            1,  # Width of the region (1 pixel)
            1,  # Height of the region (1 pixel)
            GL_RG,  # Format of the data
            GL_FLOAT,  # Data type
            data  # Pixel data
        )

    def draw(self, player_id):
        self.shader.use_shader()
        self.__bind_texture()
        for asset_name in self.meshes:
            if len(self.tile_ids_draw[asset_name]) and asset_name != "Wall":
                self.shader.set_float("resourceId", self.asset_id[asset_name])

                if asset_name in unit_classes:
                    self.shader.set_float("isPlayer", player_id)

                self.meshes[asset_name].apply_transform_only(self.shader)
                count = len(self.tile_ids_draw[asset_name])
                location = self.meshes[asset_name].get_location()
                glDrawArraysInstanced(GL_TRIANGLES, location[0], location[1], count)

                self.shader.set_float("isPlayer", -1.0)

        if len(self.tile_ids_draw["Wall"]):
            self.shader.set_float("resourceId", self.asset_id["Wall"])
            self.shader.set_float("isWall", np.float32(1.0))
            count = len(self.tile_ids_draw["Wall"])
            location = self.meshes["Wall"].get_location()
            glDrawArraysInstanced(GL_TRIANGLES, location[0], location[1], count)
            self.shader.set_float("isWall", np.float32(0.0))

        self.shader.set_float("resourceId", np.float32(-1.0))

    def __get_mesh_at(self, triangles, position, tile_id):
        mesh = Mesh(self.vbo)
        count = 0
        for triangle in triangles:
            v1 = triangle[0]
            v2 = triangle[1]
            v3 = triangle[2]
            v1.color[1] = tile_id
            v2.color[1] = tile_id
            v3.color[1] = tile_id
            count += 3
            mesh.push_triangle(v1, v2, v3)
        mesh.rotation = [np.radians(90.0), 0, 0]
        mesh.position = position
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

    def read_ply(self, ply_file, scale):
        ply_data = PlyData.read(ply_file)

        vertices = ply_data['vertex']
        positions = np.array([(scale * v['x'], scale * v['y'], scale * v['z']) for v in vertices], dtype=np.float32)
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
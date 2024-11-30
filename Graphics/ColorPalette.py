import random
import numpy as np
from OpenGL.GL import *

class ColorPalette:
    def __init__(self, shader):
        self.shader = shader

        self.color_palette = [
            np.array([0.41, 0.74, 0.06], dtype=np.float32),     # Plains
            np.array([0.06, 0.74, 0.1], dtype=np.float32),      # Grassland
            np.array([0.74, 0.74, 0.32], dtype=np.float32),     # Shallow Water
            np.array([0.47, 0.47, 0.33], dtype=np.float32),     # Ocean
            np.array([0.4, 0.43, 0.43], dtype=np.float32),      # Mountain
            np.array([0.63, 0.78, 0.76], dtype=np.float32),     # Peaks
            np.array([0.0, 0.2, 0.5], dtype=np.float32)         # Water
        ]
        self.color_id = {
            (0.41, 0.74, 0.06): 0,  # Plains
            (0.06, 0.74, 0.1): 1,   # Grassland
            (0.74, 0.74, 0.32): 2,  # Shallow Water
            (0.47, 0.47, 0.33): 3,  # Ocean
            (0.4, 0.43, 0.43): 4,   # Mountain
            (0.63, 0.78, 0.76): 5,  # Peaks
            (0.0, 0.2, 0.5): 6      # Water
        }
        self.count = 7

        self.color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_1D, self.color_texture)
        glTexImage1D(GL_TEXTURE_1D, 0, GL_RGB32F, 1024, 0, GL_RGB, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.shader.use_shader()
        texture_location = glGetUniformLocation(self.shader.shader, "color_palette_t")

        glActiveTexture(GL_TEXTURE1)
        glUniform1i(texture_location, 1)

    def identify_color(self, color):
        key = (color[0], color[1], color[2])

        if key in self.color_id.keys():
            return self.color_id[key]

        self.color_palette.append(np.array(color, dtype=np.float32))
        self.color_id[key] = self.count
        self.count += 1
        return self.count - 1

    def flush_texture_to_shader(self):
        self.shader.use_shader()
        glBindTexture(GL_TEXTURE_1D, self.color_texture)

        for i in range(self.count):
            glTexSubImage1D(GL_TEXTURE_1D, 0, i, 1, GL_RGB, GL_FLOAT, self.color_palette[i])
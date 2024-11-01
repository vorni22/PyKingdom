from OpenGL.GL import *
import numpy as np
from Graphics.Buffers import DynamicVBO

class Mesh:
    def __init__(self, vbo:DynamicVBO):
        self.vbo = vbo
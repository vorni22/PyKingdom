from tkinter import BooleanVar

import pyrr
from OpenGL.GL import *
import numpy as np
from Graphics.Buffers import DynamicVBO

class Mesh:
    def __init__(self, vbo_ref:DynamicVBO, is_big:bool):
        self.vbo = vbo_ref
        self.mem_id = -1
        self.is_big = is_big
        self.model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

    def push_to_mem(self):
        return

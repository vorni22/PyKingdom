from OpenGL.GL import *
import numpy as np

class BasicVBO:

    # capacity -> max size of vbo in bytes
    # attributes -> list for the number of GL_FLOATS for each attribute
    def __init__(self, capacity:int):
        self.capacity = capacity
        self.currentSize = 0

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, capacity, None, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    # push a list of vertices at the end of the buffer
    def push_vertices(self, vertices:np.array):
        if self.currentSize + vertices.nbytes > self.capacity:
            return False

        glBufferSubData(GL_ARRAY_BUFFER, self.currentSize, vertices.nbytes, vertices)
        self.currentSize += vertices.nbytes

        return True

    #draw content of VBO
    def draw_vertices(self):
        if self.currentSize == 0:
            return
        glDrawArrays(GL_TRIANGLES, 0, self.currentSize)



from OpenGL.GL import *
import numpy as np

class MemBlock:
    def __init__(self, start, size):
        self.start = start
        self.size = size

    def __hash__(self):
        return hash((self.start, self.size))

class DynamicVBO:
    def __init__(self, capacity:int, size_of_vertex:int):
        self.capacity = capacity
        self.size_of_vertex = size_of_vertex

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, capacity, None, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

        self.free_memory = [
            MemBlock(0, capacity)
        ]

        self.used_memory = set()

    def add_vertices(self, vertices:np.array) -> int:
        #first try to find valid zone to place the vertices in GPU memory
        if vertices.nbytes == 0:
            return -1

        block_id = -1
        min_diff = self.capacity
        data_size = vertices.nbytes

        i = 0
        for block in self.free_memory:
            if block.size >= data_size and block.size - data_size < min_diff:
                min_diff = block.size - data_size
                block_id = i
            i += 1

        if block_id == -1:
            return -1

        new_used_block = MemBlock(self.free_memory[block_id].start, data_size)
        self.free_memory[block_id].size -= data_size
        self.free_memory[block_id].start += data_size

        if self.free_memory[block_id].size == 0:
            del self.free_memory[block_id]

        self.used_memory.add(new_used_block)

        glBufferSubData(GL_ARRAY_BUFFER, new_used_block.start, data_size, vertices)

        return new_used_block.start

    def free_vertices(self, block_id:int):
        target = None
        for block in self.used_memory:
            if block.start == block_id:
                target = block
                break

        if target is None:
            return

        self.used_memory.remove(target)

        insertion_index = 0
        for block in self.free_memory:
            if block.start < target.start:
                insertion_index+= 1
            else:
                break

        self.free_memory.insert(insertion_index, target)

        # coalesce the list
        if len(self.free_memory) == 1:
            return

        i = 0
        while i < len(self.free_memory) - 1:
            block_now = self.free_memory[i]
            block_next = self.free_memory[i + 1]

            if block_now.start + block_next.size == block_next.start:
                self.free_memory[i].size += block_next.size
                del self.free_memory[ + 1]
            else:
                i += 1

    def draw(self):
        for block in self.used_memory:
            first = block.start // self.size_of_vertex
            count = block.size // self.size_of_vertex
            glDrawArrays(GL_TRIANGLES, first, count)

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



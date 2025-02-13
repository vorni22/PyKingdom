from OpenGL.GL import *
import numpy as np

# @author Vornicescu Vasile
# Holds simple information about a memory block used as a node in a list
# It is used by DynamicVBO to allocate video memory
class MemBlock:
    def __init__(self, start, size):
        self.start = start
        self.size = size
        self.active = True

    def __hash__(self):
        return hash((self.start, self.size))

# @author Vornicescu Vasile
# Dynamic video memory allocator and wrapper around a VBO used by any mesh in the game
# Stores the data in video memory as a vertex
# Any vertex is expected to store position, normal and color (data)
class DynamicVBO:
    def __init__(self, capacity:int, size_of_vertex:int):
        self.capacity = capacity
        self.size_of_vertex = size_of_vertex

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, capacity, None, GL_DYNAMIC_DRAW)

        # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, size_of_vertex, ctypes.c_void_p(0))

        # normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, size_of_vertex, ctypes.c_void_p(12))

        # data
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, size_of_vertex, ctypes.c_void_p(24))

        self.free_memory = [
            MemBlock(0, capacity)
        ]

        self.used_memory = set()

        self.status = set()

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
        self.status.add(new_used_block.start)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
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
        self.status.remove(block_id)

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

    def set_vertices_status(self, block_id:int, status:bool):
        target = None
        for block in self.used_memory:
            if block.start == block_id:
                target = block
                break

        if target is None:
            return

        target.active = status

    def get_vertices_status(self, block_id:int):
        target = None
        for block in self.used_memory:
            if block.start == block_id:
                target = block
                break

        if target is None:
            return -1

        return target.active

    def get_block_locations(self, block_id:int):
        target = None
        for block in self.used_memory:
            if block.start == block_id:
                target = block
                break

        if target is None or not target.active:
            return None, None

        first = target.start // self.size_of_vertex
        count = target.size // self.size_of_vertex
        return first, count

    def draw_vertices(self, block_id:int):
        target = None
        for block in self.used_memory:
            if block.start == block_id:
                target = block
                break

        if target is None or not target.active:
            return

        first = target.start // self.size_of_vertex
        count = target.size // self.size_of_vertex
        glDrawArrays(GL_TRIANGLES, first, count)

    def draw(self):
        for block in self.used_memory:
            if not block.active:
                continue
            first = block.start // self.size_of_vertex
            count = block.size // self.size_of_vertex
            glDrawArrays(GL_TRIANGLES, first, count)

# @author Vornicescu Vasile
# A much simpler VBO used for testing early in the project and to store some really simple
# stuff currently.
class BasicVBO:

    # capacity -> size of vbo in bytes
    # vertices -> list of vertices that will be copied into vbo
    def __init__(self, capacity:int, vertices: np.array):
        self.capacity = capacity

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, capacity, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, ctypes.c_void_p(2 * vertices.itemsize))

    def draw_vertices(self):
        if self.capacity == 0:
            return
        glDrawArrays(GL_TRIANGLES, 0, 6)

    def bind(self):
        glBindVertexArray(self.vao)

    def unbind(self):
        glBindVertexArray(0)

import time
import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr

from Graphics.Buffers import DynamicVBO
from Graphics.Mesh import Mesh
from Graphics.Shaders import Shader

# set up pygame
pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)

# set up OpenGL
glClearColor(0.1, 0.2, 0.2, 1)
glEnable(GL_DEPTH_TEST)

# create shader and VBO

vertices = [
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
         0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,

        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
         0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
        -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,

        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,

         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
         0.5,  0.5, -0.5,  1.0,  0.0,  0.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
         0.5, -0.5,  0.5,  1.0,  0.0,  0.0,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,

        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
         0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,

        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
         0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0
]

num_cubes = 3
vbo_test = DynamicVBO(24 * len(vertices) * num_cubes, 24)

cubes = [Mesh(vbo_test), Mesh(vbo_test), Mesh(vbo_test)]

start = -2.0
for i in range(num_cubes):
    cubes[i].set_vertices(vertices)
    cubes[i].flush()
    cubes[i].position = [start + 2.0 * i, 0.0, -4.0]
    cubes[i].update_matrices()

shader = Shader("Shaders/frag.glsl", "Shaders/vert.glsl")
shader.use_shader()

projection_transform = pyrr.matrix44.create_perspective_projection(
    fovy = 45, aspect = 640/480,
    near = 0.1, far = 20, dtype=np.float32
)

view = pyrr.matrix44.create_look_at(np.array([0, 0, 2]), np.array([0, 0, -1]), np.array([0, 1, 0]))

shader.set_mat4("view", view)
shader.set_mat4("projection", projection_transform)

shader.set_3float("objectColor", 0.2, 0.4, 0.5)
shader.set_3float("lightColor", 0.9, 0.8, 0.8)
shader.set_float("ambientStrength", 0.6)
shader.set_float("specularStrength", 0.6)
shader.set_int("shininess", 8)

dt = 0.0
last_time = 0.0

# main loop
running = True

while running:
    current_time = time.time()
    dt = (current_time - last_time) * 1000.0
    last_time = current_time

    # check events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # refresh screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # update and draw cubes
    shader.use_shader()
    for i in range(num_cubes):
        cubes[i].rotation[i] += np.radians(0.05 * dt)
        cubes[i].update_matrices()
        cubes[i].draw(shader)

    pg.display.flip()

shader.del_shader()
pg.quit()


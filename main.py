import time
import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import glm
from anyio import current_time

from Graphics.Buffers import BasicVBO, DynamicVBO
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

vertices = np.array([
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
], dtype=np.float32)

vbo_test = DynamicVBO(vertices.nbytes * 3, 24)

vertices[::6] += 3.1
cube_1 = vbo_test.add_vertices(vertices)

vertices[::6] -= 1.1
cube_2 = vbo_test.add_vertices(vertices)

vbo_test.free_vertices(cube_2)

vertices[::6] -= 1.1
cube_3 = vbo_test.add_vertices(vertices)

shader = Shader("Shaders/frag.glsl", "Shaders/vert.glsl")
shader.use_shader()

projection_transform = pyrr.matrix44.create_perspective_projection(
    fovy = 45, aspect = 640/480,
    near = 0.1, far = 10, dtype=np.float32
)

view = pyrr.matrix44.create_look_at(np.array([0, 0, 2]), np.array([0, 0, -1]), np.array([0, 1, 0]))

shader.set_mat4("view", view)
shader.set_mat4("projection", projection_transform)

shader.set_3float("objectColor", 0.2, 0.4, 0.5)
shader.set_3float("lightColor", 0.9, 0.8, 0.8)
shader.set_float("ambientStrength", 0.6)
shader.set_float("specularStrength", 0.6)
shader.set_int("shininess", 8)

cube_rot = 0.0
cube_pos = [0.0, 0.0, -2.0]

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

    # update cube
    cube_rot += 0.05 * dt
    model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

    model_transform = pyrr.matrix44.multiply(
        m1=model_transform,
        m2=pyrr.matrix44.create_from_axis_rotation(
            axis=[0, 1, 0],
            theta=np.radians(cube_rot),
            dtype=np.float32
        )
    )

    model_transform = pyrr.matrix44.multiply(
        m1=model_transform,
        m2=pyrr.matrix44.create_from_translation(
            vec=np.array(cube_pos), dtype=np.float32
        )
    )

    # refresh screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    shader.use_shader()
    shader.set_mat4("model", model_transform)

    vbo_test.draw()

    pg.display.flip()


shader.del_shader()
pg.quit()


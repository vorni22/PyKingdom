import time
import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr
from Graphics.Buffers import DynamicVBO
from Graphics.Camera import Camera, CameraManager
from Graphics.Mesh import Mesh
from Graphics.Shaders import Shader
from Map_Generation.MapBuilder import MapMesh

WIDTH = 1200
HEIGHT = 600

# set up pygame
pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL|pg.DOUBLEBUF|pg.RESIZABLE)

pg.mouse.set_visible(False)  # Hide the mouse cursor
pg.event.set_grab(True)  # Grab the mouse for capturing movement

# set up OpenGL
glClearColor(0.6, 0.6, 0.6, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

# create shader and VBO

vertices = [
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.2, 0.4, 0.5,
         0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.2, 0.4, 0.5,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 0.2, 0.4, 0.5,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 0.2, 0.4, 0.5,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 0.2, 0.4, 0.5,
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.2, 0.4, 0.5,

        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.2, 0.4, 0.5,
         0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.2, 0.4, 0.5,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 0.2, 0.4, 0.5,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 0.2, 0.4, 0.5,
        -0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 0.2, 0.4, 0.5,
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.2, 0.4, 0.5,

        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, 0.2, 0.4, 0.5,

         0.5,  0.5,  0.5,  1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
         0.5,  0.5, -0.5,  1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
         0.5, -0.5,  0.5,  1.0,  0.0,  0.0, 0.2, 0.4, 0.5,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0, 0.2, 0.4, 0.5,

        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.2, 0.4, 0.5,
         0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.2, 0.4, 0.5,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 0.2, 0.4, 0.5,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 0.2, 0.4, 0.5,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 0.2, 0.4, 0.5,
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.2, 0.4, 0.5,

        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.2, 0.4, 0.5,
         0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.2, 0.4, 0.5,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 0.2, 0.4, 0.5,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 0.2, 0.4, 0.5,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 0.2, 0.4, 0.5,
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.2, 0.4, 0.5
]

num_cubes = 3

size_x = 20
size_y = 20
vertices_per_hex = 17 * 3
total_size = vertices_per_hex * size_x * size_y * 36

vbo_test = DynamicVBO(total_size, 36)
builder = MapMesh(size_x, size_y, vbo_test)

shader = Shader("Shaders/frag.glsl", "Shaders/vert.glsl")
shader.use_shader()

camera = Camera(np.array([0.0, 0.0, 0.0]), HEIGHT, WIDTH,
                45.0, 0.0, -90.0, np.array([0.0, 1.0, 0.0]), 0.1, 300.0)
cameraManager = CameraManager(camera)

shader.set_mat4("view", camera.get_view_matrix())
shader.set_mat4("projection", camera.get_perspective_matrix())

shader.set_3float("lightColor", 0.9, 0.8, 0.8)
shader.set_float("ambientStrength", 0.6)
shader.set_float("specularStrength", 0.6)
shader.set_int("shininess", 2)

dt = 0.0
last_time = 0.0

font = pg.font.SysFont("Arial", 24)

# main loop
running = True
mouse_visible = False
cnt = 0
sum_time = 0.0

while running:
    current_time = time.time()
    dt = (current_time - last_time) * 1000.0
    last_time = current_time

    cnt += 1
    sum_time += dt
    if sum_time >= 1000:
        fps = cnt
        sum_time = 0.0
        cnt = 0
        pg.display.set_caption(f"FPS = {fps}; pos = {camera.pos}")

    # check events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.VIDEORESIZE:
            HEIGHT = event.h
            WIDTH = event.w
            screen = pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL|pg.DOUBLEBUF|pg.RESIZABLE)
            camera.screen_height = HEIGHT
            camera.screen_width = WIDTH
            glViewport(0, 0, WIDTH, HEIGHT)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB:
                if mouse_visible:
                    mouse_visible = False
                    pg.mouse.set_visible(False)
                    pg.event.set_grab(True)
                else:
                    mouse_visible = True
                    pg.mouse.set_visible(True)
                    pg.event.set_grab(False)
            if event.key == pg.K_ESCAPE:
                running = False

    # refresh screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    cameraManager.every_frame(shader, dt, not mouse_visible)

    shader.use_shader()
    builder.draw(shader)

    pg.display.flip()

shader.del_shader()
pg.quit()


import time
import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr
from OpenGL.arrays.vbo import VBO

from Graphics.Buffers import DynamicVBO
from Graphics.Buffers import BasicVBO
from Graphics.Camera import Camera, CameraManager, StrategicCamera
from Graphics.Mesh import Mesh
from Graphics.Shaders import Shader
from Map_Generation.MapBuilder import MapMesh
from Graphics.FrameBuffer import FrameBuffer

WIDTH = 1200
HEIGHT = 600

# set up pygame
pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL|pg.DOUBLEBUF|pg.RESIZABLE)

# pg.mouse.set_visible(False)  # Hide the mouse cursor
# pg.event.set_grab(True)  # Grab the mouse for capturing movement
pg.mouse.set_visible(True)
pg.event.set_grab(False)

# set up OpenGL
glClearColor(0.6, 0.6, 0.6, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

glEnable(GL_BLEND)
glBlendColor(0.0, 0.0, 0.0, 0.75)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# create shader and VBO

fbo = FrameBuffer(WIDTH, HEIGHT)
if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")
fbo.unbind()

shader = Shader("Shaders/frag.glsl", "Shaders/vert.glsl")
shader.use_shader()

camera = Camera(np.array([0.0, 10.0, 40.0]), HEIGHT, WIDTH,
                45.0, -45.0, -90.0, np.array([0.0, 1.0, 0.0]), 0.1, 300.0)
#cameraManager = CameraManager(camera)
cameraManager = StrategicCamera(camera)

shader.set_mat4("view", camera.get_view_matrix())
shader.set_mat4("projection", camera.get_perspective_matrix())

shader.set_3float("lightColor", 0.9, 0.8, 0.8)
shader.set_float("ambientStrength", 0.5)
shader.set_float("highlight_id", -1.0)

size_x = 60
size_y = 40
vertices_per_hex = 17 * 3
total_size = vertices_per_hex * size_x * size_y * 36

vbo_test = DynamicVBO(2 * total_size + 6, 36)
builder = MapMesh(size_x, size_y, 0.0, 2.0, 10, vbo_test, shader)

dt = 0.0
last_time = 0.0

font = pg.font.SysFont("Arial", 24)

# main loop
running = True
cnt = 0
sum_time = 0.0

# FrameBuffers
quad_vertex = np.array([
    -1.0,  1.0, 0.0, 1.0,
    -1.0, -1.0, 0.0, 0.0,
     1.0, -1.0, 1.0, 0.0,

    -1.0,  1.0, 0.0, 1.0,
     1.0, -1.0, 1.0, 0.0,
     1.0,  1.0, 1.0, 1.0
], dtype=np.float32)


quad_vbo = BasicVBO(quad_vertex.nbytes, quad_vertex)

quad_shader = Shader("Shaders/quad_frag.glsl", "Shaders/quad_vert.glsl")
quad_shader.use_shader()
quad_shader.set_int("screen_texture", 0)

#FrameBuffers
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

    fbo.bind()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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
            fbo.resize(WIDTH, HEIGHT)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False

    shader.use_shader()
    cameraManager.every_frame(shader, dt, True)

    glBindVertexArray(builder.mesh.vbo.vao)
    builder.draw()

    # TEST
    mouse_x, mouse_y = pg.mouse.get_pos()
    mouse_y = HEIGHT - mouse_y

    pixel = builder.get_tile_on_mouse(mouse_x, mouse_y, fbo)

    if 0 <= pixel <= builder.size_x * builder.size_y:
        shader.set_float("highlight_id", pixel)
        #builder.set_visibility(pixel, 0.7)

    # STOP TEST

    fbo.unbind()
    glClear(GL_COLOR_BUFFER_BIT)

    quad_vbo.bind()
    quad_shader.use_shader()
    glBindTexture(GL_TEXTURE_2D, fbo.color_texture)
    quad_vbo.draw_vertices()

    pg.display.flip()

shader.del_shader()
pg.quit()


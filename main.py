import time
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import pyrr

from Graphics.Buffers import DynamicVBO
from Graphics.Buffers import BasicVBO
from Graphics.Camera import Camera, CameraManager, StrategicCamera
from Graphics.ColorPalette import ColorPalette
from Graphics.Mesh import Mesh
from Graphics.Shaders import Shader
from Map_Generation.AssetsManager import AssetsManager
from Map_Generation.MapBuilder import MapMesh
from Graphics.FrameBuffer import FrameBuffer
from Map_Generation.MapInterface import MapInterface
from UI.MainMenu import MainMenu
from Game_UI.PanelInterface import PanelInterface

# set up pygame
pg.init()

def surface_to_texture(surface, texture_id):
    if surface is not None:
        texture_data = pg.image.tostring(surface, "RGB", True)
    else:
        texture_data = None
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)

def cursor_in_rect(position, rect):
    return rect.x <= position[0] <= rect.x + rect.width and rect.y <= position[1] <= rect.y + rect.height


pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

screen = pg.display.set_mode((0, 0), pg.OPENGL | pg.DOUBLEBUF)
size = pg.display.get_surface().get_size()
WIDTH = size[0]
HEIGHT = size[1]
# print(WIDTH, HEIGHT)

# set up OpenGL
glClearColor(0.6, 0.6, 0.6, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

glEnable(GL_BLEND)
glBlendColor(0.0, 0.0, 0.0, 0.75)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
# pg.mouse.set_visible(False)  # Hide the mouse cursor
# pg.event.set_grab(True)  # Grab the mouse for capturing movement
pg.mouse.set_visible(True)
pg.event.set_grab(False)

# create shader and VBO
fbo = FrameBuffer(WIDTH, HEIGHT)
if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")
fbo.unbind()

shader = Shader("Shaders/frag.glsl", "Shaders/vert.glsl", True)
shader.use_shader()

camera = Camera(np.array([0.0, 10.0, 40.0]), HEIGHT, WIDTH,
                    45.0, -45.0, -90.0, np.array([0.0, 1.0, 0.0]), 0.1, 300.0)
# cameraManager = CameraManager(camera)
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

vbo_test = DynamicVBO(2 * total_size + 6 + 30 * (2 ** 20), 36)
map_interface = MapInterface(vbo_test, shader, fbo)

dt = 0.0
last_time = 0.0

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

quad_shader = Shader("Shaders/quad_frag.glsl", "Shaders/quad_vert.glsl", False)
quad_shader.use_shader()
quad_shader.set_int("screenTexture", 0)

texture_data = glGenTextures(1)
surface_to_texture(None, texture_data)

main_menu = MainMenu(WIDTH, HEIGHT)

pbo = glGenBuffers(1)
glBindBuffer(GL_PIXEL_PACK_BUFFER, pbo)
glBufferData(GL_PIXEL_PACK_BUFFER, WIDTH * HEIGHT * 3, None, GL_STREAM_READ)
glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

game_state = 0

clicked = False
sw = False

panels = PanelInterface(WIDTH, HEIGHT)

f = True

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

    mouse_pos = pg.mouse.get_pos()

    # check events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.mouse.get_pressed()[0]:
                if main_menu.check_input_play(mouse_pos):
                    main_menu.set_game_state(1)
                    continue
                if main_menu.check_input_quit(mouse_pos):
                    running = False
                if main_menu.check_input_dropdown(mouse_pos):
                    main_menu.check_dropdown(mouse_pos)
                    if main_menu.check_input_start(mouse_pos):
                        main_menu.set_game_state(2)
                        continue
                if main_menu.get_game_state() == 2:
                    if not clicked:
                        clicked = True
                        sw = True
                    else:
                        break

    shader.use_shader()
    cameraManager.every_frame(shader, dt, True)

    map_interface.every_frame()

    if map_interface.activated:
        mouse_y = HEIGHT - mouse_pos[1]
        mouse_x = mouse_pos[0]
        tile_id = map_interface.tile_on_mouse(mouse_x, mouse_y)
        if not 0 <= tile_id < mouse_x * mouse_y and sw:
            clicked = False
        elif 0 <= tile_id < mouse_x * mouse_y and sw:
            panels.city_panel.change_text("tile_id: " + str(tile_id))

    sw = False
    fbo.unbind()

    fbo.bind()
    glReadBuffer(GL_COLOR_ATTACHMENT0)

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    glBindBuffer(GL_PIXEL_PACK_BUFFER, pbo)

    glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, 0)

    ptr = glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY)
    screen_surf = pg.image.frombuffer(ctypes.string_at(ptr, WIDTH * HEIGHT * 3), (WIDTH, HEIGHT), "RGB")
    glUnmapBuffer(GL_PIXEL_PACK_BUFFER)
    screen_surf = pg.transform.flip(screen_surf, False, True)

    glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

    fbo.unbind()

    # UI here
    if main_menu.get_game_state() != 2:
        main_menu.draw_menu_buttons(screen_surf, mouse_pos)
    else:
        map_interface.activate(size_x, size_y, 4, 0)
        if clicked:
            panels.city_panel.draw_surf(screen_surf, mouse_pos)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if pg.mouse.get_pressed()[0]:
                        if panels.city_panel.buy_units_button.check_for_input(mouse_pos):
                            panels.city_panel.buy_units = True
                        if panels.city_panel.buy_buildings_button.check_for_input(mouse_pos):
                            panels.city_panel.buy_buildings = True
                        panels.city_panel.close_surf(mouse_pos, screen_surf)
                        panels.city_panel.return_to_init_surf(mouse_pos, screen_surf)
                        clicked = panels.city_panel.clicked

    # UI end here

    surface_to_texture(screen_surf, texture_data)

    glClear(GL_COLOR_BUFFER_BIT)

    quad_vbo.bind()
    quad_shader.use_shader()
    glBindTexture(GL_TEXTURE_2D, texture_data)
    quad_vbo.draw_vertices()

    pg.display.flip()


shader.del_shader()
pg.quit()




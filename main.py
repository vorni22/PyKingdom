import time
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import random

from Graphics.Buffers import DynamicVBO
from Graphics.Buffers import BasicVBO
from Graphics.Camera import Camera, StrategicCamera
from Graphics.Shaders import Shader
from Graphics.FrameBuffer import FrameBuffer
from Map_Generation.MapInterface import MapInterface
from UI.MainMenu import MainMenu
from Game_UI.PanelInterface import PanelInterface

# set up pygame
pg.init()

pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

screen = pg.display.set_mode((0, 0), pg.OPENGL | pg.DOUBLEBUF | pg.HWSURFACE)
size = pg.display.get_surface().get_size()
WIDTH = size[0]
HEIGHT = size[1]

# set up OpenGL
glClearColor(0.6, 0.6, 0.6, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

glEnable(GL_BLEND)
glBlendColor(0.0, 0.0, 0.0, 0.75)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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

size_x = 48
size_y = 36
vertices_per_hex = 17 * 3
total_size = vertices_per_hex * size_x * size_y * 36

vbo_test = DynamicVBO(2 * total_size + 6 + 30 * (2 ** 20), 36)
map_interface = MapInterface(vbo_test, shader, fbo)
game = None

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
fbo.surface_to_texture(None, texture_data)

main_menu = MainMenu(WIDTH, HEIGHT)

pbo = glGenBuffers(1)
glBindBuffer(GL_PIXEL_PACK_BUFFER, pbo)
glBufferData(GL_PIXEL_PACK_BUFFER, WIDTH * HEIGHT * 3, None, GL_STREAM_READ)
glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

panels = PanelInterface(WIDTH, HEIGHT)

objects = [0, 1, 2]
tile = None
unit = None
city = None
sw = True
tile_id = -1
purchasable = None
tile_line = -1
tile_column = -1
tile_l = -1
tile_c = -1
city_pos = None

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
                main_menu.set_game_state(2)
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.mouse.get_pressed()[0]:
                action = main_menu.check_input_main_menu(mouse_pos)
                if action == 1:
                    continue
                elif action == 2:
                    mouse_y = HEIGHT - mouse_pos[1]
                    mouse_x = mouse_pos[0]
                    tid = map_interface.tile_on_mouse(mouse_x, mouse_y)
                    tile_line = tid % size[1]
                    tile_column = tid // size[1]
                    if map_interface.activated and not panels.clicked:
                        if not panels.cursor_is_on_ui(mouse_pos) and not panels.unit_is_moving:
                            objects = game.identify_object(tile_line, tile_column)
                            tile = game.get_tile(tile_line, tile_column)
                            unit_t = game.get_unit_actions(tile_line, tile_column)
                            purchasable = game.get_city_actions(tile_line, tile_column)
                            unit_info = game.get_unit_information(tile_line, tile_column)
                            unit = (unit_t, tile_line, tile_column, unit_info)
                            city = game.get_city_information(tile_line, tile_column)
                            city_pos = (tile_line, tile_column)
                    if game.is_player_turn:
                        panels.end_turn(mouse_pos, game.end_turn)
                    panels.update_interface(game.move_unit, unit, (tile_line, tile_column), game.purchase_district_with_production, game.purchase_district_with_gold)
                elif action == 0:
                    running = False


    shader.use_shader()
    cameraManager.every_frame(shader, dt, True)

    map_interface.every_frame(panels.cursor_is_on_ui)

    if map_interface.activated:
        mouse_y = HEIGHT - mouse_pos[1]
        mouse_x = mouse_pos[0]
        tile_id = map_interface.tile_on_mouse(mouse_x, mouse_y)
        panels.click_is_out_of_map(tile_id, mouse_x, mouse_y)


    panels.set_update_every_frame(False)
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
    if main_menu.get_game_state() != 3:
        main_menu.draw_menu_buttons(screen_surf, mouse_pos)
    else:
        size, num_players = main_menu.get_game_constants()
        seed = random.randint(1, 10000000)
        ret = map_interface.activate(size[0], size[1], num_players, seed, cameraManager)
        if ret is not None:
            game = ret
        if not game.is_player_turn:
            game.start_turn()

        panels.status_panel.draw(screen_surf, game.get_player_information)
        if panels.end_turn_button.rendered or sw:
            panels.end_turn_button.draw(screen_surf)
            sw = False
        panels.draw_loading_screen(screen_surf)
        if panels.clicked:
            if game.is_player_turn:
                panels.draw_interface(screen_surf, mouse_pos, objects, tile, unit, purchasable, city)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        main_menu.set_game_state(2)
                if event.type == pg.MOUSEBUTTONDOWN:
                    if pg.mouse.get_pressed()[0]:
                        if game.is_player_turn:
                            if not panels.cursor_is_on_ui(mouse_pos):
                                mouse_y = HEIGHT - mouse_pos[1]
                                mouse_x = mouse_pos[0]
                                tid = map_interface.tile_on_mouse(mouse_x, mouse_y)
                                tile_l = tid % size[1]
                                tile_c = tid // size[1]
                            panels.close_interface(mouse_pos, screen_surf, unit, game.settle_city)
                            if panels.unit_is_moving:
                                panels.clicks_unit_is_moving += 1
                            panels.move_units(unit, mouse_pos, screen_surf, city_pos[0], city_pos[1], game.move_unit, game)
                            panels.count_clicks()
                            panels.buy_units(city_pos[0], city_pos[1], mouse_pos, game, city)
                            panels.buy_buildings(city_pos[0], city_pos[1], mouse_pos, game, city)
                            panels.buy_district_buildings(city_pos[0], city_pos[1], mouse_pos, game, city, purchasable)
                            panels.buy_districts(city_pos[0], city_pos[1], mouse_pos, game, city, tile_l, tile_c)

    # UI end here

    fbo.surface_to_texture(screen_surf, texture_data)

    glClear(GL_COLOR_BUFFER_BIT)

    quad_vbo.bind()
    quad_shader.use_shader()
    glBindTexture(GL_TEXTURE_2D, texture_data)
    quad_vbo.draw_vertices()

    pg.display.flip()


shader.del_shader()
pg.quit()



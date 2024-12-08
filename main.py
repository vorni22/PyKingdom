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
from UI.Button import Button
from UI.DropDownButton import DropDownButton

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


pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

screen = pg.display.set_mode((0, 0), pg.OPENGL | pg.DOUBLEBUF)
size = pg.display.get_surface().get_size()
WIDTH = size[0]
HEIGHT = size[1]
print(WIDTH, HEIGHT)

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
map_interface = MapInterface(size_x, size_y, vbo_test, shader, fbo)

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

background = pg.image.load("Assets/MainMenu/Background.jpg")
font = "Assets/MainMenu/Font.ttf"
play_button = pg.image.load("Assets/MainMenu/Play Rect.png")
quit_button = pg.image.load("Assets/MainMenu/Quit Rect.png")

options = ["Option 1", "Option 2", "Option 3"]
options1 = ["2", "3", "4", "5"]

button_play = Button(background=play_button, x_coord=0.4*WIDTH, y_coord=0.27*HEIGHT, text_input="PLAY", font=font, color="White", hover_color="Gray", size=75)
button_quit = Button(background=quit_button, x_coord=0.4*WIDTH, y_coord=0.55*HEIGHT, text_input="QUIT", font=font, color="White", hover_color="Gray", size=75)
button_map_size = DropDownButton(background=quit_button, x_coord=WIDTH // 4, y_coord=HEIGHT // 4, text_input="MAP", font=font, color="White",
                                 hover_color="Gray", size=75, options=options, options_background_color=(169, 169, 169))
button_number_players = DropDownButton(background=quit_button, x_coord=3 * WIDTH // 4, y_coord=HEIGHT // 4, text_input="PLAYERS", font=font, color="White",
                                 hover_color="Gray", size=75, options=options1, options_background_color=(169, 169, 169))
button_start_game = Button(background=play_button, x_coord=WIDTH // 2, y_coord=HEIGHT // 2, text_input="START GAME", font=font, color="White", hover_color="Gray", size=75)


pbo = glGenBuffers(1)
glBindBuffer(GL_PIXEL_PACK_BUFFER, pbo)
glBufferData(GL_PIXEL_PACK_BUFFER, WIDTH * HEIGHT * 3, None, GL_STREAM_READ)
glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

game_state = 0

fnt_size = 100
fnt = pg.font.Font(None, fnt_size)
black = (0, 0, 0)
blue = (0, 0, 255, 128)
text = "LOH"
text_color = black

text_r = fnt.render(text, True, text_color)
rect_center_x = 3 * WIDTH // 4
rect_center_y = 3 * HEIGHT // 4
rect_width = WIDTH - rect_center_x
rect_height = HEIGHT - rect_center_y
transparent_surface = pg.Surface((rect_width, rect_height), pg.SRCALPHA)
text_rect = text_r.get_rect()
text_rect.center = (rect_center_x + rect_width // 2, rect_center_y + rect_height // 2)

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

    clicked = False
    mouse_pos = pg.mouse.get_pos()

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
        if event.type == pg.MOUSEBUTTONDOWN:
            if button_play.check_for_input(mouse_pos) and game_state == 0:
                game_state = 1
                continue
            if button_quit.check_for_input(mouse_pos) and game_state == 0:
                running = False
            if game_state == 1:
                button_map_size.check_input(mouse_pos)
                button_number_players.check_input(mouse_pos)
                if button_start_game.check_for_input(mouse_pos):
                    game_state = 2
                    continue


    shader.use_shader()
    cameraManager.every_frame(shader, dt, True)

    map_interface.every_frame()

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
    if game_state == 0:
        screen_surf.blit(background, (0, 0))
        menu_text = button_play.get_font(100).render("PyKingdom", True, "#ffd700")
        menu_rect = menu_text.get_rect(center=(0.5*WIDTH, 0.09*HEIGHT))

        screen_surf.blit(menu_text, menu_rect)

        button_play.change_color(mouse_pos)
        button_play.update(screen_surf)

        button_quit.change_color(mouse_pos)
        button_quit.update(screen_surf)
    elif game_state == 1:
        screen_surf.blit(background, (0, 0))
        menu_text = button_play.get_font(100).render("PyKingdom", True, "#ffd700")
        menu_rect = menu_text.get_rect(center=(0.5*WIDTH, 0.09*HEIGHT))
        screen_surf.blit(menu_text, menu_rect)

        button_map_size.draw_dropdown(screen_surf, mouse_pos)
        button_map_size.update(screen_surf)
        button_map_size.change_color(mouse_pos)

        button_number_players.draw_dropdown(screen_surf, mouse_pos)
        button_number_players.update(screen_surf)
        button_number_players.change_color(mouse_pos)

        button_start_game.change_color(mouse_pos)
        button_start_game.update(screen_surf)
    else:
        map_interface.activate()

        transparent_surface.fill(blue)

        screen_surf.blit(transparent_surface, (rect_center_x, rect_center_y))

        screen_surf.blit(text_r, text_rect)

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
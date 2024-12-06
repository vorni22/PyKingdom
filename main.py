import ctypes
import time
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import pyrr
import sys

from Graphics.Buffers import DynamicVBO
from Graphics.Buffers import BasicVBO
from Graphics.Camera import Camera, CameraManager, StrategicCamera
from Graphics.ColorPalette import ColorPalette
from Graphics.Mesh import Mesh
from Graphics.Shaders import Shader
from Map_Generation.AssetsManager import AssetsManager
from Map_Generation.MapBuilder import MapMesh
from Graphics.FrameBuffer import FrameBuffer
from UI.Button import Button

WIDTH = 1200
HEIGHT = 600

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


def play():
    global HEIGHT, WIDTH
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL | pg.DOUBLEBUF)
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

    color_palette = ColorPalette(shader)
    assets = AssetsManager(vbo_test, color_palette, shader, size_x * size_y)
    builder = MapMesh(size_x, size_y, 0.0, 2.0, 10, vbo_test, shader, assets)
    color_palette.flush_texture_to_shader()

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

    font_size = 100
    font = pg.font.Font(None, font_size)
    black = (0, 0, 0)
    text = "LOH"
    text_color = black
    text_rendered = font.render(text, True, text_color)
    text_rect = text_rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    texture_data = glGenTextures(1)
    surface_to_texture(None, texture_data)

    pbo = glGenBuffers(1)
    glBindBuffer(GL_PIXEL_PACK_BUFFER, pbo)
    glBufferData(GL_PIXEL_PACK_BUFFER, WIDTH * HEIGHT * 3, None, GL_STREAM_READ)
    glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

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

        if 0 <= pixel < builder.size_x * builder.size_y:
            shader.set_float("highlight_id", pixel)
            #builder.add_object_on_tile(pixel, "Theatre Square")

        # STOP TEST

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

        # 3. Unbind the PBO
        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        fbo.unbind()

        # UI here

        screen_surf.blit(text_rendered, text_rect)

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
    sys.exit()

def main_menu():
    global WIDTH, HEIGHT
    background = pg.image.load("Assets/MainMenu/Background.jpg")
    font = "Assets/MainMenu/Font.ttf"
    play_button = pg.image.load("Assets/MainMenu/Play Rect.png")
    quit_button = pg.image.load("Assets/MainMenu/Quit Rect.png")

    screen = pg.display.set_mode((WIDTH, HEIGHT))

    button_play = Button(background=play_button, x_coord=750, y_coord=300, text_input="PLAY", font=font, color="White", hover_color="Gray", size=75)
    button_quit = Button(background=quit_button, x_coord=750, y_coord=600, text_input="QUIT", font=font, color="White", hover_color="Gray", size=75)

    running = True
    while running:
        screen.blit(background, (0, 0))

        mouse_pos = pg.mouse.get_pos()

        menu_text= button_play.get_font(100).render("PyKingdom", True, "#ffd700")
        menu_rect = menu_text.get_rect(center=(750, 100))

        screen.blit(menu_text, menu_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if button_play.check_for_input(mouse_pos):
                    play()
                if button_quit.check_for_input(mouse_pos):
                    running = False

        button_play.change_color(mouse_pos)
        button_play.update(screen)

        button_quit.change_color(mouse_pos)
        button_quit.update(screen)

        pg.display.flip()

    pg.quit()

main_menu()
import pygame as pg
import numpy as np
import pyrr
import Shaders

# @author Vornicescu Vasile
# An object that store all the relevant information about a camera
# Does not include actual camera controls, just information and methods
# that can modify the camera. It is able to provide relevant information
# such as the view and perspective matrix to the shader
class Camera:
    def __init__(self, pos,
                 screen_height, screen_width,
                 fov, pitch, yaw, word_up,
                 near_plane, far_plane):
        self.pos = pos
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.fov = fov
        self.pitch = pitch
        self.yaw = yaw
        self.word_up = word_up
        self.near_plane = near_plane
        self.far_plane = far_plane

        self.front = np.array([0.0 ,0.0, 0.0])
        self.right = np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 0.0, 0.0])

        self.camera_update()

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(eye = self.pos, target = self.pos + self.front, up = self.up, dtype = np.float32)

    def get_perspective_matrix(self):
        return pyrr.matrix44.create_perspective_projection(
            fovy = self.fov, aspect = self.screen_width / self.screen_height,
            near = self.near_plane, far = self.far_plane, dtype = np.float32
        )

    def camera_move(self, front:float, right:float, up:float):
        self.pos += self.right * right + self.front * front + self.up * up

    def camera_move_globally(self, x_axis:float, y_axis:float, z_axis:float):
        self.pos += np.array([x_axis, y_axis, z_axis])

    def camera_rotate(self, delta_yaw: float, delta_pitch: float, constrain_pitch: bool, constrain_val: float):
        self.pitch += delta_pitch
        self.yaw += delta_yaw

        if constrain_pitch:
            constrain_val = abs(constrain_val)
            if self.pitch > constrain_val:
                pitch = constrain_val
            if self.pitch < -constrain_val:
                pitch = -constrain_val

    def camera_update(self):
        self.front[0] = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.front[1] = np.sin(np.radians(self.pitch))
        self.front[2] = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.front = self.front / np.linalg.norm(self.front)

        self.right = np.cross(self.front, self.word_up)
        self.right = self.right / np.linalg.norm(self.right)

        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)

class CameraManager:
    def __init__(self, camera: Camera):
        self.camera = camera
        self.camera_speed = 0.01

        self.__last_pos_x = 0.0
        self.__last_pos_y = 0.0
        self.first_update = True

    def __process_input(self, dt: float):
        keys = pg.key.get_pressed()

        camera_speed = self.camera_speed * dt
        camera_sensitivity = 0.1 * dt

        dx, dy = pg.mouse.get_rel()
        x = 0.0
        z = 0.0

        if self.first_update:
            self.first_update = False
            dx = 0
            dy = 0

        yaw = dx * camera_sensitivity
        pitch = - dy * camera_sensitivity

        if keys[pg.K_w]:
            z = camera_speed
        if keys[pg.K_s]:
            z = -camera_speed
        if keys[pg.K_d]:
            x = camera_speed
        if keys[pg.K_a]:
            x = -camera_speed
        if keys[pg.K_SPACE]:
            self.camera.pos[1] += camera_speed
        if keys[pg.K_LSHIFT]:
            self.camera.pos[1] -= camera_speed

        self.camera.camera_rotate(yaw, pitch, True, 89.0)
        self.camera.camera_move(z, x, 0)

    def every_frame(self, shader: Shaders, dt: float, move_camera: bool):
        if move_camera:
            self.__process_input(dt)
        self.camera.camera_update()
        shader.set_mat4("view", self.camera.get_view_matrix())
        shader.set_mat4("projection", self.camera.get_perspective_matrix())

# @author Vornicescu Vasile
# Simple camera controller that is wrapping the Camera class to provide
# camera movement from keyboard input
class StrategicCamera:
    def __init__(self, camera: Camera):
        self.camera = camera
        self.camera_speed = 0.01

    def __process_input(self, dt: float):
        keys = pg.key.get_pressed()

        camera_speed = self.camera_speed * dt
        x = y = z = 0

        if keys[pg.K_s]:
            z = camera_speed
        if keys[pg.K_w]:
            z = -camera_speed
        if keys[pg.K_d]:
            x = camera_speed
        if keys[pg.K_a]:
            x = -camera_speed
        if keys[pg.K_SPACE]:
            y = camera_speed
        if keys[pg.K_LSHIFT]:
            y = -camera_speed

        self.camera.camera_move_globally(x, y, z)

    def every_frame(self, shader: Shaders, dt: float, move_camera: bool):
        if move_camera:
            self.__process_input(dt)
        self.camera.camera_update()
        shader.set_mat4("view", self.camera.get_view_matrix())
        shader.set_mat4("projection", self.camera.get_perspective_matrix())
import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

class Shader:
    def __init__(self, fragment_shader_path:str, vertex_shader_path:str):
        with open(vertex_shader_path, 'r') as f:
            vertex_src = f.readlines()

        with open(fragment_shader_path, 'r') as f:
            fragment_src = f.readlines()

        self.shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                     compileShader(fragment_src, GL_FRAGMENT_SHADER))

        glValidateProgram(self.shader)
        is_valid = glGetProgramiv(self.shader, GL_VALIDATE_STATUS)
        if not is_valid:
            info_log = glGetProgramInfoLog(self.shader)
            print(f"Shader program validation failed: {info_log}")

    def del_shader(self):
        glDeleteProgram(self.shader)

    def use_shader(self):
        glUseProgram(self.shader)

    def set_int(self, uniform_name:str, value:int):
        glUniform1i(glGetUniformLocation(self.shader, uniform_name), value)

    def set_float(self, uniform_name:str, value:float):
        glUniform1f(glGetUniformLocation(self.shader, uniform_name), value)

    def set_3float(self, uniform_name:str, x, y, z):
        glUniform3f(glGetUniformLocation(self.shader, uniform_name), x , y, z)

    def set_mat3(self, uniform_name:str, mat3):
        glUniformMatrix3fv(glGetUniformLocation(self.shader, uniform_name), 1, GL_FALSE, mat3)

    def set_mat4(self, uniform_name:str, mat4):
        glUniformMatrix4fv(glGetUniformLocation(self.shader, uniform_name),1, GL_FALSE, mat4)





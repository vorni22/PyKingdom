import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

class Shader:
    def __init__(self, fragment_shader_path:str, vertex_shader_path:str, main_shader):
        with open(vertex_shader_path, 'r') as f:
            vertex_src = f.readlines()

        with open(fragment_shader_path, 'r') as f:
            fragment_src = f.readlines()

        # Create and compile vertex shader
        vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
        # Check for compilation errors
        if vertex_shader == 0:
            print("Vertex Shader Compilation Failed!")
            print(glGetShaderInfoLog(vertex_shader))
        else:
            print("Vertex Shader Compilation Successful!")

        fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
        # Check for compilation errors
        if fragment_shader == 0:
            print("Fragment Shader Compilation Failed!")
            print(glGetShaderInfoLog(fragment_shader))
        else:
            print("Fragment Shader Compilation Successful!")

        #self.shader = compileProgram(vertex_shader, fragment_shader)
        if main_shader:
            self.shader = glCreateProgram()
            glAttachShader(self.shader, vertex_shader)
            glAttachShader(self.shader, fragment_shader)
            # Link the program
            glLinkProgram(self.shader)

            # Pre-bind texture units
            glUseProgram(self.shader)
            glUniform1i(glGetUniformLocation(self.shader, "uVisibilityTexture"), 0)  # Texture unit 0
            glUniform1i(glGetUniformLocation(self.shader, "color_palette_t"), 1)  # Texture unit 1
            glUniform1i(glGetUniformLocation(self.shader, "uResourcesTexture"), 2) # Texture unit 2
        else:
            self.shader = compileProgram(vertex_shader, fragment_shader)

        success = glGetProgramiv(self.shader, GL_LINK_STATUS)
        if not success:
            info_log = glGetProgramInfoLog(self.shader)
            print(f"Program linking failed: {info_log.decode()}")
        else:
            print("Program compiled and linked successfully!")

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





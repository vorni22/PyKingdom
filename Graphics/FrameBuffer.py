from OpenGL.GL import *

class FrameBuffer:
    def __init__(self, width:int, height:int):
        self.fbo = glGenFramebuffers(1)
        self.width = width
        self.height = height
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        self.__gen_texture()
        self.__gen_renderbuffer()


    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glEnable(GL_DEPTH_TEST)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glDisable(GL_DEPTH_TEST)

    def resize(self, rwidth, rheight):
        self.width = rwidth
        self.height = rheight

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        glDeleteTextures(1, [self.texture])
        self.__gen_texture()

        glDeleteRenderbuffers(1, [self.rbo])
        self.__gen_renderbuffer()

    def __gen_texture(self):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture, 0)

    def __gen_renderbuffer(self):
        self.rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.rbo)


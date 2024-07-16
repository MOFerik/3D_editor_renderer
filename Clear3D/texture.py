import moderngl as mgl
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.EXT.texture_filter_anisotropic import GL_TEXTURE_MAX_ANISOTROPY_EXT


class Texture:
    def __init__(self, ctx):
        self.ctx = ctx
        self.textures = {}
        self.textures[0] = self.get_texture([100, 100, 100])
        self.textures[1] = self.get_texture([150, 150, 150])
        self.textures[2] = self.get_texture([0, 0, 255])

    def get_texture(self, col):
        texture_data = np.ones((1, 1, 3), dtype=np.uint8) * col
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 32.0)
        glGenerateMipmap(GL_TEXTURE_2D)
        return texture

    def destroy(self):
        [tex.release() for tex in self.textures.values()]
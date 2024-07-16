from vao import VAO
from texture import Texture


class Mesh:
    def __init__(self, app, vao_name):
        self.app = app
        self.vao = VAO(app.ctx, vao_name)
        self.texture = Texture(app.ctx)

    def destroy(self):
        self.vao.destroy()
        self.texture.destroy()
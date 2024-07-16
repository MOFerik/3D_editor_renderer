from vbo import VBO
from shader_program import ShaderProgram


class VAO:
    def __init__(self, ctx, name):
        self.ctx = ctx
        self.vbo_main = VBO(ctx, name)
        self.program = ShaderProgram(ctx)
        self.vbo = self.vbo_main.vbo
        self.vao = self.get_vao(program=self.program.programs['default'], vbo=self.vbo)
        self.vao_out = self.get_vao(program=self.program.programs['outline'], vbo=self.vbo)

    def get_vao(self, program, vbo):
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)])
        return vao

    def change_vert(self, vertices):
        self.vbo.change_vertices(vertices)
        self.vao = self.get_vao(program=self.program.programs['default'], vbo=self.vbo)
        self.vao_out = self.get_vao(program=self.program.programs['outline'], vbo=self.vbo)

    def get_vert(self, name):
        return self.vbo.vertices

    def destroy(self):
        self.vbo.destroy()
        self.program.destroy()

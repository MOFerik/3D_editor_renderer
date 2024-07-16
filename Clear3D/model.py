import moderngl as mgl
import numpy as np
import math
import glm
import glfw
from OpenGL.GL import *
from mesh import *


class BaseModel:
    def __init__(self, app, vao_name, tex_id=0, pos=(0, 0, 0), scale=(1, 1, 1), ox=(0, 0, -1), oy=(1, 0, 0), oz=(0, 1, 0), vertices=np.array(0)):
        self.app = app
        self.pos = pos
        self.scale = scale
        self.ox = ox
        self.oy = oy
        self.oz = oz
        self.mesh = Mesh(self.app, vao_name)
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)
        self.tex_id = tex_id
        self.or_vao = self.mesh.vao
        self.vao_name = vao_name
        self.or_vao.vao = self.mesh.vao.vao
        self.vao = self.or_vao.vao
        self.outline_vao = self.mesh.vao.vao_out
        self.program = self.vao.program
        self.outline_program = self.outline_vao.program
        self.camera = self.app.camera
        self.texture = self.mesh.texture.textures[tex_id]
        self.vert_texture = self.mesh.texture.textures[1]
        self.selected_vert = []
        self.buff_pos = pos
        self.buff_vert_pos = glm.vec3(0, 0, 0)
        if vertices.any() == 0:
            self.vertices = self.get_vertices()
        else:
            self.vertices = vertices
            self.or_vao.change_vert(self.vertices)
        self.on_init()

    def update(self): ...

    # Обновление матрицы объекта
    def get_model_matrix(self):
        m_model = glm.mat4()
        # Положение
        m_model = glm.translate(m_model, self.pos)
        # Поворот
        if self.ox[0] > 1.0:
            self.ox[0] = 1
        if 0 <= self.ox[2]:
            m_model = glm.rotate(m_model, math.asin(self.ox[0]), glm.vec3(0, 1, 0))
        else:
            m_model = glm.rotate(m_model, -math.asin(self.ox[0]), glm.vec3(0, 1, 0))
        if self.oy[1] > 1.0:
            self.oy[1] = 1
        if 0 <= self.oy[0]:
            m_model = glm.rotate(m_model, -math.asin(self.oy[1]), glm.vec3(0, 0, -1))
        else:
            m_model = glm.rotate(m_model, math.asin(self.oy[1]), glm.vec3(0, 0, -1))
        if self.oz[2] > 1.0:
            self.oz[2] = 1
        if 0 <= self.oz[1]:
            m_model = glm.rotate(m_model, -math.asin(self.oz[2]), glm.vec3(1, 0, 0))
        else:
            m_model = glm.rotate(m_model, math.asin(self.oz[2]), glm.vec3(1, 0, 0))
        # Масштабирование
        m_model = glm.scale(m_model, glm.vec3(np.abs(self.scale[0]), np.abs(self.scale[2]), np.abs(self.scale[1])))
        return m_model

    # Обновление матрицы выделения
    def get_outline_model_matrix(self, m_model):
        outline_model = glm.scale(m_model, (1, 1, 1))
        return outline_model

    # Проверка на попадание по клик мыши
    def contains_point(self, ray_origin, ray_direction):
        corners = np.array([[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
                    [-1, 1, -1], [-1, -1, -1], [1, -1, -1], [1, 1, -1]], dtype=np.float32)
        s = np.array(self.scale, dtype=np.float32)
        r = glm.mat4_cast(glm.quat(glm.vec3(math.acos(self.ox[2]), math.acos(self.oy[0]), math.acos(self.oz[1]))))
        t = glm.translate(glm.mat4(1), glm.vec3(self.pos))
        transform = t @ r @ np.diag(np.concatenate((s, [1.0])))
        corners = np.concatenate((corners, np.ones((8, 1), dtype=np.float32)), axis=1)
        corners = (transform @ corners.T).T[:, :3]
        min_x, max_x = np.min(corners[:, 0]), np.max(corners[:, 0])
        min_y, max_y = np.min(corners[:, 1]), np.max(corners[:, 1])
        min_z, max_z = np.min(corners[:, 2]), np.max(corners[:, 2])
        t = (min_x - ray_origin.x) / ray_direction.x
        if t > 0 and abs(ray_origin.y + t * ray_direction.y - self.pos[1]) < self.scale[1] and abs(
                ray_origin.z + t * ray_direction.z - self.pos[2]) < self.scale[2]:
            return True
        t = (max_x - ray_origin.x) / ray_direction.x
        if t > 0 and abs(ray_origin.y + t * ray_direction.y - self.pos[1]) < self.scale[1] and abs(
                ray_origin.z + t * ray_direction.z - self.pos[2]) < self.scale[2]:
            return True
        t = (min_y - ray_origin.y) / ray_direction.y
        if t > 0 and abs(ray_origin.x + t * ray_direction.x - self.pos[0]) < self.scale[0] and abs(
                ray_origin.z + t * ray_direction.z - self.pos[2]) < self.scale[2]:
            return True
        t = (max_y - ray_origin.y) / ray_direction.y
        if t > 0 and abs(ray_origin.x + t * ray_direction.x - self.pos[0]) < self.scale[0] and abs(
                ray_origin.z + t * ray_direction.z - self.pos[2]) < self.scale[2]:
            return True
        t = (min_z - ray_origin.z) / ray_direction.z
        if t > 0 and abs(ray_origin.x + t * ray_direction.x - self.pos[0]) < self.scale[0] and abs(
                ray_origin.y + t * ray_direction.y - self.pos[1]) < self.scale[1]:
            return True
        t = (max_z - ray_origin.z) / ray_direction.z
        if t > 0 and abs(ray_origin.x + t * ray_direction.x - self.pos[0]) < self.scale[0] and abs(
                ray_origin.y + t * ray_direction.y - self.pos[1]) < self.scale[1]:
            return True

    def select_vert(self, ray_origin, ray_direction):
        sphere_radius = 0.025 * self.camera.speed
        vert_id = 0
        for vert in self.vertices:
            vert_id += 1
            vert = glm.vec3(vert[0] * self.scale[0], vert[1] * self.scale[2], vert[2] * self.scale[1])
            vert += self.pos
            if 0 <= self.ox[2]:
                vert = glm.rotate(vert - self.pos, math.asin(self.ox[0]), glm.vec3(0, 1, 0)) + self.pos
            else:
                vert = glm.rotate(vert - self.pos, -math.asin(self.ox[0]), glm.vec3(0, 1, 0)) + self.pos
            if 0 <= self.oy[0]:
                vert = glm.rotate(vert - self.pos, -math.asin(self.oy[1]), glm.vec3(0, 0, -1)) + self.pos
            else:
                vert = glm.rotate(vert - self.pos, math.asin(self.oy[1]), glm.vec3(0, 0, -1)) + self.pos
            if 0 <= self.oz[1]:
                vert = glm.rotate(vert - self.pos, -math.asin(self.oz[2]), glm.vec3(1, 0, 0)) + self.pos
            else:
                vert = glm.rotate(vert - self.pos, math.asin(self.oz[2]), glm.vec3(1, 0, 0)) + self.pos
            ray_to_sphere = np.array(vert - ray_origin)
            projection = ray_to_sphere.dot(ray_direction)
            closest_distance_sq = ray_to_sphere.dot(ray_to_sphere) - projection * projection
            if closest_distance_sq > sphere_radius * sphere_radius:
                continue
            if (not (closest_distance_sq > sphere_radius * sphere_radius)) and (not self.selected_vert.count(vert_id-1)):
                self.selected_vert.append(vert_id-1)

    # Перемещение вершин
    def vert_move(self, pos=(0.0, 0.0, 0.0)):
        for id in self.selected_vert:
            if glfw.get_key(self.app.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS:
                self.buff_vert_pos += pos
                self.vertices[id] = glm.vec3(math.floor(self.buff_vert_pos[0]), math.floor(self.buff_vert_pos[1]), math.floor(self.buff_vert_pos[2]))
            else:
                self.buff_vert_pos += pos
                self.vertices[id] += pos
        self.or_vao.change_vert(self.vertices)

    # Перемещение
    def transform_move(self, pos=(0, 0, 0)):
        if glfw.get_key(self.app.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS:
            self.buff_pos += pos
            self.pos = glm.vec3(math.floor(self.buff_pos[0]), math.floor(self.buff_pos[1]), math.floor(self.buff_pos[2]))
        else:
            self.buff_pos += pos
            self.pos += pos
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)

    # Масштабирование
    def transform_scale(self, scale=(1, 1, 1)):
        self.scale += scale
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)

    # Вращение
    def transform_rotate(self, rotation, point):
        self.pos = glm.rotate(self.pos - point, rotation, self.camera.forward) + point
        if np.abs(self.camera.forward[2]) == 1:
            self.oy = glm.rotate(self.oy, rotation, self.camera.forward)
            self.oz = glm.rotate(self.oz, -rotation, self.camera.forward)
        if np.abs(self.camera.forward[0]) == 1:
            self.ox = glm.rotate(self.ox, rotation, self.camera.forward)
            self.oz = glm.rotate(self.oz, -rotation, self.camera.forward)
        if np.abs(self.camera.forward[1]) == 1:
            self.ox = glm.rotate(self.ox, rotation, self.camera.forward)
            self.oy = glm.rotate(self.oy, -rotation, self.camera.forward)
        if not (np.abs(self.camera.forward[2]) == 1 or np.abs(self.camera.forward[0]) == 1 or np.abs(self.camera.forward[1]) == 1):
            self.ox = glm.rotate(self.ox, rotation, self.camera.forward)
            self.oy = glm.rotate(self.oy, rotation, self.camera.forward)
            self.oz = glm.rotate(self.oz, -rotation, self.camera.forward)
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)

    def get_vertices(self):
        return self.or_vao.get_vert(self.vao_name)

    # Рендер
    def render(self):
        self.update()
        self.vao.render()

    # Рендер выделения
    def render_outline(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(3.0)
        self.update()
        self.outline_vao.render()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def render_vertices(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.vert_texture)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(2.0)
        self.update()
        self.vao.render()
        glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
        glPointSize(8.0)
        self.update()
        self.vao.render()
        vertices = self.get_vertices()
        for sel_vert in self.selected_vert:
            point_position = glm.vec3(vertices[sel_vert])
            vbo = self.app.ctx.buffer(point_position)
            vao = self.app.ctx.simple_vertex_array(self.outline_program, vbo, 'in_position')
            self.app.ctx.point_size = 8.0
            vao.render(mode=mgl.POINTS)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    # Удаление объекта
    def destroy(self):
        #self.vao.destroy()
        self.vao = None
        #self.outline_vao.destroy()
        self.outline_vao = None
        #self.texture.destroy()
        self.texture = None
        #self.program.destroy()
        self.program = None
        #self.outline_program.destroy()
        self.outline_program = None

class Cube(BaseModel):
    def __init__(self, app, vao_name='cube', tex_id=0, pos=(0, 0, 0), scale=(1, 1, 1), ox=(0, 0, -1), oy=(1, 0, 0), oz=(0, 1, 0), vertices=np.array(0)):
        super().__init__(app, vao_name, tex_id, pos, scale, ox, oy, oz, vertices)
        self.on_init()

    def update(self):
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        #self.outline_program['camPos'].write(self.camera.position)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)
        self.or_vao.vao = self.mesh.vao.vao
        self.vao = self.or_vao.vao
        self.outline_vao = self.mesh.vao.vao_out
        self.program = self.vao.program
        self.outline_program = self.outline_vao.program
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

    def on_init(self):
        # Текстура
        self.texture = self.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        #self.outline_program['u_texture_0'] = 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        self.outline_program['m_proj'].write(self.camera.m_proj)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)

class Pyramid(BaseModel):
    def __init__(self, app, vao_name='pyramid', tex_id=0, pos=(0, 0, 0), scale=(1, 1, 1), ox=(0, 0, -1), oy=(1, 0, 0), oz=(0, 1, 0), vertices=np.array(0)):
        super().__init__(app, vao_name, tex_id, pos, scale, ox, oy, oz, vertices)
        self.on_init()

    def update(self):
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        #self.outline_program['camPos'].write(self.camera.position)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)
        self.or_vao.vao = self.mesh.vao.vao
        self.vao = self.or_vao.vao
        self.outline_vao = self.mesh.vao.vao_out
        self.program = self.vao.program
        self.outline_program = self.outline_vao.program
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

    def on_init(self):
        # Текстура
        self.texture = self.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        #self.outline_program['u_texture_0'] = 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        self.outline_program['m_proj'].write(self.camera.m_proj)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)


class Sphere(BaseModel):
    def __init__(self, app, vao_name='sphere', tex_id=0, pos=(0, 0, 0), scale=(1, 1, 1), ox=(0, 0, -1), oy=(1, 0, 0), oz=(0, 1, 0), vertices=np.array(0)):
        super().__init__(app, vao_name, tex_id, pos, scale, ox, oy, oz, vertices)
        self.on_init()

    def update(self):
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        #self.outline_program['camPos'].write(self.camera.position)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)
        self.or_vao.vao = self.mesh.vao.vao
        self.vao = self.or_vao.vao
        self.outline_vao = self.mesh.vao.vao_out
        self.program = self.vao.program
        self.outline_program = self.outline_vao.program
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

    def on_init(self):
        # Текстура
        self.texture = self.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        #self.outline_program['u_texture_0'] = 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        self.outline_program['m_proj'].write(self.camera.m_proj)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)


class Plane(BaseModel):
    def __init__(self, app, vao_name='plane', tex_id=0, pos=(0, 0, 0), scale=(1, 1, 1), ox=(0, 0, -1), oy=(1, 0, 0), oz=(0, 1, 0), vertices=np.array(0)):
        super().__init__(app, vao_name, tex_id, pos, scale, ox, oy, oz, vertices)
        self.on_init()

    def update(self):
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        #self.outline_program['camPos'].write(self.camera.position)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)
        self.or_vao.vao = self.mesh.vao.vao
        self.vao = self.or_vao.vao
        self.outline_vao = self.mesh.vao.vao_out
        self.program = self.vao.program
        self.outline_program = self.outline_vao.program
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

    def on_init(self):
        # Текстура
        self.texture = self.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        #self.outline_program['u_texture_0'] = 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        self.outline_program['m_proj'].write(self.camera.m_proj)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)


class Custom(BaseModel):
    def __init__(self, app, vao_name='custom', tex_id=0, pos=(0, 0, 0), scale=(1, 1, 1), ox=(0, 0, -1), oy=(1, 0, 0), oz=(0, 1, 0), vertices=np.array(0)):
        super().__init__(app, vao_name, tex_id, pos, scale, ox, oy, oz, vertices)
        self.on_init()

    def update(self):
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        #self.outline_program['camPos'].write(self.camera.position)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)
        self.or_vao.vao = self.mesh.vao.vao
        self.vao = self.or_vao.vao
        self.outline_vao = self.mesh.vao.vao_out
        self.program = self.vao.program
        self.outline_program = self.outline_vao.program
        self.m_model = self.get_model_matrix()
        self.outline_model = self.get_outline_model_matrix(self.m_model)
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

    def on_init(self):
        # Текстура
        self.texture = self.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        #self.outline_program['u_texture_0'] = 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        self.outline_program['m_proj'].write(self.camera.m_proj)
        self.outline_program['m_view'].write(self.camera.m_view)
        self.outline_program['m_model'].write(self.outline_model)

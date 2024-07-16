from model import *
import glfw


class Scene:
    def __init__(self, app):
        self.app = app
        self.objects = []
        self.editing_mode = False
        # ID
        self.obj_ids = []
        # Выделение
        self.obj_sel = []
        self.load()

    # Создание объекта
    def add_object(self, obj):
        self.obj_ids.append(len(self.obj_ids))
        self.objects.append(obj)

    # Выделение объекта
    def select_object(self, obj_id):
        if not self.obj_sel.count(obj_id):
            self.obj_sel.append(obj_id)

    # Отмена выделения
    def deselect(self):
        self.obj_sel.clear()

    def deselect_vertices(self):
        for obj_id in self.obj_sel:
            self.objects[obj_id].selected_vert = []

    # Функция запуска
    def load(self):
        app = self.app
        add = self.add_object
        add(Cube(app, pos=(0, 0, 0), scale=(1, 1, 1)))

    def load_scene(self, objects, editing_mode, obj_ids, obj_sel, vertices):
        self.objects = []
        i = 0
        for obj in objects:
            object_type = obj[0]
            if object_type == 'cube':
                self.add_object(Cube(self.app, pos=obj[1], scale=obj[2], ox=obj[3], oy=obj[4], oz=obj[5], vertices=vertices[i]))
            elif object_type == 'pyramid':
                self.add_object(Pyramid(self.app, pos=obj[1], scale=obj[2], ox=obj[3], oy=obj[4], oz=obj[5], vertices=vertices[i]))
            elif object_type == 'sphere':
                self.add_object(Sphere(self.app, pos=obj[1], scale=obj[2], ox=obj[3], oy=obj[4], oz=obj[5], vertices=vertices[i]))
            elif object_type == 'plane':
                self.add_object(Plane(self.app, pos=obj[1], scale=obj[2], ox=obj[3], oy=obj[4], oz=obj[5], vertices=vertices[i]))
            else:
                self.add_object(Custom(self.app, vao_name=obj[0], pos=obj[1], scale=obj[2], ox=obj[3], oy=obj[4], oz=obj[5], vertices=vertices[i]))
            i += 1
        self.obj_ids = []
        self.obj_sel = []
        self.editing_mode = editing_mode
        self.obj_ids = obj_ids
        self.deselect()
        self.obj_sel = obj_sel

    # Функция создания объекта в центре фокуса
    def new_obj(self, object_type):
        pos_x = self.app.camera.target[0]
        pos_y = self.app.camera.target[1]
        pos_z = self.app.camera.target[2]
        if object_type == 'Cube':
            self.add_object(Cube(self.app, pos=(pos_x, pos_y, pos_z)))
        elif object_type == 'Pyramid':
            self.add_object(Pyramid(self.app, pos=(pos_x, pos_y, pos_z)))
        elif object_type == 'Sphere':
            self.add_object(Sphere(self.app, pos=(pos_x, pos_y, pos_z)))
        elif object_type == 'Plane':
            self.add_object(Plane(self.app, pos=(pos_x, pos_y, pos_z)))

    def new_cust_obj(self, filename):
        pos_x = self.app.camera.target[0]
        pos_y = self.app.camera.target[1]
        pos_z = self.app.camera.target[2]
        self.add_object(Custom(self.app, vao_name=filename, pos=(pos_x, pos_y, pos_z)))

    def copy_paste_obj(self):
        pos_x = self.app.camera.target[0]
        pos_y = self.app.camera.target[1]
        pos_z = self.app.camera.target[2]
        ids = []
        mid = glm.vec3(0, 0, 0)
        for obj_id in self.obj_sel:
            mid += self.objects[obj_id].pos
            object_type = self.objects[obj_id].vao_name
            pos = self.objects[obj_id].pos
            scale = self.objects[obj_id].scale
            ox = self.objects[obj_id].ox
            oy = self.objects[obj_id].oy
            oz = self.objects[obj_id].oz
            vertices = np.array(self.objects[obj_id].get_vertices())
            if object_type == 'cube':
                self.add_object(Cube(self.app, pos=pos, scale=scale, ox=ox, oy=oy, oz=oz, vertices=vertices))
            elif object_type == 'pyramid':
                self.add_object(Pyramid(self.app, pos=pos, scale=scale, ox=ox, oy=oy, oz=oz, vertices=vertices))
            elif object_type == 'sphere':
                self.add_object(Sphere(self.app, pos=pos, scale=scale, ox=ox, oy=oy, oz=oz, vertices=vertices))
            elif object_type == 'plane':
                self.add_object(Plane(self.app, pos=pos, scale=scale, ox=ox, oy=oy, oz=oz, vertices=vertices))
            else:
                self.add_object(Custom(self.app, vao_name=object_type, pos=pos, scale=scale, ox=ox, oy=oy, oz=oz, vertices=vertices))
            ids.append(len(self.objects) - 1)
        self.deselect()
        for id in ids:
            self.select_object(id)
        for obj_id in self.obj_sel:
            del_pos = self.objects[obj_id].pos - mid
            self.objects[obj_id].pos = del_pos + (pos_x, pos_y, pos_z)

    # Функция удаления объектов
    def delete_obj(self):
        copy_objects = self.objects.copy()
        for obj_id in self.obj_sel:
            if self.objects[obj_id] in copy_objects:
                copy_objects.remove(self.objects[obj_id])
                self.obj_ids.remove(obj_id)
                #self.objects[obj_id].destroy()
        self.objects = copy_objects
        i = 0
        for obj in self.objects:
            self.obj_ids[i] = i
            i += 1
        self.deselect()

    # Функция получения объекта, по которому кликнули мышью
    def get_object_at_pos(self, mouse_x, mouse_y):
        x = 2.0 * mouse_x / self.app.WIN_SIZE[0] - 1.0
        y = 1.0 - (2.0 * mouse_y) / self.app.WIN_SIZE[1]
        z = 1.0
        ray_nds = glm.vec3(x, y, z)
        ray_clip = glm.vec4(ray_nds.xy, -1.0, 1.0)
        ray_eye = glm.inverse(self.app.camera.m_proj) * ray_clip
        ray_eye = glm.vec4(ray_eye.xy, -1.0, 0.0)
        ray_wor = (glm.inverse(self.app.camera.m_view) * ray_eye).xyz
        ray_wor = glm.normalize(ray_wor)
        ray_origin = self.app.camera.position
        ray_direction = ray_wor
        for obj in self.objects:
            cont = obj.contains_point(ray_origin, ray_direction)
            if cont:
                return self.objects.index(obj)
        return None

    def get_vert_at_pos(self, mouse_x, mouse_y):
        x = 2.0 * mouse_x / self.app.WIN_SIZE[0] - 1.0
        y = 1.0 - (2.0 * mouse_y) / self.app.WIN_SIZE[1]
        z = 1.0
        ray_nds = glm.vec3(x, y, z)
        ray_clip = glm.vec4(ray_nds.xy, -1.0, 1.0)
        ray_eye = glm.inverse(self.app.camera.m_proj) * ray_clip
        ray_eye = glm.vec4(ray_eye.xy, -1.0, 0.0)
        ray_wor = (glm.inverse(self.app.camera.m_view) * ray_eye).xyz
        ray_wor = glm.normalize(ray_wor)
        ray_origin = self.app.camera.position
        ray_direction = ray_wor
        for obj_id in self.obj_sel:
            self.objects[obj_id].select_vert(ray_origin, ray_direction)

    # Функция перемещения объекта
    def move_obj(self):
        current_mouse_pos = glm.vec2(*glfw.get_cursor_pos(self.app.window))
        delta_pos = current_mouse_pos - glm.vec2(self.app.camera.mouse_pos)
        self.app.camera.mouse_pos = current_mouse_pos
        velocity = self.app.delta_time * self.app.camera.speed
        new_position = self.app.camera.right * delta_pos.x * 0.007 * velocity * 25
        new_position -= self.app.camera.up * delta_pos.y * 0.007 * velocity * 25
        if glfw.get_key(self.app.window, glfw.KEY_W) == glfw.PRESS:
            new_position += self.app.camera.forward * velocity
        if glfw.get_key(self.app.window, glfw.KEY_S) == glfw.PRESS:
            new_position -= self.app.camera.forward * velocity
        if glfw.get_key(self.app.window, glfw.KEY_D) == glfw.PRESS:
            new_position += self.app.camera.right * velocity
        if glfw.get_key(self.app.window, glfw.KEY_A) == glfw.PRESS:
            new_position -= self.app.camera.right * velocity
        if glfw.get_key(self.app.window, glfw.KEY_Q) == glfw.PRESS:
            new_position += self.app.camera.up * velocity
        if glfw.get_key(self.app.window, glfw.KEY_E) == glfw.PRESS:
            new_position -= self.app.camera.up * velocity
        if glfw.get_key(self.app.window, glfw.KEY_UP) == glfw.PRESS:
            new_position -= glm.vec3(0, 0, 1) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_DOWN) == glfw.PRESS:
            new_position += glm.vec3(0, 0, 1) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT) == glfw.PRESS:
            new_position += glm.vec3(1, 0, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_LEFT) == glfw.PRESS:
            new_position -= glm.vec3(1, 0, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS:
            new_position += glm.vec3(0, 1, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS:
            new_position -= glm.vec3(0, 1, 0) * velocity
        for obj_id in self.obj_sel:
            self.objects[obj_id].transform_move(pos=new_position)

    # Функция перемещения вершин
    def move_vert(self):
        current_mouse_pos = glm.vec2(*glfw.get_cursor_pos(self.app.window))
        delta_pos = current_mouse_pos - glm.vec2(self.app.camera.mouse_pos)
        self.app.camera.mouse_pos = current_mouse_pos
        velocity = self.app.delta_time * self.app.camera.speed
        new_position = self.app.camera.right * delta_pos.x * 0.007 * velocity * 25
        new_position -= self.app.camera.up * delta_pos.y * 0.007 * velocity * 25
        if glfw.get_key(self.app.window, glfw.KEY_W) == glfw.PRESS:
            new_position += self.app.camera.forward * velocity
        if glfw.get_key(self.app.window, glfw.KEY_S) == glfw.PRESS:
            new_position -= self.app.camera.forward * velocity
        if glfw.get_key(self.app.window, glfw.KEY_D) == glfw.PRESS:
            new_position += self.app.camera.right * velocity
        if glfw.get_key(self.app.window, glfw.KEY_A) == glfw.PRESS:
            new_position -= self.app.camera.right * velocity
        if glfw.get_key(self.app.window, glfw.KEY_Q) == glfw.PRESS:
            new_position += self.app.camera.up * velocity
        if glfw.get_key(self.app.window, glfw.KEY_E) == glfw.PRESS:
            new_position -= self.app.camera.up * velocity
        if glfw.get_key(self.app.window, glfw.KEY_UP) == glfw.PRESS:
            new_position -= glm.vec3(0, 0, 1) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_DOWN) == glfw.PRESS:
            new_position += glm.vec3(0, 0, 1) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT) == glfw.PRESS:
            new_position += glm.vec3(1, 0, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_LEFT) == glfw.PRESS:
            new_position -= glm.vec3(1, 0, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS:
            new_position += glm.vec3(0, 1, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS:
            new_position -= glm.vec3(0, 1, 0) * velocity
        for obj_id in self.obj_sel:
            self.objects[obj_id].vert_move(pos=new_position)

    # Функция масштабиования объекта
    def scale_obj(self):
        current_mouse_pos = glm.vec2(*glfw.get_cursor_pos(self.app.window))
        delta_pos = current_mouse_pos - glm.vec2(self.app.camera.mouse_pos)
        self.app.camera.mouse_pos = current_mouse_pos
        if glfw.get_key(self.app.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            delta = delta_pos.x + delta_pos.y
            for obj_id in self.obj_sel:
                new_scale = glm.vec3(0.007 * delta, self.objects[obj_id].scale[1] * 0.007 * delta / self.objects[obj_id].scale[0], self.objects[obj_id].scale[2] * 0.007 * delta / self.objects[obj_id].scale[0])
                self.objects[obj_id].transform_scale(scale=new_scale)
        else:
            new_scale = glm.vec3(np.abs(self.app.camera.right[0]), np.abs(self.app.camera.right[2]), np.abs(self.app.camera.right[1])) * delta_pos.x * 0.007
            new_scale += glm.vec3(np.abs(self.app.camera.up[0]), self.app.camera.forward[1], -np.abs(self.app.camera.up[1])) * delta_pos.y * 0.007
            for obj_id in self.obj_sel:
                self.objects[obj_id].transform_scale(scale=new_scale)

    # Функция вращения объекта вокруг своей оси
    def rotate_obj(self):
        current_mouse_pos = glm.vec2(*glfw.get_cursor_pos(self.app.window))
        cur_angle = math.atan2(current_mouse_pos[1] - self.app.WIN_SIZE[1] / 2,
                                current_mouse_pos[0] - self.app.WIN_SIZE[0] / 2)
        rotation = cur_angle - math.atan2(self.app.camera.mouse_pos[1] - self.app.WIN_SIZE[1] / 2,
                                        self.app.camera.mouse_pos[0] - self.app.WIN_SIZE[0] / 2)
        self.app.camera.mouse_pos = current_mouse_pos
        middle = glm.vec3(0, 0, 0)
        for obj_id in self.obj_sel:
            middle += self.objects[obj_id].pos
        middle = middle / len(self.obj_sel)
        if rotation != 0:
            for obj_id in self.obj_sel:
                # new_rot = self.objects[obj_id].rot
                # new_rot += glm.vec3(rotation, rotation, rotation) * self.app.camera.forward
                # new_rot = glm.rotate(new_rot, rotation, self.app.camera.forward)
                self.objects[obj_id].transform_rotate(rotation=rotation, point=middle)

    def change_mode(self):
        if self.editing_mode:
            self.editing_mode = False
        else:
            self.editing_mode = True

    # Рендеринг
    def render(self):
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glStencilFunc(GL_ALWAYS, 1, 0xFF)
        glStencilMask(0xFF)
        for obj in self.objects:
            obj.render()
        glStencilOp(GL_KEEP, GL_KEEP, GL_INVERT)
        glStencilFunc(GL_NOTEQUAL, 0, 0xFF)
        glStencilMask(0x00)
        glDisable(GL_DEPTH_TEST)
        if self.editing_mode:
            for obj_id in self.obj_sel:
                self.objects[obj_id].render_vertices()
        else:
            for obj_id in self.obj_sel:
                self.objects[obj_id].render_outline()
        glDisable(GL_STENCIL_TEST)

    def destroy(self):
        self.objects = []
        self.obj_ids = []
        self.obj_sel = []
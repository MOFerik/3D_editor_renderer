import time
import sys
from tkinter import *
from tkinter.filedialog import askopenfilename
import re
from functools import partial
from camera import Camera
from light import Light
from model import *
from scene import Scene


class GraphicsEngine:
    def __init__(self, win_size=(1920, 1080)):
        # Инициализация GLFW
        glfw.init()

        np.set_printoptions(threshold=sys.maxsize)

        # Размер окна
        self.WIN_SIZE = win_size

        # Создание окна
        self.window = glfw.create_window(self.WIN_SIZE[0], self.WIN_SIZE[1], "My Window", None, None)

        # Инициализация контекста окна как текущего контекста
        glfw.make_context_current(self.window)

        # Использование ModernGL контекста
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        # Счетчик времени
        self.start_time = time.perf_counter()
        self.time = 0
        self.delta_time = 0

        # Свет
        self.light = Light()

        self.mouse_pos = 0
        # Маркеры клавиш
        self.shift_b_pressed = False
        self.shift_x_pressed = False
        self.shift_d_pressed = False
        self.ctrl_z_pressed = False
        self.ctrl_shift_z_pressed = False
        self.is_g_pressed = False
        self.was_g_pressed = False
        self.is_tab_pressed = False
        self.was_tab_pressed = False
        self.is_t_pressed = False
        self.was_t_pressed = False
        self.is_r_pressed = False
        self.was_r_pressed = False
        self.is_r_pressed = False
        self.was_r_pressed = False
        self.scene_buffer = []
        self.scene_redo_buffer = []

        # Камера
        self.camera = Camera(self)

        # Сцена
        self.scene = Scene(self)

    # Буфер действий
    def buffer(self):
        buff_obj = []
        vertices = []
        for obj in self.scene.objects.copy():
            v_name = obj.vao_name
            pos = obj.pos
            scale = obj.scale
            ox = obj.ox
            oy = obj.oy
            oz = obj.oz
            vert = np.array(obj.get_vertices())
            vertices.append(vert)
            buff_obj.append([v_name, pos, scale, ox, oy, oz])
        objects = buff_obj.copy()
        editing_mode = self.scene.editing_mode
        obj_ids = self.scene.obj_ids.copy()
        obj_sel = self.scene.obj_sel.copy()
        buffer = [objects, editing_mode, obj_ids, obj_sel, vertices]
        self.scene_buffer.append(buffer[:])

    # Отмена
    def undo(self):
        if len(self.scene_buffer) > 0:
            self.redo_buffer()
            buffer = self.scene_buffer.pop()
            objects = buffer[0]
            editing_mode = buffer[1]
            obj_ids = buffer[2]
            obj_sel = buffer[3]
            vertices = buffer[4]
            self.scene.load_scene(objects, editing_mode, obj_ids, obj_sel, vertices)

    # Буфер отмененных действий
    def redo_buffer(self):
        buff_obj = []
        vertices = []
        for obj in self.scene.objects.copy():
            v_name = obj.vao_name
            pos = obj.pos
            scale = obj.scale
            ox = obj.ox
            oy = obj.oy
            oz = obj.oz
            vert = np.array(obj.get_vertices())
            vertices.append(vert)
            buff_obj.append([v_name, pos, scale, ox, oy, oz])
        objects = buff_obj.copy()
        editing_mode = self.scene.editing_mode
        obj_ids = self.scene.obj_ids.copy()
        obj_sel = self.scene.obj_sel.copy()
        buffer = [objects, editing_mode, obj_ids, obj_sel, vertices[:]]
        self.scene_redo_buffer.append(buffer[:])

    # Отмена отмены
    def redo(self):
        #self.scene_buffer = []
        if len(self.scene_redo_buffer) > 0:
            self.buffer()
            #self.scene.destroy()
            buffer = self.scene_redo_buffer.pop()
            objects = buffer[0]
            editing_mode = buffer[1]
            obj_ids = buffer[2]
            obj_sel = buffer[3]
            vertices = buffer[4]
            self.scene.load_scene(objects, editing_mode, obj_ids, obj_sel, vertices)

    def option_function1(self, popup):
        self.scene.new_obj('Cube')
        popup.destroy()

    def option_function2(self, popup):
        self.scene.new_obj('Pyramid')
        popup.destroy()

    def option_function3(self, popup):
        self.scene.new_obj('Sphere')
        popup.destroy()

    def option_function4(self, popup):
        self.scene.new_obj('Plane')
        popup.destroy()

    def option_function5(self, popup):
        filename = askopenfilename()
        #filename = filename.removeprefix("C:\\Users\\deadp\\Desktop\\Projects\Diploma\\Graphics Engine\\")
        if ".obj" in filename:
            self.scene.new_cust_obj("{}".format(filename))
        else:
            popup = Tk()
            popup.title("Выберите файл формата .obj")
            popup.geometry("600x50")
            options = ["Ок"]
            button1 = Button(popup, text=options[0], command=popup.destroy)
            button1.pack()
            popup.mainloop()

    def show_popup(self):
        popup = Tk()
        popup.title("Создание объекта")
        popup.geometry("300x200")

        options = ["Куб", "Пирамида", "Сфера", "Плоскость", "Загрузить объект"]
        button1 = Button(popup, text=options[0], command=partial(self.option_function1, popup))
        button1.pack()
        button2 = Button(popup, text=options[1], command=partial(self.option_function2, popup))
        button2.pack()
        button3 = Button(popup, text=options[2], command=partial(self.option_function3, popup))
        button3.pack()
        button4 = Button(popup, text=options[3], command=partial(self.option_function4, popup))
        button4.pack()
        button5 = Button(popup, text=options[4], command=partial(self.option_function5, popup))
        button5.pack()
        popup.mainloop()

    def saving(self, popup):
        filename = askopenfilename()
        with open(filename, "w") as file:
            for obj in self.scene.objects.copy():
                v_name = obj.vao_name
                pos = obj.pos
                scale = obj.scale
                ox = obj.ox
                oy = obj.oy
                oz = obj.oz
                vert = np.array(obj.get_vertices())
                file.write("obj \n{}\n{} {} {} {} {} \n{} \n".format(v_name, pos, scale, ox, oy, oz, vert))
            editing_mode = self.scene.editing_mode
            file.write("mode \n{}\n".format(editing_mode))
            obj_ids = self.scene.obj_ids.copy()
            file.write("ids {}\n".format(obj_ids))
            obj_sel = self.scene.obj_sel.copy()
            file.write("sel {}".format(obj_sel))
        popup.destroy()

    def autosave(self):
        with open('backup.txt', "w") as file:
            for obj in self.scene.objects.copy():
                v_name = obj.vao_name
                pos = obj.pos
                scale = obj.scale
                ox = obj.ox
                oy = obj.oy
                oz = obj.oz
                vert = obj.get_vertices()
                file.write("obj \n{}\n{} {} {} {} {} \n{} \n".format(v_name, pos, scale, ox, oy, oz, vert))
            editing_mode = self.scene.editing_mode
            file.write("mode \n{}\n".format(editing_mode))
            obj_ids = self.scene.obj_ids.copy()
            file.write("ids {}\n".format(obj_ids))
            obj_sel = self.scene.obj_sel.copy()
            file.write("sel {}".format(obj_sel))

    def loading(self, popup):
        filename = askopenfilename()
        if not ".txt" in filename:
            popup = Tk()
            popup.title("Выберите файл формата .txt")
            popup.geometry("600x50")
            options = ["Ок"]
            button1 = Button(popup, text=options[0], command=popup.destroy)
            button1.pack()
            popup.mainloop()
        else:
            self.scene_buffer = []
            self.scene_redo_buffer = []
            objects = []
            vertice_arr = []
            editing_mode = False
            obj_ids = []
            obj_sel = []
            with open(filename, encoding="utf-8") as f:
                i = 0
                while (i < 500000):
                    line = f.readline()
                    if 'obj ' in line:
                        vertices = []
                        line = f.readline()
                        type = line
                        type = type.removesuffix("\n")
                        line = f.readline()
                        remove_list = ['vec3(']
                        word_list = line.split()
                        line = ' '.join([i for i in word_list if i not in remove_list])
                        numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                        rx = re.compile(numeric_const_pattern, re.VERBOSE)
                        values = rx.findall(line)
                        pos = glm.vec3(float(values[0]), float(values[1]), float(values[2]))
                        scale = glm.vec3(float(values[3]), float(values[4]), float(values[5]))
                        ox = glm.vec3(float(values[6]), float(values[7]), float(values[8]))
                        oy = glm.vec3(float(values[9]), float(values[10]), float(values[11]))
                        oz = glm.vec3(float(values[12]), float(values[13]), float(values[14]))
                        objects.append([type, pos, scale, ox, oy, oz])
                    elif '[[' in line and 'ids' not in line:
                        while ']]' not in line:
                            numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                            rx = re.compile(numeric_const_pattern, re.VERBOSE)
                            values = rx.findall(line)
                            vert = (float(values[0]), float(values[1]), float(values[2]))
                            vertices.append(vert)
                            line = f.readline()
                        numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                        rx = re.compile(numeric_const_pattern, re.VERBOSE)
                        values = rx.findall(line)
                        vert = (float(values[0]), float(values[1]), float(values[2]))
                        vertices.append(vert)
                        vertice_arr.append(np.array(vertices))
                    elif 'mode' in line:
                        line = f.readline()
                        if line == "True":
                            editing_mode = True
                        else:
                            editing_mode = False
                    elif 'ids' in line:
                        numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                        rx = re.compile(numeric_const_pattern, re.VERBOSE)
                        values = rx.findall(line)
                        obj_ids = [values]
                        line = f.readline()
                    elif 'sel' in line:
                        numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                        rx = re.compile(numeric_const_pattern, re.VERBOSE)
                        values = rx.findall(line)
                        obj_sel = np.array(values)
                        line = f.readline()
                    else:
                        break
            self.scene.load_scene(objects, editing_mode, obj_ids, obj_sel, vertice_arr)
            popup.destroy()

    def exiting(self, popup):
        self.autosave()
        popup.destroy()
        self.scene.destroy()
        glfw.terminate()
        sys.exit()

    def manual(self, popup):
        popup.destroy()
        ws = Tk()
        ws.title('PythonGuides')
        ws.geometry('850x900')
        ws.config(bg='#9bf5ff')
        message = ""
        with open(r"other\manual.txt", encoding="utf-8") as f:
            message = f.read()
        text_box = Text(
            ws,
            height=44,
            width=82
        )
        text_box.pack(expand=True)
        text_box.insert('end', message)
        text_box.config(state='disabled')
        ws.mainloop()

    def show_menu(self):
        popup = Tk()
        popup.title("Меню")
        popup.geometry("280x150")

        options = ["Сохранить файл", "Загрузить файл", "Закрыть", "Открыть мануал"]
        button1 = Button(popup, text=options[0], command=partial(self.saving, popup))
        button1.pack()
        button2 = Button(popup, text=options[1], command=partial(self.loading, popup))
        button2.pack()
        button3 = Button(popup, text=options[2], command=partial(self.exiting, popup))
        button3.pack()
        button4 = Button(popup, text=options[3], command=partial(self.manual, popup))
        button4.pack()
        popup.mainloop()

    # Функция проверки событий
    def get_controls(self):
        if glfw.get_key(self.window, glfw.KEY_KP_0) == glfw.PRESS:
            middle = glm.vec3(0, 0, 0)
            for obj_id in self.scene.obj_sel:
                middle += self.scene.objects[obj_id].pos
            if middle != glm.vec3(0, 0, 0):
                middle = middle / len(self.scene.obj_sel)
            self.camera.position -= self.camera.target - middle
            self.camera.target = middle

        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            self.show_menu()

        # Режим редактирования вершин
        self.was_tab_pressed = self.is_tab_pressed
        self.is_tab_pressed = glfw.get_key(self.window, glfw.KEY_TAB) == glfw.PRESS
        if self.is_tab_pressed and not self.was_tab_pressed:
            if glfw.get_key(self.window, glfw.KEY_TAB) == glfw.PRESS:
                self.scene_redo_buffer = []
                self.buffer()
                self.scene.change_mode()

        if self.scene.editing_mode:
            # Выделение вершин
            if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS:
                    self.scene.deselect_vertices()
                x, y = self.mouse_pos
                self.scene.get_vert_at_pos(x, y)
            # Перемещение вершин
            self.was_g_pressed = self.is_g_pressed
            self.is_g_pressed = glfw.get_key(self.window, glfw.KEY_G) == glfw.PRESS
            if self.is_g_pressed and not self.was_g_pressed:
                self.scene_redo_buffer = []
                self.buffer()
                self.camera.mouse_pos = glfw.get_cursor_pos(self.window)
            if glfw.get_key(self.window, glfw.KEY_G) == glfw.PRESS:
                self.scene.move_vert()
            # Отмена действия
            if glfw.get_key(self.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS and glfw.get_key(self.window,
                                                                        glfw.KEY_Z) == glfw.PRESS and glfw.get_key(
                                                                self.window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS:
                if not self.ctrl_z_pressed:
                    self.undo()
                    self.ctrl_z_pressed = True
            else:
                self.ctrl_z_pressed = False
            # Отмена отмены действия
            if glfw.get_key(self.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS and glfw.get_key(self.window,
                                                                        glfw.KEY_Z) == glfw.PRESS and glfw.get_key(
                                                                self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
                if not self.ctrl_shift_z_pressed:
                    self.redo()
                    self.ctrl_shift_z_pressed = True
            else:
                self.ctrl_shift_z_pressed = False
        else:
            # Перемещение объектов
            self.was_g_pressed = self.is_g_pressed
            self.is_g_pressed = glfw.get_key(self.window, glfw.KEY_G) == glfw.PRESS
            if self.is_g_pressed and not self.was_g_pressed:
                self.scene_redo_buffer = []
                self.buffer()
                self.camera.mouse_pos = glfw.get_cursor_pos(self.window)
            if glfw.get_key(self.window, glfw.KEY_G) == glfw.PRESS:
                self.scene.move_obj()
            # Масштабирование объектов
            self.was_t_pressed = self.is_t_pressed
            self.is_t_pressed = glfw.get_key(self.window, glfw.KEY_T) == glfw.PRESS
            if self.is_t_pressed and not self.was_t_pressed:
                self.scene_redo_buffer = []
                self.buffer()
                self.camera.mouse_pos = glfw.get_cursor_pos(self.window)
            if glfw.get_key(self.window, glfw.KEY_T) == glfw.PRESS:
                self.scene.scale_obj()
            # Вращение объектов
            self.was_r_pressed = self.is_r_pressed
            self.is_r_pressed = glfw.get_key(self.window, glfw.KEY_R) == glfw.PRESS
            if self.is_r_pressed and not self.was_r_pressed:
                self.scene_redo_buffer = []
                self.buffer()
                self.camera.mouse_pos = glfw.get_cursor_pos(self.window)
            if glfw.get_key(self.window, glfw.KEY_R) == glfw.PRESS:
                self.scene.rotate_obj()
            # Создание новых кубов
            if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS and glfw.get_key(self.window,
                                                                                glfw.KEY_B) == glfw.PRESS:
                if not self.shift_b_pressed:
                    self.scene_redo_buffer = []
                    self.buffer()
                    self.show_popup()
                    self.shift_b_pressed = True
            else:
                self.shift_b_pressed = False
            # Копипастинг
            if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS and glfw.get_key(self.window,
                                                                                glfw.KEY_C) == glfw.PRESS:
                if not self.shift_d_pressed:
                    self.scene_redo_buffer = []
                    self.buffer()
                    self.scene.copy_paste_obj()
                    self.shift_d_pressed = True
            else:
                self.shift_d_pressed = False
            # Удаление кубов
            if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS and glfw.get_key(self.window,
                                                                                                 glfw.KEY_X) == glfw.PRESS:
                if not self.shift_x_pressed:
                    self.scene_redo_buffer = []
                    self.buffer()
                    self.scene.delete_obj()
                    self.shift_x_pressed = True
            else:
                self.shift_x_pressed = False
            # Выделение кубов
            if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS:
                    self.scene.deselect()
                x, y = self.mouse_pos
                obj_id = self.scene.get_object_at_pos(x, y)
                if obj_id is not None:
                    self.scene.select_object(obj_id)
            # Отмена действия
            if glfw.get_key(self.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS and glfw.get_key(self.window,
                                                                                                   glfw.KEY_Z) == glfw.PRESS and glfw.get_key(
                self.window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS:
                if not self.ctrl_z_pressed:
                    #self.deselect()
                    self.undo()
                    self.ctrl_z_pressed = True
            else:
                self.ctrl_z_pressed = False
            # Отмена отмены действия
            if glfw.get_key(self.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS and glfw.get_key(self.window,
                                                                                                   glfw.KEY_Z) == glfw.PRESS and glfw.get_key(
                self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
                if not self.ctrl_shift_z_pressed:
                    #self.deselect()
                    self.redo()
                    self.ctrl_shift_z_pressed = True
            else:
                self.ctrl_shift_z_pressed = False

    # Функция рендера
    def render(self):
        self.light = Light(position=self.camera.position)
        self.ctx.clear(color=(0.175, 0.225, 0.275))
        self.get_controls()
        # Рендер
        self.scene.render()
        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def get_time(self):
        self.delta_time = (time.perf_counter() - self.start_time) * 1 - self.time
        self.time = (time.perf_counter() - self.start_time) * 1

    def run(self):
        self.show_menu()
        while not glfw.window_should_close(self.window):
            self.camera.update()
            x, y = glfw.get_cursor_pos(self.window)
            self.mouse_pos = (int(x), int(y))
            self.render()
            self.get_time()
        self.autosave()
        self.scene.destroy()
        glfw.terminate()
        sys.exit()

# Работа программы
if __name__ == '__main__':
    engine = GraphicsEngine()
    engine.run()

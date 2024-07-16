import glm
import glfw

FOV = 50
NEAR = 0.01
FAR = 200
SENSITIVITY = 0.0075


class Camera:
    def __init__(self, app):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(0, 0, 9)
        self.target = glm.vec3(0, 0, 0)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.horizontal_angle = 0.0
        self.vertical_angle = 0.0
        self.mouse_pos = 0
        self.is_middle_pressed = False
        self.was_middle_pressed = False
        self.total_horizontal_angle = 0.0
        self.total_vertical_angle = 0.0
        self.speed = 10
        # Матрица вида
        self.m_view = self.get_view_matrix()
        # Матрица проекции
        self.m_proj = self.get_projection_matrix()

    # Функция обновления
    def update(self):
        self.was_middle_pressed = self.is_middle_pressed
        self.is_middle_pressed = glfw.get_mouse_button(self.app.window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS
        if self.is_middle_pressed and not self.was_middle_pressed:
            self.mouse_pos = glfw.get_cursor_pos(self.app.window)
        self.move()
        self.m_view = self.get_view_matrix()

    # Функция отдаления/приближения камеры к точке фокусаа при прокрутке колеса мыши
    def scroll_callback(self, window, xoffset, yoffset):
        distance = glm.distance(self.position, self.target)
        new_distance = distance - yoffset/5
        # Изменение скорости перемещение камеры в зависимости от уровня приближения
        if new_distance > 0.05:
            self.speed -= yoffset/4.5
            direction = glm.normalize(self.position - self.target)
            self.position = self.target + direction * new_distance
            self.m_view = self.get_view_matrix()

    # Функция перемещения и вращения камеры
    def move(self):
        # Вычисление скорости не зависящей от FPS
        velocity = self.app.delta_time * self.speed

        # Перемещение камеры от первого лица с помощью WASD и QE - вверх-вниз
        if glfw.get_key(self.app.window, glfw.KEY_W) == glfw.PRESS:
            self.position += self.forward * velocity
            self.target += self.forward * velocity
        if glfw.get_key(self.app.window, glfw.KEY_S) == glfw.PRESS:
            self.position -= self.forward * velocity
            self.target -= self.forward * velocity
        if glfw.get_key(self.app.window, glfw.KEY_A) == glfw.PRESS:
            self.position -= self.right * velocity
            self.target -= self.right * velocity
        if glfw.get_key(self.app.window, glfw.KEY_D) == glfw.PRESS:
            self.position += self.right * velocity
            self.target += self.right * velocity
        if glfw.get_key(self.app.window, glfw.KEY_Q) == glfw.PRESS:
            self.position += self.up * velocity
            self.target += self.up * velocity
        if glfw.get_key(self.app.window, glfw.KEY_E) == glfw.PRESS:
            self.position -= self.up * velocity
            self.target -= self.up * velocity

        # Вызов функции отдаления/приближения камеры к точке фокусаа при прокрутке колеса мыши
        glfw.set_scroll_callback(self.app.window, self.scroll_callback)

        # Вращение камеры вокруг точки фокуса при зажатии колеса мыши
        if glfw.get_key(self.app.window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS:
            if glfw.get_mouse_button(self.app.window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS:
                current_mouse_pos = glm.vec2(*glfw.get_cursor_pos(self.app.window))
                delta_pos = current_mouse_pos - glm.vec2(self.mouse_pos)
                self.mouse_pos = current_mouse_pos
                if delta_pos.x != 0:
                    angle = -delta_pos.x * SENSITIVITY
                    rotate_axis = self.up
                    self.position = glm.rotate(self.position - self.target, angle, rotate_axis) + self.target
                    self.right = glm.rotate(self.right, angle, rotate_axis)
                    self.forward = glm.rotate(self.forward, angle, rotate_axis)
                    self.total_horizontal_angle += angle
                if delta_pos.y != 0:
                    angle = -delta_pos.y * SENSITIVITY
                    rotate_axis = self.right
                    self.position = glm.rotate(self.position - self.target, angle, rotate_axis) + self.target
                    self.up = glm.rotate(self.up, angle, rotate_axis)
                    self.forward = glm.rotate(self.forward, angle, rotate_axis)
                    self.total_vertical_angle += angle

        # Перемещение камеры по плоскости при зажатых клавише LEFT_SHIFT и средней кнопке мыши
        if glfw.get_key(self.app.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            if glfw.get_mouse_button(self.app.window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS:
                current_mouse_pos = glm.vec2(*glfw.get_cursor_pos(self.app.window))
                delta_pos = current_mouse_pos - glm.vec2(self.mouse_pos)
                self.mouse_pos = current_mouse_pos
                if delta_pos != 0:
                    self.position -= self.right * delta_pos.x * SENSITIVITY * velocity * 25
                    self.target -= self.right * delta_pos.x * SENSITIVITY * velocity * 25
                    self.position += self.up * delta_pos.y * SENSITIVITY * velocity * 25
                    self.target += self.up * delta_pos.y * SENSITIVITY * velocity * 25

        # Перемещение камеры по осям координат с помощью клавиш-стрелочек
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.position += glm.vec3(1, 0, 0) * velocity
            self.target += glm.vec3(1, 0, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_LEFT) == glfw.PRESS:
            self.position -= glm.vec3(1, 0, 0) * velocity
            self.target -= glm.vec3(1, 0, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS:
            self.position += glm.vec3(0, 1, 0) * velocity
            self.target += glm.vec3(0, 1, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS:
            self.position -= glm.vec3(0, 1, 0) * velocity
            self.target -= glm.vec3(0, 1, 0) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_DOWN) == glfw.PRESS:
            self.position += glm.vec3(0, 0, 1) * velocity
            self.target += glm.vec3(0, 0, 1) * velocity
        if glfw.get_key(self.app.window, glfw.KEY_UP) == glfw.PRESS:
            self.position -= glm.vec3(0, 0, 1) * velocity
            self.target -= glm.vec3(0, 0, 1) * velocity

        # Выравнивание камеры по осям координат сс помощью клавиш на нумпаде
        if glfw.get_key(self.app.window, glfw.KEY_KP_8) == glfw.PRESS:
            distance = glm.distance(self.position, self.target)
            self.position = self.target + glm.vec3(0, 0, distance)
            self.up = glm.vec3(0, 1, 0)
            self.right = glm.vec3(1, 0, 0)
            self.forward = glm.vec3(0, 0, -1)
            self.total_horizontal_angle = 0.0
            self.total_vertical_angle = 0.0
        if glfw.get_key(self.app.window, glfw.KEY_KP_2) == glfw.PRESS:
            distance = glm.distance(self.position, self.target)
            self.position = self.target + glm.vec3(0, 0, -distance)
            self.up = glm.vec3(0, 1, 0)
            self.right = glm.vec3(-1, 0, 0)
            self.forward = glm.vec3(0, 0, 1)
            self.total_horizontal_angle = 0.0
            self.total_vertical_angle = 0.0
        if glfw.get_key(self.app.window, glfw.KEY_KP_9) == glfw.PRESS:
            distance = glm.distance(self.position, self.target)
            self.position = self.target + glm.vec3(0, distance, 0)
            self.up = glm.vec3(0, 0, -1)
            self.right = glm.vec3(1, 0, 0)
            self.forward = glm.vec3(0, -1, 0)
            self.total_horizontal_angle = 0.0
            self.total_vertical_angle = 0.0
        if glfw.get_key(self.app.window, glfw.KEY_KP_3) == glfw.PRESS:
            distance = glm.distance(self.position, self.target)
            self.position = self.target + glm.vec3(0, -distance, 0)
            self.up = glm.vec3(0, 0, 1)
            self.right = glm.vec3(1, 0, 0)
            self.forward = glm.vec3(0, 1, 0)
            self.total_horizontal_angle = 0.0
            self.total_vertical_angle = 0.0
        if glfw.get_key(self.app.window, glfw.KEY_KP_6) == glfw.PRESS:
            distance = glm.distance(self.position, self.target)
            self.position = self.target + glm.vec3(distance, 0, 0)
            self.up = glm.vec3(0, 1, 0)
            self.right = glm.vec3(0, 0, -1)
            self.forward = glm.vec3(-1, 0, 0)
            self.total_horizontal_angle = 0.0
            self.total_vertical_angle = 0.0
        if glfw.get_key(self.app.window, glfw.KEY_KP_4) == glfw.PRESS:
            distance = glm.distance(self.position, self.target)
            self.position = self.target + glm.vec3(-distance, 0, 0)
            self.up = glm.vec3(0, 1, 0)
            self.right = glm.vec3(0, 0, 1)
            self.forward = glm.vec3(1, 0, 0)
            self.total_horizontal_angle = 0.0
            self.total_vertical_angle = 0.0

        # Перемещение в центр сцены/к выбранному объекту с помощью клавишы 5 на нумпаде
        if glfw.get_key(self.app.window, glfw.KEY_KP_5) == glfw.PRESS:
            self.position -= self.target - glm.vec3(0, 0, 0)
            self.target = glm.vec3(0, 0, 0)

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)

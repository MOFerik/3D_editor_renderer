import glm

class Light:
    def __init__(self, position = (6, 6, 6), color = (1, 1, 1)):
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        #интенсивность
        self.Ia = 0.1 * self.color #эмбиент
        self.Id = 0.8 * self.color #диффузия
        self.Is = 1.0 * self.color #блики
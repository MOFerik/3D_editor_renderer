import numpy as np
import math
import re
import glm
import fileinput


class VBO:
    def __init__(self, ctx, name):
        self.ctx = ctx
        self.vbo = 0
        if name == 'cube':
            self.vbo = CubeVBO(ctx)
        elif name == 'pyramid':
            self.vbo = PyramidVBO(ctx)
        elif name == 'sphere':
            self.vbo = SphereVBO(ctx)
        elif name == 'plane':
            self.vbo = PlaneVBO(ctx)
        else:
            self.vbo = CustomVBO(ctx, name)

    def destroy(self):
        self.vbo = 0


class BaseVBO:
    def __init__(self, ctx):
        self.vertices: list = self.get_vertices()
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.format: str = None
        self.attrib: list = None

    def get_vertex_data(self): ...

    def get_vertices(self):
        return [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)]

    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def change_vertices(self, vertices):
        self.vertices = []
        for vert in vertices:
            self.vertices.append(glm.vec3(vert))
        self.vbo = self.get_vbo()

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def destroy(self):
        self.vbo.release()


class CubeVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        vertices = self.vertices
        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]
        vertex_data = self.get_data(vertices, indices)

        tex_coord = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [(0, 2, 3), (0, 1, 2),
                             (0, 2, 3), (0, 1, 2),
                             (0, 1, 2), (2, 3, 0),
                             (2, 3, 0), (2, 0, 1),
                             (0, 2, 3), (0, 1, 2),
                             (3, 1, 2), (3, 0, 1)]
        tex_coord_data = self.get_data(tex_coord, tex_coord_indices)

        normals = [(0, 0, 1) * 6,
                   (1, 0, 0) * 6,
                   (0, 0, -1) * 6,
                   (-1, 0, 0) * 6,
                   (0, 1, 0) * 6,
                   (0, -1, 0) * 6]
        normals = np.array(normals, dtype='f4').reshape(36, 3)

        vertex_data = np.hstack([normals, vertex_data])
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data

    def get_vertices(self):
        return [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)]

class PyramidVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        vertices = self.vertices
        indices = [(0, 1, 2), (0, 2, 3),
                   (0, 3, 4), (0, 4, 1),
                   (3, 2, 1), (4, 3, 1)]
        vertex_data = self.get_data(vertices, indices)

        tex_coord = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [(0, 2, 3), (0, 1, 2),
                             (0, 2, 3), (0, 1, 2),
                             (0, 1, 2), (2, 3, 0)]
        tex_coord_data = self.get_data(tex_coord, tex_coord_indices)

        normals = [(0, 1, -1) * 3,
                   (-1, 1, 0) * 3,
                   (0, 1, 1) * 3,
                   (1, 1, 0) * 3,
                   (0, -1, 0) * 3,
                   (0, -1, 0) * 3]
        normals = np.array(normals, dtype='f4').reshape(18, 3)

        vertex_data = np.hstack([normals, vertex_data])
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data

    def get_vertices(self):
        return [(0, 1, 0), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (1, -1, 1)]


class SphereVBO(BaseVBO):
    def __init__(self, app):
        super().__init__(app)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        vertices = self.vertices
        indices = []
        temp_norm = []
        norm_id = []
        normals = []
        tex_coord = [(0, 0), (1, 0), (1/2, math.sqrt(2)/2)]
        tex_coord_indices = []
        n = 0
        t = 0
        with open('objects/Sphere/untitled.obj', encoding="utf-8") as f:
            i = 0
            while (i < 1000):
                line = f.readline()
                if 'vn' in line:
                    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                    rx = re.compile(numeric_const_pattern, re.VERBOSE)
                    norm = rx.findall(line)
                    temp_norm.append((float(norm[0]), float(norm[1]), float(norm[2])))
                    n += 3
                    i += 1
                elif 'f' in line:
                    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                    rx = re.compile(numeric_const_pattern, re.VERBOSE)
                    ind = rx.findall(line)
                    indices.append((int(ind[0]) - 1, int(ind[3]) - 1, int(ind[6]) - 1))
                    norm_id.append((int(ind[2]) - 1, int(ind[5]) - 1, int(ind[8]) - 1))
                    i += 1
                else:
                    i += 1
        for k in range(n//3, len(indices)):
            temp_norm.append((0, 0, 0, 0, 0, 0, 0, 0, 0))
        for j in range(0, len(indices)):
            normals.append((temp_norm[norm_id[j][0]], temp_norm[norm_id[j][1]], temp_norm[norm_id[j][2]]))
            tex_coord_indices.append((0, 1, 2))
        vertex_data = self.get_data(vertices, indices)
        tex_coord_data = self.get_data(tex_coord, tex_coord_indices)
        n = len(normals) * 3
        normals = np.array(normals, dtype='f4').reshape(n, 3)
        vertex_data = np.hstack([normals, vertex_data])
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data

    def get_vertices(self):
        vertices = []
        with open('objects/Sphere/untitled.obj', encoding="utf-8") as f:
            i = 0
            while (i < 1000):
                line = f.readline()
                if 'vn' in line:
                    return vertices
                if 'v ' in line:
                    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                    rx = re.compile(numeric_const_pattern, re.VERBOSE)
                    vert = rx.findall(line)
                    vertices.append(glm.vec3(float(vert[0]), float(vert[1]), float(vert[2])))
                    i += 1
        return vertices

    def change_vertices(self, vertices):
        i = 0
        for line in fileinput.input("objects/Sphere/untitled.obj", inplace=True):
            if 'vn' in line or 'vt' in line:
                print('{}'.format(line), end='')
            elif 'v' in line:
                #v 0.000000 0.382683 -0.923880
                print('v {} {} {}'.format(vertices[i][0], vertices[i][1], vertices[i][2]), end='\n')
                i += 1
            else:
                print('{}'.format(line), end='')
        self.vertices = self.get_vertices()
        self.vbo = self.get_vbo()


class PlaneVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        vertices = self.vertices
        indices = [(0, 2, 3), (0, 1, 2),
                   (0, 3, 2), (0, 2, 1)]
        vertex_data = self.get_data(vertices, indices)

        tex_coord = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [(0, 2, 3), (0, 1, 2),
                             (0, 2, 3), (0, 1, 2)]
        tex_coord_data = self.get_data(tex_coord, tex_coord_indices)

        normals = [(0, 1, 0) * 3,
                   (0, 1, 0) * 3,
                   (0, -1, 0) * 3,
                   (0, -1, 0) * 3]
        normals = np.array(normals, dtype='f4').reshape(12, 3)

        vertex_data = np.hstack([normals, vertex_data])
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data

    def get_vertices(self):
        return [(-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1)]


class CustomVBO:
    def __init__(self, ctx, name):
        self.name = "{}".format(name)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']
        self.vertices: list = self.get_vertices()
        self.ctx = ctx
        self.vbo = self.get_vbo()

    def get_vertex_data(self):
        vertices = self.vertices
        indices = []
        temp_norm = []
        norm_id = []
        normals = []
        tex_coord = [(0, 0), (1, 0), (1/2, math.sqrt(2)/2)]
        tex_coord_indices = []
        n = 0
        t = 0
        with open(self.name, encoding="utf-8") as f:
            i = 0
            while (i < 500000):
                line = f.readline()
                if 'vn' in line:
                    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                    rx = re.compile(numeric_const_pattern, re.VERBOSE)
                    norm = rx.findall(line)
                    temp_norm.append((float(norm[0]), float(norm[1]), float(norm[2])))
                    n += 3
                    i += 1
                elif 'f' in line:
                    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                    rx = re.compile(numeric_const_pattern, re.VERBOSE)
                    ind = rx.findall(line)
                    if (len(ind) > 6):
                        indices.append((int(ind[0]) - 1, int(ind[3]) - 1, int(ind[6]) - 1))
                        norm_id.append((int(ind[2]) - 1, int(ind[5]) - 1, int(ind[8]) - 1))
                    else:
                        indices.append((int(ind[0]) - 1, int(ind[2]) - 1, int(ind[4]) - 1))
                        norm_id.append((int(ind[1]) - 1, int(ind[3]) - 1, int(ind[5]) - 1))
                    i += 1
                else:
                    if (not (' ' in line)) and i > 100:
                        i = 500000
                    i += 1
        for k in range(n//3, len(indices)):
            temp_norm.append((0, 0, 0, 0, 0, 0, 0, 0, 0))
        for j in range(0, len(indices)):
            normals.append((temp_norm[norm_id[j][0]], temp_norm[norm_id[j][1]], temp_norm[norm_id[j][2]]))
            tex_coord_indices.append((0, 1, 2))
        vertex_data = self.get_data(vertices, indices)
        tex_coord_data = self.get_data(tex_coord, tex_coord_indices)
        n = len(normals) * 3
        normals = np.array(normals, dtype='f4').reshape(n, 3)
        vertex_data = np.hstack([normals, vertex_data])
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data

    def get_vertices(self):
        vertices = []
        max = 0
        with open(self.name, encoding="utf-8") as f:
            i = 0
            while (i < 500000):
                line = f.readline()
                if 'vn' in line:
                    for i in range(0, len(vertices)):
                        vertices[i][0] = vertices[i][0] / max
                        vertices[i][1] = vertices[i][1] / max
                        vertices[i][2] = vertices[i][2] / max
                    return vertices
                if 'v ' in line:
                    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                    rx = re.compile(numeric_const_pattern, re.VERBOSE)
                    vert = rx.findall(line)
                    vertices.append(glm.vec3(float(vert[0]), float(vert[1]), float(vert[2])))
                    if float(vert[0]) > max:
                        max = float(vert[0])
                    elif float(vert[1]) > max:
                        max = float(vert[1])
                    elif float(vert[2]) > max:
                        max = float(vert[2])
                    i += 1
        for i in range(0, len(vertices) - 1):
            vertices[i][0] = vertices[i][0] / max
            vertices[i][1] = vertices[i][1] / max
            vertices[i][2] = vertices[i][2] / max
        return vertices

    def change_vertices(self, vertices):
        i = 0
        for line in fileinput.input(self.name, inplace=True):
            if 'vn' in line or 'vt' in line:
                print('{}'.format(line), end='')
            elif 'v' in line:
                #v 0.000000 0.382683 -0.923880
                print('v {} {} {}'.format(vertices[i][0], vertices[i][1], vertices[i][2]), end='\n')
                i += 1
            else:
                print('{}'.format(line), end='')
        self.vertices = self.get_vertices()
        self.vbo = self.get_vbo()

    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def destroy(self):
        self.vbo.release()
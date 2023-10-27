from math import cos, sin, sqrt, pi

import PIL
import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image


def third_tr(ang, dx, dy):
    return [0.43 * cos(ang) + 0.61 * sin(ang) + dx,
            - 0.25 * cos(ang) - 0.35 * sin(ang) + dy,
            0.71 * cos(ang) - 0.5 * sin(ang)]


def second_tr(ang, dx, dy):
    return [-0.43 * cos(ang) - 0.61 * sin(ang) + dx,
            - 0.25 * cos(ang) - 0.35 * sin(ang) + dy,
            0.71 * cos(ang) - 0.5 * sin(ang)]


def first_tr(ang, dx, dy):
    return [0 + dx,
            -0.5 * cos(ang) - 0.71 * sin(ang) + dy,
            0.71 * cos(ang) - 0.5 * sin(ang)]


class Config:
    def __init__(self):
        # угол вращения сцены
        self.angle = 0.
        # хар-ки тетраэдра
        #    длина ребра
        self.edge_len = 1
        #    нижний центр
        self.lower_center = [0, 0, 0]
        #    верхняя вершина
        self.upper_vert = 'D'
        #    координаты центров рёбер противоположных вершинам нижней грани
        self.centers = {}
        #    координаты вершин
        self.vertices = {}
        #    координаты вершин для текстурирования
        self.tex_vertices = {}
        # хар-ки траектории перемещения тетраэдра (окружности)
        #    var и var_max - для перемещения по кругу
        self.var = 0
        self.var_max = 5

        self.show_trajectory = False
        #    тип нижней грани 0 или 1 (всегда чередуется при перекате):
        ''' 
            0    |     1
        ---------+-----------  
            x    |   xxхxx
           xхx   |    xxx
          xxxxx  |     x
        '''
        self.lower = 0
        #    упорядоченные вершины нижней грани по возрастанию х
        self.keys = []
        #    индекс траектории, по которой будут перемещаться вершины тетраедра
        self.trajectory_index = 0
        #    список координат xyz для перемещения вершин тетраэдра по окружности
        self.coords = []
        #    индекс координаты
        self.coord_index = 0
        # 200
        # self.diff_index = 244
        # 100
        # self.diff_index = 122
        # 25
        self.diff_index = 31
        self.parts = 25

        #    инициализируем начальное положение вершин тетраэдра
        self.init_vertices()
        #    получаем значения центров рёбер противоположных вершинам нижней грани, а также верхнюю вершину
        self.get_centers()

        self.calculate_trajectory()

        #    расчёт траектории при движении по кругу
        # self.calculate_cycle_moving()

    def init_vertices(self):
        cx, cy, cz = self.lower_center
        vert = {"A": [cx + self.edge_len / 2, cy + (-self.edge_len / 6) * sqrt(3), cz],
                "B": [cx - self.edge_len / 2, cy + (-self.edge_len / 6) * sqrt(3), cz],
                "C": [cx, cy + (self.edge_len / 3) * sqrt(3), cz],
                "D": [cx, cy, cz + self.edge_len * sqrt(2 / 3)]}
        self.vertices = vert.copy()
        self.tex_vertices = vert.copy()
        print(vert)

    # центры - сдвиги в формулах траекторий
    def get_centers(self):
        lower_verts = {}
        for vert in self.vertices.keys():
            if self.vertices[vert][2] == 0.:
                lower_verts[vert] = self.vertices[vert]
            else:
                self.upper_vert = vert

        self.keys = []
        value = []
        for vert in lower_verts.keys():
            self.keys.append(vert)
            value.append(lower_verts[vert])

        for i in range(len(value)):
            for j in range(len(value) - i - 1):
                if value[j] > value[j + 1]:
                    value[j], value[j + 1] = value[j + 1], value[j]
                    self.keys[j], self.keys[j + 1] = self.keys[j + 1], self.keys[j]

        try:
            edges = {self.keys[2]: (self.keys[0], self.keys[1]),
                     self.keys[1]: (self.keys[0], self.keys[2]),
                     self.keys[0]: (self.keys[1], self.keys[2])}
        except IndexError:
            print(self.vertices)
            edges = {}
            return

        for vert in self.keys:
            literal_a = edges[vert][0]
            literal_b = edges[vert][1]
            a = self.vertices[literal_a]
            b = self.vertices[literal_b]
            center = [(a[0] + b[0]) / 2,
                      (a[1] + b[1]) / 2,
                      0]
            self.centers[vert] = center

    def on_floor(self):
        counter = 0
        for vert in self.vertices.keys():
            if self.vertices[vert][2] == 0.:
                counter += 1
        return counter == 3

    def calculate_trajectory(self):
        self.coords.clear()
        for j in range(3):
            ans = []
            literal_vert = self.keys[j]
            center = self.centers[literal_vert]
            for i in range(int(-pi * self.parts), int(pi * self.parts), 1):
                angle = i / self.parts
                match self.lower:
                    case 0:
                        match j:
                            case 0:
                                cx, cy, cz = second_tr(-angle, center[0], center[1])
                            case 1:
                                cx, cy, cz = first_tr(angle, center[0], center[1])
                            case 2:
                                cx, cy, cz = third_tr(-angle, center[0], center[1])
                            case _:
                                return
                    case 1:
                        match j:
                            case 0:
                                cx, cy, cz = third_tr(angle, center[0], center[1])
                            case 1:
                                cx, cy, cz = first_tr(-angle, center[0], center[1])
                            case 2:
                                cx, cy, cz = second_tr(angle, center[0], center[1])
                            case _:
                                return
                    case _:
                        return
                if cz < 0:
                    continue
                ans.append([cx, cy, cz])
            if ans[len(ans) - 1][2] != 0:
                ans.append([ans[len(ans) - 1][0], ans[len(ans) - 1][1], 0.])
            if ans[0][2] != 0:
                ans.insert(0, [ans[0][0], ans[0][1], 0.])
            print(ans)
            self.coords.append(ans)

    def calculate_cycle_moving(self):
        ans = []
        for i in range(int(-pi * 25), int(pi * 25), 1):
            angle = i / 25
            match self.var:
                case 0:
                    cx, cy, cz = first_tr(angle, 0, -0.29)
                case 1:
                    cx, cy, cz = second_tr(angle, -0.25, -0.72)
                case 2:
                    cx, cy, cz = third_tr(-angle, -0.75, -0.72)
                case 3:
                    cx, cy, cz = first_tr(-angle, -1, -0.29)
                case 4:
                    cx, cy, cz = second_tr(-angle, -0.75, 0.14)
                case 5:
                    cx, cy, cz = third_tr(angle, -0.25, 0.14)
                case _:
                    return
            if cz < 0:
                continue
            ans.append((cx, cy, cz))
        print(ans)
        self.coords = ans


cfg = Config()


def set_lightning_params():
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 10, 2])
    color = [1., 1., 1., 1.]
    glLightfv(GL_LIGHT0, GL_DIFFUSE, color)
    glLightfv(GL_LIGHT0, GL_SPECULAR, color)
    glLightfv(GL_LIGHT0, GL_AMBIENT, color)


def read_texture(filename):
    image = PIL.Image.open(filename)
    img_data = numpy.array(list(image.getdata()), numpy.int64)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)


def draw_tex_triangle(name_a: str, name_b: str, name_c: str):
    a, b, c = (cfg.vertices[name_a], cfg.tex_vertices[name_a]), \
              (cfg.vertices[name_b], cfg.tex_vertices[name_b]), \
              (cfg.vertices[name_c], cfg.tex_vertices[name_c])

    glBegin(GL_TRIANGLES)
    for vert, tex_vert in [a, b, c]:
        glVertex3fv(vert)
        glTexCoord3fv(tex_vert)
    glEnd()


def draw_tetrahedron():
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1., 1., 1., 1.])
    # ABC
    draw_tex_triangle("A", "B", "C")
    # ABD
    draw_tex_triangle("A", "B", "D")
    # ACD
    draw_tex_triangle("A", "C", "D")
    # BCD
    draw_tex_triangle("B", "C", "D")


def draw_plane(n: int = 10):
    color = [.7, .6, .3, 1.]
    glPushMatrix()
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, color)
    glBegin(GL_QUADS)

    glVertex2fv([-n, -n])
    glVertex2fv([-n, n])
    glVertex2fv([n, n])
    glVertex2fv([n, -n])
    glEnd()
    glPopMatrix()


def draw_trajectory():
    color = [.7, .2, .1, 1.]
    glPushMatrix()
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, color)
    glBegin(GL_LINE_STRIP)
    for vert in cfg.coords[cfg.trajectory_index]:
        glVertex3fv(vert)
    glEnd()
    glPopMatrix()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)

    glPushMatrix()
    set_lightning_params()
    draw_plane(2)
    if cfg.show_trajectory:
        draw_trajectory()
    glEnable(GL_TEXTURE_2D)
    draw_tetrahedron()
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

    glRotatef(cfg.angle, 0., 0., 1.)
    glutSwapBuffers()
    glutPostRedisplay()


def special(key, x, y):
    global cfg
    if key == GLUT_KEY_DOWN:
        cfg.coord_index += 1
        if cfg.coord_index + cfg.diff_index < len(cfg.coords[cfg.trajectory_index]):
            cfg.vertices[cfg.keys[cfg.trajectory_index]] = cfg.coords[cfg.trajectory_index][cfg.coord_index]
            cfg.vertices[cfg.upper_vert] = cfg.coords[cfg.trajectory_index][cfg.coord_index + cfg.diff_index]
        else:
            print('allez-hop!')
            cfg.lower = (cfg.lower + 1) % 2
            cfg.get_centers()
            cfg.calculate_trajectory()
            cfg.coord_index = 0

    if key == GLUT_KEY_UP:
        cfg.coord_index -= 1
        if cfg.coord_index >= 0:
            cfg.vertices[cfg.keys[cfg.trajectory_index]] = cfg.coords[cfg.trajectory_index][cfg.coord_index]
            cfg.vertices[cfg.upper_vert] = cfg.coords[cfg.trajectory_index][cfg.coord_index + cfg.diff_index]
        else:
            # print('allez-hop!')
            cfg.coord_index += 1
            # cfg.lower = (cfg.lower + 1) % 2
            # cfg.get_centers()
            # cfg.calculate_trajectory()
            # cfg.coord_index = len(cfg.coords[cfg.trajectory_index]) - cfg.diff_index
    if key == GLUT_KEY_PAGE_UP:
        if cfg.on_floor():
            cfg.trajectory_index += 1
            if cfg.trajectory_index > 2:
                cfg.trajectory_index = 0

    if key == GLUT_KEY_PAGE_DOWN:
        if cfg.angle == 0:
            cfg.angle = 0.05
        else:
            cfg.angle = 0

    if key == GLUT_KEY_HOME:
        if cfg.show_trajectory:
            cfg.show_trajectory = False
        else:
            cfg.show_trajectory = True

    if key == GLUT_KEY_END:
        cfg = Config()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 800)
    glutInitWindowPosition(360, 35)
    glutCreateWindow(f'lab3')
    glClearColor(0.3, 0.5, 0.9, 1.)

    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)

    set_lightning_params()

    read_texture('test.png')

    glutDisplayFunc(display)
    glutSpecialFunc(special)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(40., 1., 1., 40.)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(-3, -3, 5,
              0., 0., 0.,
              0, 0, 1)
    glPushMatrix()
    glutMainLoop()


if __name__ == "__main__":
    main()

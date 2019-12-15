
class Vertex2D:

    def __init__(self, x: float, y: float, t_x: float, t_y: float, color: int):
        self._x = x
        self._y = y
        self._t_x = t_x
        self._t_y = t_y
        self._color = color

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val: int):
        self._x = val

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val: int):
        self._y = val

    @property
    def t_x(self):
        return self._t_x

    @t_x.setter
    def t_x(self, val: int):
        self._t_x = val

    @property
    def t_y(self):
        return self._t_y

    @t_y.setter
    def t_y(self, val: int):
        self._t_y = val

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color


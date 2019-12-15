
from pyrr import rectangle, matrix44

from src.internal.render_target import RenderTarget
from src.model.vertex_2d import Vertex2D


class RenderSurface:

    def __init__(self, area, name="Surface"):
        self._vertices = []
        self._render_area = area
        self._render_target = RenderTarget(int(rectangle.width(area)), int(rectangle.height(area)))
        self._projection = matrix44.create_orthogonal_projection(
            0,
            self._render_target.width,
            self._render_target.height,
            0,
            0,
            1000.0
        )

        self._name = name
        self.set_area(area)

    @property
    def name(self):
        return self._name

    def set_area(self, area):
        self._render_area = area
        self._vertices[0] = Vertex2D(rectangle.left(area), rectangle.bottom(area), 0, 0, 0xFFFFFFFF)
        self._vertices[2] = Vertex2D(rectangle.right(area), rectangle.bottom(area), 1, 0, 0xFFFFFFFF)
        self._vertices[3] = Vertex2D(rectangle.right(area), rectangle.top(area), 1, 1, 0xFFFFFFFF)
        self._vertices[4] = Vertex2D(rectangle.left(area), rectangle.top(area), 0, 1, 0xFFFFFFFF)

    def resize_surface(self, width: int, height: int):
        if width != self._render_target.width or height != self._render_target.height:
            self._render_target.dispose()
            self._render_target = RenderTarget(width, height)
            self._projection = matrix44.create_orthogonal_projection(
                0,
                self._render_target.width,
                self._render_target.height,
                0,
                0,
                1000.0
            )

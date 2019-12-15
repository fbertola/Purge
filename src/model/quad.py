from bgfx import BGFX_STATE_BLEND_ALPHA
from pyrr import rectangle

from src.internal.texture_2d import Texture2D
from src.model.vertex_2d import Vertex2D


class Quad:
    _v0: Vertex2D
    _v1: Vertex2D
    _v2: Vertex2D
    _v3: Vertex2D

    _region = None

    _blend_mode: int

    def __init__(self, texture: Texture2D, src_rect=None, dest_rect=None):
        self._v0 = Vertex2D(0, 0, 0, 0, 0xFFFFFFFF)
        self._v1 = Vertex2D(0, 0, 0, 0, 0xFFFFFFFF)
        self._v2 = Vertex2D(0, 0, 0, 0, 0xFFFFFFFF)
        self._v3 = Vertex2D(0, 0, 0, 0, 0xFFFFFFFF)

        self._blend_mode = BGFX_STATE_BLEND_ALPHA

        if texture:
            self.set_region(texture, src_rect)
            self.set_area(dest_rect)

    def set_area(self, dest_rect=None) -> None:
        if not dest_rect:
            dest_x1 = 0
            dest_y1 = 0
            dest_x2 = rectangle.width(self._region)
            dest_y2 = rectangle.height(self._region)
        else:
            dest_x1 = rectangle.left(dest_rect)
            dest_y1 = rectangle.bottom(dest_rect)
            dest_x2 = rectangle.right(dest_rect)
            dest_y2 = rectangle.top(dest_rect)

        self._v0.x = dest_x1
        self._v0.y = dest_y1
        self._v1.x = dest_x2
        self._v1.y = dest_y1
        self._v2.x = dest_x2
        self._v2.y = dest_y2
        self._v3.x = dest_x1
        self._v3.y = dest_y2

    def set_region(self, texture: Texture2D, src_rect=None) -> None:
        if not src_rect:
            self._region = rectangle.create(0, 0, texture.width, texture.height)

            ax = 0.0
            ay = 0.0
            bx = 1.0
            by = 1.0
        else:
            self._region = src_rect
            inv_tex_w = 1.0 / texture.width
            inv_tex_h = 1.0 / texture.height

            ax = rectangle.left(src_rect) * inv_tex_w
            ay = rectangle.bottom(src_rect) * inv_tex_h
            bx = rectangle.right(src_rect) * inv_tex_w
            by = rectangle.top(src_rect) * inv_tex_h

        self._v0._t_x = ax
        self._v0._t_y = ay
        self._v1._t_x = bx
        self._v1._t_y = ay
        self._v2._t_x = bx
        self._v2._t_y = by
        self._v3._t_x = ax
        self._v3._t_y = by

    def set_color(self, abgr_color: int) -> None:
        self._v0.color = abgr_color
        self._v1.color = abgr_color
        self._v2.color = abgr_color
        self._v3.color = abgr_color

    def set_colors(self, top_left: int, top_right: int, bottom_left: int, bottom_right: int) -> None:
        self._v0.color = top_left
        self._v1.color = top_right
        self._v2.color = bottom_right
        self._v3.color = bottom_left

    def get_region_rect(self, texture: Texture2D):
        return rectangle.create_from_bounds(
            self._v0.t_x * texture.width,
            self._v0.t_y * texture.height,
            self._v2.t_x * texture.width,
            self._v2.t_y * texture.height
        )

    @property
    def width(self):
        return abs(self._v1.x - self._v0.x)

    def height(self):
        return abs(self._v2.y - self._v1.y)

from array import array
from typing import List

from bgfx import (
    bgfx,
    as_void_ptr,
    BGFX_STATE_WRITE_A,
    BGFX_STATE_WRITE_RGB,
    BGFX_STATE_BLEND_ALPHA,
    BGFX_CLEAR_COLOR,
    BGFX_CLEAR_DEPTH,
    BGFX_SAMPLER_UVW_CLAMP,
    BGFX_SAMPLER_POINT,
)

from src.internal.render_surface import RenderSurface
from src.internal.shader_program import ShaderProgram
from ctypes import memmove, addressof, sizeof

from src.model.vertex_2d import Vertex2D


class RenderPipeline:
    _render_surfaces: List[RenderSurface] = []
    _current_shader_program = None
    _current_render_pass = 0
    _max_render_pass = 0
    _current_blend_mode = 0
    _vertex_index = 0
    _screen_projection = None

    def __init__(self, max_vertex_count: int, render_area):

        self.add_surface(render_area, "MainSurface")

        self._max_vertex_count = max_vertex_count

        self._vertices = [None] * max_vertex_count
        self._indices = array("B", [0] * int(max_vertex_count / 4 * 6))

        i, j = 0, 0
        while i < max_vertex_count:
            self._indices[i + 0] = j + 0
            self._indices[i + 1] = j + 1
            self._indices[i + 2] = j + 2
            self._indices[i + 3] = j + 0
            self._indices[i + 4] = j + 2
            self._indices[i + 5] = j + 3
            i += 6
            j += 4

        self._vertex_layout = bgfx.VertexLayout()
        self._vertex_layout.begin().add(
            bgfx.Attrib.Position, 2, bgfx.AttribType.Float
        ).add(bgfx.Attrib.TexCoord0, 2, bgfx.AttribType.Float).add(
            bgfx.Attrib.Color0, 4, bgfx.AttribType.Uint8, True
        ).end()

        ib_memory = bgfx.copy(as_void_ptr(self._indices), len(self._indices))
        self._index_buffer = bgfx.createIndexBuffer(ib_memory)

        base_render_state = BGFX_STATE_WRITE_RGB | BGFX_STATE_WRITE_A
        blending_state = BGFX_STATE_BLEND_ALPHA
        self._render_state = base_render_state | blending_state

    def reset(self):
        self._current_render_pass = 0
        self._max_render_pass = 0

    def set_blend_mode(self, blend_mode: int) -> None:
        if self._current_blend_mode == blend_mode:
            return

        if self._vertex_index > 0:
            self.submit()

        base_render_state = BGFX_STATE_WRITE_RGB | BGFX_STATE_WRITE_A
        self._current_blend_mode = blend_mode
        self._render_state = base_render_state | blend_mode

    def set_shader_program(self, shader_program: ShaderProgram) -> None:
        if self._current_shader_program == shader_program:
            return

        if self._vertex_index > 0:
            self.submit()

        self._current_shader_program = shader_program

    def set_render_surface(self, surface: RenderSurface) -> None:
        if self._vertex_index > 0:
            self.submit()

        if surface:
            self._current_render_pass += 1

            if self._current_render_pass > self._max_render_pass:
                self._max_render_pass = self._current_render_pass
        else:
            surface = self._render_surfaces[0]
            self._current_render_pass = 0

        projection = surface.projection.flatten()

        bgfx.setViewFrameBuffer(
            self._current_render_pass, surface.render_target.frame_buffer
        )
        bgfx.touch(self._current_render_pass)
        bgfx.setViewClear(
            self._current_render_pass,
            BGFX_CLEAR_COLOR | BGFX_CLEAR_DEPTH,
            0x00000000 if surface != self._render_surfaces[0] else 0x000000FF,
        )
        bgfx.setViewRect(self._current_render_pass, 0, 0, surface.width, surface.height)
        bgfx.setViewTransform(self._current_render_pass, None, as_void_ptr(projection))

    def set_scissor(self, x: int, y: int, w: int, h: int) -> None:
        bgfx.setScissor(self._current_render_pass, x, y, w, h)

    def add_surface(self, area, name="Surface") -> RenderSurface:
        surface = RenderSurface(area, name)

        self._render_surfaces.append(surface)

        return surface

    def draw_surfaces(self) -> None:
        for surface, i in self._render_surfaces:
            vertex_buffer = bgfx.TransientVertexBuffer()
            bgfx.allocTransientVertexBuffer(vertex_buffer, 4, self._vertex_layout)
            memmove(
                addressof(vertex_buffer.data),
                surface.vertices,
                sizeof(surface.vertices),
            )

            render_pass = self._max_render_pass + i + 1
            bgfx.setViewRect(render_pass, 0, 0, game.width, game.height)

            projection = self._screen_projection.flatten()
            bgfx.setViewTransform(render_pass, None, as_void_ptr(projection))
            bgfx.setTexture(
                0,
                self._current_shader_program.samplers[0],
                surface.render_target.texture,
                BGFX_SAMPLER_POINT | BGFX_SAMPLER_UVW_CLAMP,
            )
            bgfx.setRenderState(self._render_state)
            bgfx.setIndexBuffer(self._index_buffer, 0, 6)
            bgfx.setVertexBuffer(0, vertex_buffer, 0, self._vertex_index)
            bgfx.submit(
                render_pass,
                self._current_shader_program.program
                if not surface.shader
                else surface.shader.program,
            )

    def resize_surfaces(self, width: int, height: int) -> None:
        for surface in self._render_surfaces:
            surface.resize_surface(width, height)

    def set_surfaces_area(self, area) -> None:
        for surface in self._render_surfaces:
            surface.set_area(area)

    def set_screen_projection(self, mat) -> None:
        self._screen_projection = mat

    def submit(self):
        if self._vertex_index == 0:
            return

        vertex_buffer = bgfx.TransientVertexBuffer()
        bgfx.allocTransientVertexBuffer(vertex_buffer, 4, self._vertex_layout)
        memmove(
            addressof(vertex_buffer.data),
            surface.vertices,
            self._vertex_index * Vertex2D.stride,
        )

        bgfx.setTexture(
            0,
            self._current_shader_program.samplers[0],
            self._current_texture.texture,
            bgfx.TextureFormat.BGRA8,
        )
        bgfx.setRenderState(self._render_state)
        bgfx.setIndexBuffer(self._index_buffer, 0, self._vertex_index / 4 * 6)
        bgfx.setVertexBuffer(0, vertex_buffer, 0, self._vertex_index)

        self._current_shader_program.submit_values()

        bgfx.setViewMode(self._current_render_pass, bgfx.ViewMode.Sequential)
        bgfx.submit(self._current_render_pass, self._current_shader_program.program)

        self._vertex_index = 0

    def push_quads(self):
        pass

    def dispose(self):
        bgfx.destroy(self._index_buffer)

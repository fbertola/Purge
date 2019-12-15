from array import array

from bgfx import bgfx, as_void_ptr, BGFX_STATE_WRITE_A, BGFX_STATE_WRITE_RGB, BGFX_STATE_BLEND_ALPHA
from typing import List, Optional
from src.internal.render_surface import RenderSurface
from src.internal.shader_program import ShaderProgram


class RenderPipeline:
    _render_surfaces: List[RenderSurface] = []
    _current_shader_program = None
    _current_render_pass = 0
    _max_render_pass = 0
    _current_blend_mode = 0
    _vertex_index = 0
    _screen_projection = None

    def __init__(self, graphic_context, max_vertex_count: int, render_area):

        # add surface

        self._max_vertex_count = max_vertex_count

        self._vertices = [None] * max_vertex_count
        self._indices = array('B', [0] * int(max_vertex_count / 4 * 6))

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
        self._vertex_layout.begin() \
            .add(bgfx.Attrib.Position, 2, bgfx.AttribType.Float) \
            .add(bgfx.Attrib.TexCoord0, 2, bgfx.AttribType.Float) \
            .add(bgfx.Attrib.Color0, 4, bgfx.AttribType.Uint8, True) \
            .end()

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

        projection = surface.projection

        # FIXME: fix these
        bgfx.setRendererTarget(self._current_render_pass, surface.render_target)
        bgfx.setClearColor(self._current_render_pass, 0x00000000 if surface != self._render_surfaces[0] else 0x000000FF)
        bgfx.setViewRect(self._current_render_pass, 0, 0, surface.width, surface.height)
        bgfx.setProjection(self._current_render_pass, projection)

    def set_scissor(self, x: int, y: int, w: int, h: int) -> None:
        bgfx.setScissor(self._current_render_pass, x, y, w, h)

    def add_surface(self, area, name = "Surface") -> RenderSurface:
        surface = RenderSurface(area, name)

        self._render_surfaces.append(surface)

        return surface

    def draw_surfaces(self) -> None:
        for surface, i in self._render_surfaces:
            pass
            # var vertex_buffer = new TransientVertexBuffer(4, Vertex2DLayout);
            #
            # fixed (void* v = surface.Vertices)
            # {
            #     Unsafe.CopyBlock((void*)vertex_buffer.Data, v, (uint)(4 * Vertex2D.Stride));
            # }
            #
            # var pass = (byte)(max_render_pass + index + 1);
            #
            # gfx.SetViewport(pass, 0, 0, Game.Instance.ScreenSize.W, Game.Instance.ScreenSize.H);
            #
            # var proj = screen_projection;
            #
            # gfx.SetProjection(pass, &proj.M11);
            #
            # //gfx.SetClearColor(pass, Color.Blue);
            #
            # Bgfx.SetTexture(0, current_shader_program.Samplers[0], surface.RenderTarget.NativeTexture, TextureFlags.FilterPoint | TextureFlags.ClampUVW);
            #
            # Bgfx.SetRenderState(render_state);
            #
            # Bgfx.SetIndexBuffer(index_buffer, 0, 6);
            #
            # Bgfx.SetVertexBuffer(0, vertex_buffer, 0, vertex_index);
            #
            # Bgfx.Submit(pass, surface.Shader?.Program ?? current_shader_program.Program);


    def resize_surfaces(self, width: int, height: int) -> None
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

        # var vertex_buffer = new TransientVertexBuffer(vertex_index, Vertex2DLayout);
        #
        # fixed (void* v = vertices)
        # {
        #     Unsafe.CopyBlock((void*)vertex_buffer.Data, v, (uint)(vertex_index * Vertex2D.Stride));
        # }
        #
        # Bgfx.SetTexture(0, current_shader_program.Samplers[0], current_texture.Texture, current_texture.TexFlags);
        #
        # Bgfx.SetRenderState(render_state);
        #
        # Bgfx.SetIndexBuffer(index_buffer, 0, vertex_index / 4 * 6);
        #
        # Bgfx.SetVertexBuffer(0, vertex_buffer, 0, vertex_index);
        #
        # current_shader_program.SubmitValues();
        #
        # Bgfx.SetViewMode(current_render_pass, ViewMode.Sequential);
        #
        # Bgfx.Submit(current_render_pass, current_shader_program.Program);

        self._vertex_index = 0

    def push_quads(self):
        pass

    def dispose(self):
        bgfx.destroy(self._index_buffer)

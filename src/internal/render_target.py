
from bgfx import bgfx


class RenderTarget:

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._frame_buffer = bgfx.createFrameBuffer(
            width,
            height,
            bgfx.TextureFormat.BGRA8,
            bgfx.TextureFlags.ClampU | bgfx.TextureFlags.ClampV | bgfx.TextureFlags.FilterPoint
        )
        self._texture = self._frame_buffer.getTexture()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def dispose(self) -> None:
        bgfx.destroy(self._frame_buffer)

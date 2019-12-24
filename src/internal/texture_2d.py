from bgfx import bgfx, as_void_ptr

from src.model.pixmap import Pixmap


class Texture2D:

    _texture = None
    _texture_flags = None

    def __init__(self, pixmap: Pixmap):
        self._width = pixmap.width
        self._height = pixmap.height
        self._texture = bgfx.createTexture2D(
            pixmap.width,
            pixmap.height,
            False,
            0,
            bgfx.TextureFormat.BGRA8,
            bgfx.copy(as_void_ptr(pixmap.pixels), len(pixmap.pixels)),
        )

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def texture(self):
        return self._texture

    def dispose(self) -> None:
        bgfx.destroy(self._texture)

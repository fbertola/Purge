from typing import Dict, Tuple, Sequence


class Pixmap:
    def __init__(self, pixels: bytes, width: int, height: int):
        self._pixels = self._swizzle_to_bgra(pixels)
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def pixels(self):
        return self._pixels

    def _swizzle_to_bgra(self, pixels: bytes) -> bytes:
        swizzled_pixels = bytearray(pixels)
        index = 0

        while index < len(pixels):
            r = self._pixels[index]
            g = self._pixels[index + 1]
            b = self._pixels[index + 2]
            a = self._pixels[index + 3]

            swizzled_pixels[index] = b
            swizzled_pixels[index + 1] = g
            swizzled_pixels[index + 2] = r
            swizzled_pixels[index + 3] = a

        return swizzled_pixels

    def _swizzle_to_rgba(self, pixels: bytes) -> bytes:
        swizzled_pixels = bytearray(len(pixels))
        index = 0

        while index < len(pixels):
            b = self._pixels[index]
            g = self._pixels[index + 1]
            r = self._pixels[index + 2]
            a = self._pixels[index + 3]

            swizzled_pixels[index] = r
            swizzled_pixels[index + 1] = g
            swizzled_pixels[index + 2] = b
            swizzled_pixels[index + 3] = a

        return swizzled_pixels

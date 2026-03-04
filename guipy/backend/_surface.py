import numpy as np
from guipy.backend._rect import Rect
from guipy.backend import _gpu


class Surface:
    """GPU-backed surface using moderngl FBO + texture."""

    def __init__(self, size, flags=0):
        w, h = int(size[0]), int(size[1])
        ctx = _gpu.get_context()
        self._texture = ctx.texture((w, h), 4)
        self._texture.filter = (ctx.NEAREST, ctx.NEAREST)
        self._fbo = ctx.framebuffer(color_attachments=[self._texture])
        self._fbo.clear(0.0, 0.0, 0.0, 0.0)

    @classmethod
    def _from_array(cls, arr):
        s = cls.__new__(cls)
        ctx = _gpu.get_context()
        h, w = arr.shape[:2]
        s._texture = ctx.texture((w, h), 4)
        s._texture.filter = (ctx.NEAREST, ctx.NEAREST)
        # OpenGL expects bottom-up row order
        flipped = np.flipud(arr).copy()
        s._texture.write(flipped.tobytes())
        s._fbo = ctx.framebuffer(color_attachments=[s._texture])
        return s

    def get_size(self):
        return self._texture.size

    def get_width(self):
        return self._texture.width

    def get_height(self):
        return self._texture.height

    def get_rect(self):
        w, h = self._texture.size
        return Rect(0, 0, w, h)

    def convert_alpha(self):
        return self

    def fill(self, color):
        c = _normalize_color(color)
        self._fbo.clear(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, c[3] / 255.0)

    def blit(self, source, pos):
        _gpu.blit_texture(self._fbo, self.get_size(),
                          source._texture, source.get_size(), pos)

    def copy(self):
        ctx = _gpu.get_context()
        w, h = self._texture.size
        data = self._fbo.read(components=4)
        new_tex = ctx.texture((w, h), 4)
        new_tex.filter = (ctx.NEAREST, ctx.NEAREST)
        new_tex.write(data)
        s = Surface.__new__(Surface)
        s._texture = new_tex
        s._fbo = ctx.framebuffer(color_attachments=[new_tex])
        return s


def _normalize_color(color):
    """Convert a color tuple (RGB or RGBA) to a 4-element RGBA tuple."""
    if len(color) == 3:
        return (color[0], color[1], color[2], 255)
    return tuple(color)

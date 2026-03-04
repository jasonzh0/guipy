import numpy as np
from guipy.backend._rect import Rect
from guipy.backend import _gpu


class Surface:
    """GPU-backed surface using moderngl FBO + texture.

    User-facing API works in logical pixels. Internally, textures are
    allocated at physical resolution (logical * dpi_scale) for HiDPI clarity.
    """

    def __init__(self, size, flags=0):
        w, h = int(size[0]), int(size[1])
        s = _gpu.get_dpi_scale()
        pw, ph = int(w * s), int(h * s)
        ctx = _gpu.get_context()
        self._texture = ctx.texture((pw, ph), 4)
        self._texture.filter = (ctx.NEAREST, ctx.NEAREST)
        self._fbo = ctx.framebuffer(color_attachments=[self._texture])
        self._fbo.clear(0.0, 0.0, 0.0, 0.0)
        self._logical_size = (w, h)

    @classmethod
    def _from_array(cls, arr, logical_size=None):
        s = cls.__new__(cls)
        ctx = _gpu.get_context()
        h, w = arr.shape[:2]
        s._texture = ctx.texture((w, h), 4)
        s._texture.filter = (ctx.NEAREST, ctx.NEAREST)
        # OpenGL expects bottom-up row order
        flipped = np.flipud(arr).copy()
        s._texture.write(flipped.tobytes())
        s._fbo = ctx.framebuffer(color_attachments=[s._texture])
        if logical_size is not None:
            s._logical_size = logical_size
        else:
            scale = _gpu.get_dpi_scale()
            s._logical_size = (int(w / scale), int(h / scale))
        return s

    def _phys_size(self):
        return self._texture.size

    def get_size(self):
        return self._logical_size

    def get_width(self):
        return self._logical_size[0]

    def get_height(self):
        return self._logical_size[1]

    def get_rect(self):
        return Rect(0, 0, self._logical_size[0], self._logical_size[1])

    def convert_alpha(self):
        return self

    def fill(self, color):
        c = _normalize_color(color)
        self._fbo.clear(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, c[3] / 255.0)

    def blit(self, source, pos):
        s = _gpu.get_dpi_scale()
        _gpu.blit_texture(
            self._fbo, self._phys_size(),
            source._texture, source._phys_size(),
            (pos[0] * s, pos[1] * s),
        )

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
        s._logical_size = self._logical_size
        return s


def _normalize_color(color):
    """Convert a color tuple (RGB or RGBA) to a 4-element RGBA tuple."""
    if len(color) == 3:
        return (color[0], color[1], color[2], 255)
    return tuple(color)

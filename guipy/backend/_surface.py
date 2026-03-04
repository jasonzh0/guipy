import numpy as np
from guipy.backend._rect import Rect


class Surface:
    """numpy-based replacement for pygame.Surface. Stores pixels as (h, w, 4) uint8 RGBA."""

    def __init__(self, size, flags=0):
        w, h = int(size[0]), int(size[1])
        self._pixels = np.zeros((h, w, 4), dtype=np.uint8)

    @classmethod
    def _from_array(cls, arr):
        s = cls.__new__(cls)
        s._pixels = arr
        return s

    def get_size(self):
        h, w = self._pixels.shape[:2]
        return (w, h)

    def get_width(self):
        return self._pixels.shape[1]

    def get_height(self):
        return self._pixels.shape[0]

    def get_rect(self):
        h, w = self._pixels.shape[:2]
        return Rect(0, 0, w, h)

    def convert_alpha(self):
        return self

    def fill(self, color):
        c = _normalize_color(color)
        self._pixels[:, :] = c

    def blit(self, source, pos):
        dx, dy = int(pos[0]), int(pos[1])
        src = source._pixels
        sh, sw = src.shape[:2]
        dh, dw = self._pixels.shape[:2]

        # Compute clipped region
        sx0 = max(0, -dx)
        sy0 = max(0, -dy)
        dx0 = max(0, dx)
        dy0 = max(0, dy)
        cw = min(sw - sx0, dw - dx0)
        ch = min(sh - sy0, dh - dy0)

        if cw <= 0 or ch <= 0:
            return

        src_region = src[sy0:sy0 + ch, sx0:sx0 + cw]
        dst_region = self._pixels[dy0:dy0 + ch, dx0:dx0 + cw]

        # Alpha compositing
        sa = src_region[:, :, 3:4].astype(np.float32) / 255.0
        da = dst_region[:, :, 3:4].astype(np.float32) / 255.0

        out_a = sa + da * (1.0 - sa)
        # Avoid division by zero
        safe_out_a = np.where(out_a > 0, out_a, 1.0)

        out_rgb = (src_region[:, :, :3].astype(np.float32) * sa +
                   dst_region[:, :, :3].astype(np.float32) * da * (1.0 - sa)) / safe_out_a

        self._pixels[dy0:dy0 + ch, dx0:dx0 + cw, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
        self._pixels[dy0:dy0 + ch, dx0:dx0 + cw, 3:4] = np.clip(out_a * 255, 0, 255).astype(np.uint8)

    def copy(self):
        return Surface._from_array(self._pixels.copy())


def _normalize_color(color):
    """Convert a color tuple (RGB or RGBA) to a 4-element RGBA tuple."""
    if len(color) == 3:
        return (color[0], color[1], color[2], 255)
    return tuple(color)

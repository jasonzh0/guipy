from guipy.backend import _gpu
from guipy.backend._rect import Rect


def _normalize_color(color):
    """Convert a color tuple (RGB or RGBA) to a 4-element RGBA tuple."""
    if len(color) == 3:
        return (color[0], color[1], color[2], 255)
    return tuple(color)


def rect(surface, color, rect_arg, width=0, border_radius=0, antialias=True):
    c = _normalize_color(color)
    if isinstance(rect_arg, Rect):
        rx, ry, rw, rh = rect_arg.x, rect_arg.y, rect_arg.w, rect_arg.h
    else:
        rx, ry, rw, rh = int(rect_arg[0]), int(rect_arg[1]), int(rect_arg[2]), int(rect_arg[3])
    s = _gpu.get_dpi_scale()
    _gpu.draw_rect(surface._fbo, surface._phys_size(), c,
                   rx * s, ry * s, rw * s, rh * s,
                   width * s, border_radius * s)


def circle(surface, color, center, radius, width=0, antialias=True):
    c = _normalize_color(color)
    s = _gpu.get_dpi_scale()
    _gpu.draw_circle(surface._fbo, surface._phys_size(), c,
                     int(center[0]) * s, int(center[1]) * s,
                     int(radius) * s, width * s)


def line(surface, color, start, end, width=1, antialias=True):
    c = _normalize_color(color)
    s = _gpu.get_dpi_scale()
    _gpu.draw_line(surface._fbo, surface._phys_size(), c,
                   int(start[0]) * s, int(start[1]) * s,
                   int(end[0]) * s, int(end[1]) * s,
                   width * s)

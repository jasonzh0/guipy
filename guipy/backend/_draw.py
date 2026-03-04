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
    _gpu.draw_rect(surface._fbo, surface.get_size(), c, rx, ry, rw, rh, width, border_radius)


def circle(surface, color, center, radius, width=0, antialias=True):
    c = _normalize_color(color)
    _gpu.draw_circle(surface._fbo, surface.get_size(), c,
                     int(center[0]), int(center[1]), int(radius), width)


def line(surface, color, start, end, width=1, antialias=True):
    c = _normalize_color(color)
    _gpu.draw_line(surface._fbo, surface.get_size(), c,
                   int(start[0]), int(start[1]), int(end[0]), int(end[1]), width)

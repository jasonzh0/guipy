import numpy as np
from guipy.backend._surface import _normalize_color
from guipy.backend._rect import Rect


def rect(surface, color, rect_arg, width=0, border_radius=0):
    """Draw a rectangle on a Surface.

    Args:
        surface: Target Surface
        color: RGB or RGBA tuple
        rect_arg: Rect object or (x, y, w, h) tuple
        width: Border width (0 = filled)
        border_radius: Corner radius for rounded rectangles
    """
    c = _normalize_color(color)
    pixels = surface._pixels
    ph, pw = pixels.shape[:2]

    if isinstance(rect_arg, Rect):
        rx, ry, rw, rh = rect_arg.x, rect_arg.y, rect_arg.w, rect_arg.h
    else:
        rx, ry, rw, rh = int(rect_arg[0]), int(rect_arg[1]), int(rect_arg[2]), int(rect_arg[3])

    if border_radius > 0:
        _rounded_rect(pixels, c, rx, ry, rw, rh, width, border_radius)
        return

    if width == 0:
        # Filled rectangle
        x0 = max(0, rx)
        y0 = max(0, ry)
        x1 = min(pw, rx + rw)
        y1 = min(ph, ry + rh)
        if x0 < x1 and y0 < y1:
            pixels[y0:y1, x0:x1] = c
    else:
        # Border only
        _hline(pixels, c, rx, rx + rw, ry, width)
        _hline(pixels, c, rx, rx + rw, ry + rh - width, width)
        _vline(pixels, c, rx, ry, ry + rh, width)
        _vline(pixels, c, rx + rw - width, ry, ry + rh, width)


def circle(surface, color, center, radius, width=0):
    """Draw a circle on a Surface."""
    c = _normalize_color(color)
    pixels = surface._pixels
    ph, pw = pixels.shape[:2]
    cx, cy = int(center[0]), int(center[1])
    r = int(radius)

    y_coords, x_coords = np.ogrid[:ph, :pw]
    dist_sq = (x_coords - cx) ** 2 + (y_coords - cy) ** 2

    if width == 0:
        mask = dist_sq <= r * r
    else:
        outer = dist_sq <= r * r
        inner = dist_sq <= (r - width) * (r - width)
        mask = outer & ~inner

    pixels[mask] = c


def line(surface, color, start, end, width=1):
    """Draw a line on a Surface using Bresenham-like rasterization."""
    c = _normalize_color(color)
    pixels = surface._pixels
    ph, pw = pixels.shape[:2]

    x0, y0 = int(start[0]), int(start[1])
    x1, y1 = int(end[0]), int(end[1])

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    half_w = max(0, width // 2)

    while True:
        # Draw a square brush of size `width` centered at (x0, y0)
        ylo = max(0, y0 - half_w)
        yhi = min(ph, y0 + half_w + 1)
        xlo = max(0, x0 - half_w)
        xhi = min(pw, x0 + half_w + 1)
        if ylo < yhi and xlo < xhi:
            pixels[ylo:yhi, xlo:xhi] = c

        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def _hline(pixels, color, x0, x1, y, thickness):
    ph, pw = pixels.shape[:2]
    x0c = max(0, int(x0))
    x1c = min(pw, int(x1))
    y0c = max(0, int(y))
    y1c = min(ph, int(y + thickness))
    if x0c < x1c and y0c < y1c:
        pixels[y0c:y1c, x0c:x1c] = color


def _vline(pixels, color, x, y0, y1, thickness):
    ph, pw = pixels.shape[:2]
    x0c = max(0, int(x))
    x1c = min(pw, int(x + thickness))
    y0c = max(0, int(y0))
    y1c = min(ph, int(y1))
    if x0c < x1c and y0c < y1c:
        pixels[y0c:y1c, x0c:x1c] = color


def _rounded_rect(pixels, color, rx, ry, rw, rh, width, border_radius):
    """Draw a rounded rectangle."""
    ph, pw = pixels.shape[:2]
    br = min(border_radius, rw // 2, rh // 2)

    y_coords, x_coords = np.ogrid[:ph, :pw]

    # Start with full rectangle mask
    in_rect = ((x_coords >= rx) & (x_coords < rx + rw) &
               (y_coords >= ry) & (y_coords < ry + rh))

    # Corners: check if pixel is inside the rounded corner
    corners = [
        (rx + br, ry + br, rx, ry, rx + br, ry + br),           # top-left
        (rx + rw - br, ry + br, rx + rw - br, ry, rx + rw, ry + br),  # top-right
        (rx + br, ry + rh - br, rx, ry + rh - br, rx + br, ry + rh),  # bottom-left
        (rx + rw - br, ry + rh - br, rx + rw - br, ry + rh - br, rx + rw, ry + rh),  # bottom-right
    ]

    corner_mask = np.zeros((ph, pw), dtype=bool)
    for cx, cy, x0, y0, x1, y1 in corners:
        in_corner_box = ((x_coords >= x0) & (x_coords < x1) &
                         (y_coords >= y0) & (y_coords < y1))
        dist_sq = (x_coords - cx) ** 2 + (y_coords - cy) ** 2
        outside_radius = dist_sq > br * br
        corner_mask |= (in_corner_box & outside_radius)

    filled_mask = in_rect & ~corner_mask

    if width == 0:
        pixels[filled_mask] = color
    else:
        # For bordered rounded rect, subtract the inner rounded rect
        inner_rx = rx + width
        inner_ry = ry + width
        inner_rw = rw - 2 * width
        inner_rh = rh - 2 * width
        inner_br = max(0, br - width)

        in_inner_rect = ((x_coords >= inner_rx) & (x_coords < inner_rx + inner_rw) &
                         (y_coords >= inner_ry) & (y_coords < inner_ry + inner_rh))

        inner_corner_mask = np.zeros((ph, pw), dtype=bool)
        inner_corners = [
            (inner_rx + inner_br, inner_ry + inner_br, inner_rx, inner_ry, inner_rx + inner_br, inner_ry + inner_br),
            (inner_rx + inner_rw - inner_br, inner_ry + inner_br, inner_rx + inner_rw - inner_br, inner_ry, inner_rx + inner_rw, inner_ry + inner_br),
            (inner_rx + inner_br, inner_ry + inner_rh - inner_br, inner_rx, inner_ry + inner_rh - inner_br, inner_rx + inner_br, inner_ry + inner_rh),
            (inner_rx + inner_rw - inner_br, inner_ry + inner_rh - inner_br, inner_rx + inner_rw - inner_br, inner_ry + inner_rh - inner_br, inner_rx + inner_rw, inner_ry + inner_rh),
        ]
        for cx, cy, x0, y0, x1, y1 in inner_corners:
            in_corner_box = ((x_coords >= x0) & (x_coords < x1) &
                             (y_coords >= y0) & (y_coords < y1))
            dist_sq = (x_coords - cx) ** 2 + (y_coords - cy) ** 2
            outside_radius = dist_sq > inner_br * inner_br
            inner_corner_mask |= (in_corner_box & outside_radius)

        inner_filled = in_inner_rect & ~inner_corner_mask
        border_mask = filled_mask & ~inner_filled
        pixels[border_mask] = color

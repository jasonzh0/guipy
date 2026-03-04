import os
import sys
import glob as globmod
import freetype
import numpy as np
from guipy.backend._surface import Surface
from guipy.backend import _gpu

# Cached font search paths per platform
_font_dirs = None
_font_cache = None


def _get_font_dirs():
    global _font_dirs
    if _font_dirs is not None:
        return _font_dirs

    dirs = []
    if sys.platform == "darwin":
        dirs = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
        ]
    elif sys.platform == "win32":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        dirs = [os.path.join(windir, "Fonts")]
    else:  # Linux / other
        dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
        ]
    _font_dirs = [d for d in dirs if os.path.isdir(d)]
    return _font_dirs


def _scan_fonts():
    """Scan system font directories and return dict of {lowercase_name: path}."""
    global _font_cache
    if _font_cache is not None:
        return _font_cache

    _font_cache = {}
    for d in _get_font_dirs():
        for ext in ("*.ttf", "*.otf", "*.TTF", "*.OTF"):
            for path in globmod.glob(os.path.join(d, "**", ext), recursive=True):
                name = os.path.splitext(os.path.basename(path))[0].lower()
                # Normalize: remove spaces, dashes
                normalized = name.replace(" ", "").replace("-", "").replace("_", "")
                _font_cache[normalized] = path
    return _font_cache


def get_fonts():
    """Return list of available system font names."""
    return list(_scan_fonts().keys())


def _find_font_path(name):
    """Find a font file path by name (case-insensitive, flexible matching)."""
    if name and os.path.isfile(name):
        return name

    fonts = _scan_fonts()
    if not name:
        return None

    normalized = name.lower().replace(" ", "").replace("-", "").replace("_", "")

    # Exact match
    if normalized in fonts:
        return fonts[normalized]

    # Partial match
    for key, path in fonts.items():
        if normalized in key:
            return path

    return None


def _get_fallback_font_path():
    """Get a fallback font path that supports Latin characters."""
    fonts = _scan_fonts()

    # Try exact matches for known good Latin fonts first
    preferred = [
        "arial", "helvetica", "helveticaneue", "dejavusans", "liberationsans",
        "roboto", "robotoregular", "ubuntu", "ubunturegular",
        "sfprodisplay", "sfprotext", "sfnsdisplay", "sfnstext",
        "verdana", "tahoma", "calibri", "segoeui",
    ]
    for name in preferred:
        if name in fonts:
            return fonts[name]

    # Try partial match but skip italic/bold/narrow variants
    for name in preferred:
        for key, path in fonts.items():
            if name in key and not any(v in key for v in ("italic", "bold", "narrow", "condensed", "light", "thin")):
                return path

    # Last resort: any font
    if fonts:
        return next(iter(fonts.values()))

    return None


class Font:
    """freetype-py based font replacement for pygame.font.Font."""

    def __init__(self, path, size):
        self._size = size
        if path:
            self._face = freetype.Face(path)
        else:
            fallback = _get_fallback_font_path()
            if fallback:
                self._face = freetype.Face(fallback)
            else:
                raise RuntimeError("No font found")
        # Render at physical resolution for HiDPI clarity
        s = _gpu.get_dpi_scale()
        self._face.set_char_size(int(size * s * 64))  # freetype uses 1/64 pixel units

    def render(self, text, antialias, color, background=None):
        """Render text to a Surface."""
        if not text:
            text = " "

        if len(color) == 4:
            r, g, b, a = color
        else:
            r, g, b = color
            a = 255

        # First pass: compute total width and collect glyph data
        glyphs = []
        total_width = 0
        for char in text:
            self._face.load_char(char, freetype.FT_LOAD_RENDER)
            glyph = self._face.glyph
            glyphs.append({
                'bitmap': np.array(glyph.bitmap.buffer, dtype=np.uint8).reshape(
                    glyph.bitmap.rows, glyph.bitmap.width
                ).copy() if glyph.bitmap.width > 0 and glyph.bitmap.rows > 0 else None,
                'width': glyph.bitmap.width,
                'rows': glyph.bitmap.rows,
                'left': glyph.bitmap_left,
                'top': glyph.bitmap_top,
                'advance': glyph.advance.x >> 6,
            })
            total_width += glyph.advance.x >> 6

        height = self._face.size.height >> 6  # physical pixels
        ascender = self._face.size.ascender >> 6  # physical pixels

        if total_width <= 0:
            total_width = 1
        if height <= 0:
            height = 1

        arr = np.zeros((height, total_width, 4), dtype=np.uint8)

        pen_x = 0
        for glyph_data in glyphs:
            bmp = glyph_data['bitmap']
            if bmp is not None:
                bx = pen_x + glyph_data['left']
                by = ascender - glyph_data['top']

                # Clip to array bounds
                src_y0 = max(0, -by)
                src_x0 = max(0, -bx)
                dst_y0 = max(0, by)
                dst_x0 = max(0, bx)
                src_y1 = min(glyph_data['rows'], height - by) if by >= 0 else min(glyph_data['rows'], height)
                src_x1 = min(glyph_data['width'], total_width - bx) if bx >= 0 else min(glyph_data['width'], total_width)

                if src_y0 < src_y1 and src_x0 < src_x1:
                    h_slice = slice(dst_y0, dst_y0 + src_y1 - src_y0)
                    w_slice = slice(dst_x0, dst_x0 + src_x1 - src_x0)
                    alpha_region = bmp[src_y0:src_y1, src_x0:src_x1]
                    arr[h_slice, w_slice, 0] = r
                    arr[h_slice, w_slice, 1] = g
                    arr[h_slice, w_slice, 2] = b
                    arr[h_slice, w_slice, 3] = (alpha_region.astype(np.uint16) * a // 255).astype(np.uint8)

            pen_x += glyph_data['advance']

        s = _gpu.get_dpi_scale()
        logical_size = (round(total_width / s), round(height / s))
        return Surface._from_array(arr, logical_size=logical_size)

    def size(self, text):
        """Return (width, height) of rendered text in logical pixels."""
        if not text:
            return (0, self.get_height())
        total_width = 0
        for char in text:
            self._face.load_char(char, freetype.FT_LOAD_RENDER)
            total_width += self._face.glyph.advance.x >> 6
        s = _gpu.get_dpi_scale()
        return (round(total_width / s), self.get_height())

    def get_height(self):
        s = _gpu.get_dpi_scale()
        return round(((self._face.size.ascender - self._face.size.descender) >> 6) / s)

    def get_linesize(self):
        s = _gpu.get_dpi_scale()
        return round((self._face.size.height >> 6) / s)


def SysFont(name, size, bold=False, italic=False):
    """Create a Font from a system font name."""
    path = _find_font_path(name)
    return Font(path, size)

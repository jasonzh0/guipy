import os
import sys
import glob as globmod
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from guipy.backend._surface import Surface

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
    """Pillow-based font replacement for pygame.font.Font."""

    def __init__(self, path, size):
        self._size = size
        if path:
            self._font = ImageFont.truetype(path, size)
        else:
            fallback = _get_fallback_font_path()
            if fallback:
                self._font = ImageFont.truetype(fallback, size)
            else:
                self._font = ImageFont.load_default()

    def render(self, text, antialias, color, background=None):
        """Render text to a Surface."""
        if not text:
            text = " "

        # Measure text
        bbox = self._font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = self.get_linesize()

        img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if len(color) == 4:
            fill = tuple(color)
        else:
            fill = (color[0], color[1], color[2], 255)

        draw.text((0, 0), text, font=self._font, fill=fill)

        arr = np.array(img, dtype=np.uint8)
        return Surface._from_array(arr)

    def size(self, text):
        """Return (width, height) of rendered text."""
        if not text:
            return (0, self.get_height())
        bbox = self._font.getbbox(text)
        return (bbox[2] - bbox[0], self.get_height())

    def get_height(self):
        bbox = self._font.getbbox("Ay")
        return bbox[3] - bbox[1]

    def get_linesize(self):
        metrics = self._font.getmetrics()
        return metrics[0] + metrics[1]


def SysFont(name, size, bold=False, italic=False):
    """Create a Font from a system font name."""
    path = _find_font_path(name)
    return Font(path, size)

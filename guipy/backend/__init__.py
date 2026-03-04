from guipy.backend._rect import Rect
from guipy.backend._surface import Surface
from guipy.backend._draw import rect as draw_rect, circle as draw_circle, line as draw_line
from guipy.backend import _draw as draw
from guipy.backend import _transform as transform
from guipy.backend._font import Font, SysFont, get_fonts
from guipy.backend._events import (
    Event, QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, MOUSEMOTION,
    K_RETURN, K_BACKSPACE,
)
from guipy.backend._renderer import Window


def init():
    """Initialize the backend (replaces pygame.init() + pygame.font.init())."""
    pass

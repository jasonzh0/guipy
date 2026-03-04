from guipy.backend import SysFont, get_fonts


def add_vector(a, b):
    """
    Adds two vectors (a+b)

    :param a:
    :param b:
    """
    return (a[0] + b[0], a[1] + b[1])


def sub_vector(a, b):
    """
    Subtracts two vectors (a-b)

    :param a:
    :param b:
    """
    return (a[0] - b[0], a[1] - b[1])


def translate(value, min1, max1, min2, max2):
    """
    Maps one value from one range to another range

    :param value: Value to be mapped
    :param min1: Min of range 1
    :param max1: Max of range 1
    :param min2: Min of range 2
    :param max2: Max of range 2
    """
    span1 = max1 - min1
    span2 = max2 - min2
    if span1 == 0:
        return 0
    if value == None:
        return None
    valueScaled = float(value - min1) / float(span1)
    return min2 + (valueScaled * span2)


def get_default_font():
    return SysFont(None, 20)


def clip(value, min1, max1):
    return max(min1, min(max1, value))


def float_format(n, exponent):
    return str(n) if exponent < 0 else str(int(n))


WHITE = (255, 255, 255)
"""
Preset for the color White
"""
RED = (255, 0, 0)
"""
Preset for the color Red
"""
GREEN = (0, 255, 0)
"""
Preset for the color Green
"""
BLUE = (0, 0, 255)
"""
Preset for the color Blue
"""
BLACK = (0, 0, 0)
"""
Preset for the color Black
"""
LIGHT_GREY = (230, 230, 230)
"""
Preset for the color Light Grey
"""
GREY = (200, 200, 200)
"""
Preset for the color Grey
"""
DARK_GREY = (100, 100, 100)
"""
Preset for the color Dark Grey
"""
ORANGE = (255, 100, 0)
"""
Preset for the color Orange
"""
TRANSPARENT = (0, 0, 0, 0)
"""
Preset for transparent (for alpha surfaces)
"""

import numpy as np
from PIL import Image
from guipy.backend._surface import Surface


def rotate(surface, angle):
    """Rotate a Surface by the given angle (degrees, counter-clockwise)."""
    arr = surface._pixels
    img = Image.fromarray(arr, "RGBA")
    rotated = img.rotate(angle, expand=True, resample=Image.BICUBIC)
    result = np.array(rotated, dtype=np.uint8)
    return Surface._from_array(result)

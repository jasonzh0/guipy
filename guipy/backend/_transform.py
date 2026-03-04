import numpy as np
from guipy.backend._surface import Surface


def rotate(surface, angle):
    """Rotate a Surface by the given angle (degrees, counter-clockwise).

    Uses numpy-based rotation as a simple fallback.
    """
    # Read pixels from GPU
    w, h = surface.get_size()
    data = surface._fbo.read(components=4)
    arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 4)
    arr = np.flipud(arr).copy()

    # Apply rotation using numpy (90-degree increments are exact, others approximate)
    k = int(round(angle / 90)) % 4
    if k == 0:
        rotated = arr
    elif k == 1:
        rotated = np.rot90(arr, 1)
    elif k == 2:
        rotated = np.rot90(arr, 2)
    elif k == 3:
        rotated = np.rot90(arr, 3)
    else:
        rotated = arr

    return Surface._from_array(rotated)

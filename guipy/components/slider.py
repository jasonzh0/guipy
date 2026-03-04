from guipy.backend import Surface, draw, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from guipy.components._component import Component
from guipy.utils import *


class Slider(Component):
    """
    Slider component for user interactions with drag and value setting
    """

    def __init__(self, width, height, thickness=2, radius=10, initial_val=0):
        """
        Initializes Slider Component

        :param width: width of slider
        :param height: height of slider
        :param thickness: thickness of slider line
        :param radius: radius of knob
        :param initial_val: initial value of the slider (0.0 - 1.0)
        """
        self.width = width
        self.height = height

        self.root = Surface((self.width, self.height)).convert_alpha()

        self.thickness = thickness
        self.val = initial_val
        self.r = radius

        self.grabbed = False

    def _draw(self):
        """
        Draws slider onto root
        """
        self.root.fill((0, 0, 0, 0))

        p1 = (self.r, self.height // 2)
        p2 = (self.width - self.r, self.height // 2)

        pVal = (self.r + self.val * (self.width - self.r * 2), self.height // 2)

        draw.line(self.root, (57, 189, 248), p1, pVal, self.thickness)
        draw.line(self.root, (200, 200, 200), pVal, p2, self.thickness)

        draw.circle(self.root, (0, 0, 0), pVal, self.r)
        draw.circle(self.root, (255, 255, 255), pVal, self.r - 3)

    def update(self, rel_mouse, events):
        """
        Updates slider logic

        :param rel_mouse: relative mouse position based on slider position
        :param events: Event list
        """
        on_click = False
        on_release = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                on_click = True
            if event.type == MOUSEBUTTONUP:
                on_release = True

        in_comp = self._collide(rel_mouse)

        if in_comp and on_click:
            self.grabbed = True

        if on_release:
            self.grabbed = False

        if self.grabbed:
            new_val = (rel_mouse[0] - self.r) / (self.width - 2 * self.r)

            self.val = clip(new_val, 0, 1)

        self._draw()

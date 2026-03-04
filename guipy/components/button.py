from guipy.backend import Surface, draw, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from guipy.components._component import Component
from guipy.utils import *


class Button(Component):
    """
    Button component
    """

    def __init__(self, width=None, height=None, font=None, text="Bruh"):
        """
        Button init

        :param width: button width in pixels, defaults to fit text
        :param height: button height in pixels, defaults to fit text
        :param font: Font object to use
        :param text: text to display on the button
        """
        if font == None:
            self.font = get_default_font()
        else:
            self.font = font

        min_w, min_h = self.font.size(text)
        if width == None:
            width = min_w + 6
        if height == None:
            height = min_h

        self.width = width
        self.height = height
        self.off_surf = Surface((self.width, self.height)).convert_alpha()
        self.on_surf = Surface((self.width, self.height)).convert_alpha()

        self.pressed = False

        self.set_text(text)

        self.cb = None

    def get_val(self):
        """
        Get current state

        :return: State as a boolean
        """
        return self.pressed

    def set_callback(self, cb):
        """
        Set the callback to be run when the button is released

        :param cb: Callback function

        :return: self
        """
        self.cb = cb
        return self

    def _draw(self):
        text_surf = self.font.render(self.text, True, BLACK)

        x, y = sub_vector((self.width, self.height), text_surf.get_size())
        pos = (x // 2, y // 2)

        self.off_surf.fill(TRANSPARENT)
        surf = self.off_surf
        draw.rect(surf, LIGHT_GREY, surf.get_rect())
        draw.rect(surf, DARK_GREY, surf.get_rect(), 1)
        surf.blit(text_surf, pos)

        self.on_surf.fill(TRANSPARENT)
        surf = self.on_surf
        draw.rect(surf, GREY, surf.get_rect())
        draw.rect(surf, DARK_GREY, surf.get_rect(), 1)
        surf.blit(text_surf, pos)

    def set_text(self, text):
        """
        Sets the text on the button and redraws the surface

        :param text:

        :return: self
        """
        self.text = text
        self._draw()
        return self

    def get_surf(self):
        """
        Get the button's surface

        :return: Surface
        """
        if self.pressed:
            return self.on_surf
        else:
            return self.off_surf

    def update(self, rel_mouse, events):
        """
        Update the button

        :param rel_mouse: Relative mouse position
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

        if on_click and in_comp:
            self.pressed = True

        if on_release and self.pressed:
            if in_comp and self.cb != None:
                self.cb(self)
            self.pressed = False

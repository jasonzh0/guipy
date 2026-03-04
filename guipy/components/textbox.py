from guipy.backend import Surface, draw, MOUSEBUTTONDOWN, KEYDOWN, K_RETURN, K_BACKSPACE
from guipy.components._component import Component
from guipy.utils import *


class Textbox(Component):
    """
    Textbox component for text input
    """

    def __init__(self, width, font=None, default_text="Type here..."):
        """
        Textbox init

        :param width: Width of the textbox (height is defined by font)
        :param font: Font object to be used
        :param default_text: Text to be shown when textbox is empty
        """
        if font == None:
            self.font = get_default_font()
        else:
            self.font = font

        self.width = width
        self.height = font.get_height() + 4
        self.root = Surface((self.width, self.height))

        self.text = ""
        self.default = default_text

        self.active = False
        self.func = None

    def set_func(self, func):
        """
        Set the callback to be run when the textbox is unselected, or enter is pressed

        :param cb: Callback function

        :return: self
        """
        self.func = func
        return self

    def _draw(self):
        """
        Draws the textbox
        """
        self.root.fill(WHITE)

        if self.text:
            text = self.font.render(self.text, True, BLACK)
        else:
            text = self.font.render(self.default, True, LIGHT_GREY)
        self.root.blit(text, (4, 1))

        if self.active:
            draw.rect(self.root, (0, 0, 0), self.root.get_rect(), width=2)
        else:
            draw.rect(self.root, (0, 0, 0), self.root.get_rect(), width=1)

    def update(self, rel_mouse, events):
        """
        Update the textbox

        :param rel_mouse: Relative mouse position
        :param events: Event list (used to read keypresses)
        """
        keydowns = []
        on_click = False
        for event in events:
            if event.type == KEYDOWN:
                keydowns.append(event)
            elif event.type == MOUSEBUTTONDOWN:
                on_click = True

        if on_click:
            in_comp = self._collide(rel_mouse)
            if self.active and not in_comp and self.func != None:
                self.func(self)
            self.active = in_comp

        if self.active:
            for event in keydowns:
                # check for backspace
                if event.key == K_RETURN:
                    if self.func != None:
                        self.func(self)
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:  # add character
                    self.text += event.unicode

        self._draw()

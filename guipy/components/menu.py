from guipy.backend import Surface, Rect, draw, MOUSEBUTTONDOWN
from guipy.components._component import Component
from guipy.utils import *


class Dropdown(Component):
    """
    Dropdown menu component
    """

    def __init__(self, width, font=None):
        """
        Dropdown init

        :param width: Menu width in pixels
        :param font: Font object to use
        """
        if font == None:
            self.font = get_default_font()
        else:
            self.font = font

        self.height = self.font.get_linesize()
        self.width = max(self.height, width)

        self.open = False
        self.value = None
        self.highlighted = -1
        self.options = []

        self.cb = None

        self._draw()

    def set_callback(self, cb):
        """
        Set the callback to be run when a new option is selected

        :param cb: Callback function

        :return: self
        """
        self.cb = cb
        return self

    def _draw(self):
        w = self.width - self.height
        n = len(self.options)
        if self.open:
            self.root = Surface(
                (self.width, self.height * (n + 1))
            ).convert_alpha()
            self.root.fill((200, 200, 200, 150))

            for i in range(n):
                y = (i + 1) * self.height
                if i == self.highlighted:
                    box = Rect(0, y, self.width, self.height)
                    draw.rect(self.root, (170, 170, 170, 150), box)
                text = self.font.render(str(self.options[i]), True, BLACK)
                self.root.blit(text, (3, y))
        else:
            self.root = Surface((self.width, self.height)).convert_alpha()

        box = Rect(0, 0, self.width, self.height)
        draw.rect(self.root, WHITE, box)
        if self.value != None:
            text = self.font.render(str(self.value), True, BLACK)
            self.root.blit(text, (3, 0))
        arrow = Rect(self.width - self.height, 0, self.height, self.height)
        draw.rect(self.root, GREY, arrow)
        y = self.height // 2
        x = y + w
        if self.open:
            draw.line(
                self.root,
                WHITE,
                (x, y - self.height // 6),
                (x - self.height // 3, y + self.height // 6),
                2,
            )
            draw.line(
                self.root,
                WHITE,
                (x, y - self.height // 6),
                (x + self.height // 3, y + self.height // 6),
                2,
            )
        else:
            draw.line(
                self.root,
                WHITE,
                (x, y + self.height // 6),
                (x - self.height // 3, y - self.height // 6),
                2,
            )
            draw.line(
                self.root,
                WHITE,
                (x, y + self.height // 6),
                (x + self.height // 3, y - self.height // 6),
                2,
            )
        draw.rect(self.root, BLACK, self.root.get_rect(), 1)

    def add(self, *options):
        """
        Add options to the menu

        :param *options: Any number of objects with a string representation

        :return: self
        """
        self.options += options
        return self

    def update(self, rel_mouse, events):
        """
        Update the dropdown menu

        :param rel_mouse: Relative mouse position
        :param events: Event list
        """
        on_click = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                on_click = True

        in_width = 0 <= rel_mouse[0] < self.width
        index = rel_mouse[1] // self.height - 1

        if self.open:
            if 0 <= index < len(self.options) and in_width:
                self.highlighted = index
                if on_click:
                    self.value = self.options[index]
                    if not self.cb == None:
                        self.cb(self)
            else:
                self.highlighted = -1
            if on_click:
                self.open = False
                self.highlighted = -1
            self._draw()

        else:
            if on_click and in_width and index == -1:
                self.open = True

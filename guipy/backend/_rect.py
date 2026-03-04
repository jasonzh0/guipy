class Rect:
    """Axis-aligned rectangle with position and size."""

    def __init__(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @property
    def left(self):
        return self.x

    @left.setter
    def left(self, value):
        self.x = int(value)

    @property
    def right(self):
        return self.x + self.w

    @right.setter
    def right(self, value):
        self.x = int(value) - self.w

    @property
    def top(self):
        return self.y

    @top.setter
    def top(self, value):
        self.y = int(value)

    @property
    def bottom(self):
        return self.y + self.h

    @bottom.setter
    def bottom(self, value):
        self.y = int(value) - self.h

    @property
    def width(self):
        return self.w

    @width.setter
    def width(self, value):
        self.w = int(value)

    @property
    def height(self):
        return self.h

    @height.setter
    def height(self, value):
        self.h = int(value)

    @property
    def size(self):
        return (self.w, self.h)

    @property
    def topleft(self):
        return (self.x, self.y)

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def inflate(self, dx, dy):
        return Rect(self.x - dx // 2, self.y - dy // 2, self.w + dx, self.h + dy)

    def collidepoint(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.w}, {self.h})"

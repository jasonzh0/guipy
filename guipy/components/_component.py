from guipy.backend import Surface


class Component:
    def __init__(self, width, height):
        """
        Component init. Should create a surface for the component
        """
        self.width = width
        self.height = height
        self.root = Surface((width, height))

    def _draw(self):
        """
        Draws the component
        """

    def get_surf(self):
        """
        Returns the surface of the component

        :return: Surface
        """
        return self.root

    def _collide(self, rel_mouse):
        """
        Helper method to detect collisions

        :param rel_mouse: Mouse position relative to the component

        :return: True if the mouse is inside the component
        """
        return 0 <= rel_mouse[0] < self.width and 0 <= rel_mouse[1] < self.height

    def update(self, rel_mouse, events):
        """
        Update the component. Gets the surface ready to be used

        :param rel_mouse: Mouse position relative to the component
        :param events: Event list
        """
        self._draw()

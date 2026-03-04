from guipy.utils import *


class GUIManager:
    """
    GUI Manager

    Main class that is required for all UI components to work.
    Add components to the manager, update, and then render them all onto a surface
    """

    def __init__(self):
        """
        Initializes the GUIManager
        """
        self.components = []

    def add(self, component, pos):
        """
        Add component to the manager

        :param component: UI component to be added to the GUIManager
        :param pos: Position of UI component on screen

        """
        self.components.append((component, pos))

    def update(self, mouse_pos, events, root):
        """
        Update all components in the manager, and render onto root

        :param mouse_pos: Mouse position used to update the components so components understand the relative location
        :param events: events used to update the components


        :param root: the surface these components should be drawn on
        """

        for component in self.components:
            rel_mouse = sub_vector(mouse_pos, component[1])
            component[0].update(rel_mouse, events)
            root.blit(component[0].get_surf(), component[1])

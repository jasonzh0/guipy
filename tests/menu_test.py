import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from guipy.backend import Window, Surface, SysFont, QUIT
from guipy.manager import GUIManager
from guipy.components.menu import *
from guipy.components.switch import *
from guipy.utils import *


def func(menu):
    print(menu.value)


winW = 1280
winH = 720

window = Window(winW, winH, "Menu Test")
root = Surface((winW, winH))

myFont = SysFont("Microsoft Sans Serif", 20)
man = GUIManager()
myMenu1 = Dropdown(200, myFont).add("A", "B", "C", "D").set_callback(func)
myMenu2 = Dropdown(200, myFont).add(1, 2, 3, 4).set_callback(func)


man.add(myMenu2, (150, 150))
man.add(myMenu1, (100, 100))


while not window.should_close():
    events = window.get_events()
    for event in events:
        if event.type == QUIT:
            window.destroy()
            sys.exit()

    root.fill(LIGHT_GREY)

    man.update(window.get_mouse_pos(), events, root)
    window.display(root)

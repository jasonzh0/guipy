import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from guipy.backend import Window, Surface, SysFont, QUIT
from guipy.manager import GUIManager
from guipy.components.textbox import Textbox

myFont = SysFont("Microsoft Sans Serif", 20)

winW = 1280
winH = 720

window = Window(winW, winH, "Textbox Test")
root = Surface((winW, winH))

man = GUIManager()
myTextbox1 = Textbox(width=400, font=myFont).set_func(lambda x: print("1: " + x.text))
myTextbox2 = Textbox(width=400, font=myFont).set_func(lambda x: print("2: " + x.text))
myTextbox3 = Textbox(width=400, font=myFont).set_func(lambda x: print("3: " + x.text))
myTextbox4 = Textbox(width=400, font=myFont).set_func(lambda x: print("4: " + x.text))

man.add(myTextbox1, (10, 25))
man.add(myTextbox2, (10, 75))
man.add(myTextbox3, (10, 125))
man.add(myTextbox4, (10, 175))
while not window.should_close():
    events = window.get_events()
    for event in events:
        if event.type == QUIT:
            window.destroy()
            sys.exit()
    root.fill((200, 200, 200))

    man.update(window.get_mouse_pos(), events, root)
    window.display(root)

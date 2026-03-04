import sys
import os
import inspect
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from guipy.backend import Window, Surface, QUIT
from guipy.manager import GUIManager
from guipy.components.plot import LivePlot
from guipy.utils import *

winW = 1280
winH = 720

window = Window(winW, winH, "LivePlot Test")
root = Surface((winW, winH))

myPlot1 = LivePlot(height=winH, width=winW)

man = GUIManager()
man.add(myPlot1, (0, 0))

start = time.time()
running = True
count = 0
while running and not window.should_close():
    events = window.get_events()
    for event in events:
        if event.type == QUIT:
            running = False

    root.fill(LIGHT_GREY)

    p = window.get_mouse_pos()

    myPlot1.add((time.time(), p[1]))

    man.update(p, [], root)

    window.display(root)
    count += 1

elapsed = time.time() - start
if elapsed > 0:
    print(f"Average fps: {count//elapsed}")
window.destroy()

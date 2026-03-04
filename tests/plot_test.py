import sys
import os
import inspect
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from guipy.backend import Window, Surface, QUIT
from guipy.manager import GUIManager
from guipy.components.plot import Plot
from guipy.utils import *

winW = 1280
winH = 720

window = Window(winW, winH, "Plot Test")
root = Surface((winW, winH))

myPlot1 = Plot(height=winH, width=winW, xlabel="X axis", ylabel="Y axis")

man = GUIManager()
man.add(myPlot1, (0, 0))

x = 1
y = 1

start = time.time()
count = 0
running = True
while running and not window.should_close():
    t = time.time()
    events = window.get_events()
    for event in events:
        if event.type == QUIT:
            running = False
    root.fill(LIGHT_GREY)

    p = window.get_mouse_pos()
    x = p[0] if p[0] else x
    y = p[1] if p[1] else y

    myPlot1.set_range((0, x), (0, y))

    myPlot1.plot(
        [(5, 35), (0, 40), (0, 60), (10, 70), (20, 60), (20, 40), (10, 30), (10, 10)]
    )
    myPlot1.plot(
        [(10, 60), (10, 40), (0, 30), (0, 10), (10, 0), (20, 10), (20, 30), (15, 35)]
    )

    man.update(window.get_mouse_pos(), events, root)
    window.display(root)
    count += 1

elapsed = time.time() - start
if elapsed > 0:
    print(f"Average fps: {count//elapsed}")
window.destroy()

# Guipy

![Python](https://img.shields.io/badge/python-3-blue.svg?v=1)
![Version](https://img.shields.io/pypi/v/guipylib.svg?v=1)
![License](https://img.shields.io/pypi/l/guipylib.svg?v=1)

GPU-accelerated UI library built by Casey (@caseyhackerman) and Jason

Uses moderngl + glfw for rendering and windowing, with Pillow for text.

## Installation

```
pip install guipylib
```

or with uv

```
uv add guipylib
```

## Components

### Button

<p align="center">
<img alt="Button" src="https://github.com/Zjjc123/guipy/blob/main/docs/imgs/button.gif" width="200" />
</p>

### Dropdown

<p align="center">
<img alt="Dropdown" src="https://github.com/Zjjc123/guipy/blob/main/docs/imgs/dropdown.gif" width="500" />
</p>

### Live Plot

<p align="center">
<img alt="Live Plot" src="https://github.com/Zjjc123/guipy/blob/main/docs/imgs/live_plot.gif" width="600" />
</p>

### Plot

<p align="center">
<img alt="Plot" src="https://github.com/Zjjc123/guipy/blob/main/docs/imgs/plot.gif" width="600" />
</p>

### Slider

<p align="center">
<img alt="Slider" src="https://github.com/Zjjc123/guipy/blob/main/docs/imgs/slider.gif" width="600" />
</p>

### Switch

<p align="center">
<img alt="Switch" src="https://github.com/Zjjc123/guipy/blob/main/docs/imgs/switch.gif" width="500" />
</p>

### Textbox

<p align="center">
<img alt="Textbox" src="https://github.com/Zjjc123/guipy/blob/main/docs/imgs/textbox.gif" width="600" />
</p>

## Example

```python
import sys
import colorsys

from guipy.backend import Window, Surface, draw, QUIT
from guipy.components.slider import Slider
from guipy.manager import GUIManager
from guipy.utils import *

winW = 1280
winH = 720

window = Window(winW, winH, "Slider Demo")
root = Surface((winW, winH))

man = GUIManager()

mySlider = Slider(height=50, width=500, thickness=5, radius=12, initial_val=0.4)
mySlider2 = Slider(height=50, width=500, thickness=5, radius=12, initial_val=0)
mySlider3 = Slider(height=50, width=500, thickness=5, radius=12, initial_val=0.5)
mySlider4 = Slider(height=50, width=500, thickness=5, radius=12, initial_val=0.5)

man.add(mySlider, (0, 25))
man.add(mySlider2, (0, 75))
man.add(mySlider3, (0, 125))
man.add(mySlider4, (0, 175))

while not window.should_close():
    events = window.get_events()
    for event in events:
        if event.type == QUIT:
            window.destroy()
            sys.exit()

    root.fill(DARK_GREY)

    color = tuple(
        i * 255
        for i in colorsys.hls_to_rgb(mySlider2.val, mySlider3.val, mySlider4.val)
    )
    center = (winW // 2, winH // 2)
    r = 10 + mySlider.val * 100
    draw.circle(root, color, center, r)
    draw.circle(root, BLACK, center, r, 3)

    man.update(window.get_mouse_pos(), events, root)
    window.display(root)
```

## Documentation

Check out some helpful guides and API references [here](https://zjjc123.github.io/guipy/)

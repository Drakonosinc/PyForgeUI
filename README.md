# PyForgeUI

[![Ask DeepWiki](https://img.shields.io/badge/Ask-DeepWiki-4B32C3?logo=read-the-docs&logoColor=white)](https://deepwiki.com/Drakonosinc/PyForgeUI)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**PyForgeUI** is a modular, zero-leak, game-ready GUI widget and container library built on top of **Pygame**. Designed around the `ElementsFactory` and `UIManager` patterns, it lets you build HUDs, RPG inventories, draggable windows, and multi-tab settings screens with cached font surfaces and clean event propagation.

---

## Features

- **18 Built-in Game Widgets & Containers**:
  - **Core Controls**: `Text`, `TextButton`, `PolygonButton`, `InputText`, `Image`, `ImageButton`
  - **Settings & Value Controls**: `CheckBox`, `ToggleSwitch`, `Slider`, `ProgressBar`, `RadioButton` / `RadioGroup`, `NumberSpinner`, `KeybindButton`
  - **Dropdowns & Scrolling**: `ComboBox` (`down`, `up`, `right`, `left`) & `ScrollBar` (`vertical` & `horizontal` with mouse wheel support)
  - **Containers & Layouts**: `Panel` (draggable & clippable), `StackLayout`, `GridLayout`, `TabContainer`, `Modal` / `DialogBox`
  - **Feedback**: Automatic floating `Tooltip` with hover delay
- **High Performance (Zero Surface Leaks)**: Text and label surfaces are pre-rendered and cached (`_update_surfaces()`), avoiding per-frame `font.render()` calls.
- **Z-Order & Modal Input Blocking**: `UIManager` handles top-down event consumption and blocks background clicks when a `Modal` is open.

---

## Installation

### From PyPI (once published)
```bash
pip install pyforgeui
```

### Local Editable Install (for development or local projects)
```bash
pip install -e .
```

---

## Quickstart

```python
import pygame
from pyforgeui import ElementsFactory

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

factory = ElementsFactory({"screen": screen})
ui = factory.create_UIManager()

panel = factory.create_Panel({
    "position": (200, 120, 400, 320),
    "title": "AUDIO & VIDEO SETTINGS",
    "draggable": True,
})

chk_vsync = factory.create_CheckBox({
    "position": (230, 175),
    "text": "Enable V-Sync",
    "checked": True,
    "tooltip": "Sync frame rate with monitor refresh rate",
})

sld_volume = factory.create_Slider({
    "position": (230, 245, 260, 14),
    "min_value": 0,
    "max_value": 100,
    "value": 80,
    "label": "Master Volume",
})

btn_apply = factory.create_TextButton({
    "position": (230, 310),
    "text": "Apply Changes",
    "command1": lambda: print("Volume:", sld_volume.get_value(), "VSync:", chk_vsync.get_value()),
})

for child in (chk_vsync, sld_volume, btn_apply):
    panel.add_child(child)

ui.add(panel)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            ui.events(event)

    screen.fill((20, 24, 32))
    ui.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

---

## Complete Interactive RPG Demo

Run the included multi-screen game UI showcase (`Main Menu`, `Hero Loadout & HUD`, and `System Configuration`):

```bash
python demo_game_ui.py
```

---

## Running Tests & Building the Package

Run the automated test suite:
```bash
python -m unittest discover -s tests
```

Build `.whl` and `.tar.gz` distributions for PyPI:
```bash
pip install build twine
python -m build
twine upload dist/*
```

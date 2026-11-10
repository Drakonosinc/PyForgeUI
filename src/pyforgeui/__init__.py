"""PyForgeUI - Modular and Scalable GUI Library for Pygame."""

__version__ = "1.0.0"
__author__ = "Drakonosinc"

from .Elements_Factory import ElementsFactory
from .UI_Manager import UIManager
from .Elements import (
    Text,
    TextButton,
    PolygonButton,
    InputText,
    Input_text,
    ScrollBar,
    ComboBox,
    ComboBoxDown,
    ComboBoxUp,
    ComboBoxRight,
    ComboBoxLeft,
    CheckBox,
    ToggleSwitch,
    Slider,
    ProgressBar,
    Image,
    ImageButton,
    RadioButton,
    RadioGroup,
    NumberSpinner,
    KeybindButton,
    Tooltip,
)
from .Containers import (
    Panel,
    StackLayout,
    GridLayout,
    Modal,
    DialogBox,
    TabContainer,
)
from .Behavior import (
    MouseCollision,
    PressedButton,
    ElementBehavior,
)

__all__ = [
    "__version__",
    "ElementsFactory",
    "UIManager",
    "Text",
    "TextButton",
    "PolygonButton",
    "InputText",
    "Input_text",
    "ScrollBar",
    "ComboBox",
    "ComboBoxDown",
    "ComboBoxUp",
    "ComboBoxRight",
    "ComboBoxLeft",
    "CheckBox",
    "ToggleSwitch",
    "Slider",
    "ProgressBar",
    "Image",
    "ImageButton",
    "RadioButton",
    "RadioGroup",
    "NumberSpinner",
    "KeybindButton",
    "Tooltip",
    "Panel",
    "StackLayout",
    "GridLayout",
    "Modal",
    "DialogBox",
    "TabContainer",
    "MouseCollision",
    "PressedButton",
    "ElementBehavior",
]

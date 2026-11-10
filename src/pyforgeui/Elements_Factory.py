import pygame
try:
    from .Elements import *
    from .Containers import *
    from .UI_Manager import UIManager
except ImportError:
    from Elements import *
    from Containers import *
    from UI_Manager import UIManager


class ElementsFactory:
    """Centralized factory for creating themed PyForgeUI widgets and containers."""

    def __init__(self, config: dict) -> None:
        self.screen = config["screen"]
        self.window = config.get("window", None)
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.color = config.get("color", (255, 255, 255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.color_back = config.get("color_back", (255, 255, 255))
        self.sound_hover = config.get("sound_hover", None)
        self.sound_touch = config.get("sound_touch", None)

    def _base_config(self, config: dict, include_font: bool = True, include_sounds: bool = True) -> dict:
        base = {
            "screen": self.screen,
            "window": self.window,
            "color": self.color,
            "hover_color": self.hover_color,
        }
        if include_font:
            base["font"] = self.font
        if include_sounds:
            base["sound_hover"] = self.sound_hover
            base["sound_touch"] = self.sound_touch
        base.update(config)
        return base

    def create_Text(self, config: dict) -> Text:
        return Text(self._base_config(config, include_font=True, include_sounds=False))

    def create_TextButton(self, config: dict) -> TextButton:
        return TextButton(self._base_config(config))

    def create_PolygonButton(self, config: dict) -> PolygonButton:
        return PolygonButton(self._base_config(config, include_font=False))

    def create_InputText(self, config: dict) -> InputText:
        cfg = {"color_back": self.color_back, **config}
        return InputText(self._base_config(cfg))

    def create_ScrollBar(self, config: dict) -> ScrollBar:
        return ScrollBar(self._base_config(config, include_font=False))

    def create_ComboBox(self, config: dict) -> ComboBox:
        type_key = (config.get("type_dropdown", "down")).lower()
        mapping = {
            "down": ComboBoxDown,
            "up": ComboBoxUp,
            "right": ComboBoxRight,
            "left": ComboBoxLeft,
        }
        cls = mapping.get(type_key, ComboBoxDown)
        return cls(self._base_config(config))

    def create_CheckBox(self, config: dict) -> CheckBox:
        return CheckBox(self._base_config(config))

    def create_ToggleSwitch(self, config: dict) -> ToggleSwitch:
        return ToggleSwitch(self._base_config(config))

    def create_Slider(self, config: dict) -> Slider:
        return Slider(self._base_config(config))

    def create_ProgressBar(self, config: dict) -> ProgressBar:
        return ProgressBar(self._base_config(config, include_sounds=False))

    def create_Image(self, config: dict) -> Image:
        return Image(self._base_config(config, include_font=False, include_sounds=False))

    def create_ImageButton(self, config: dict) -> ImageButton:
        return ImageButton(self._base_config(config, include_font=False))

    def create_RadioButton(self, config: dict) -> RadioButton:
        return RadioButton(self._base_config(config))

    def create_RadioGroup(self, config: dict | None = None) -> RadioGroup:
        return RadioGroup(config)

    def create_NumberSpinner(self, config: dict) -> NumberSpinner:
        return NumberSpinner(self._base_config(config))

    def create_KeybindButton(self, config: dict) -> KeybindButton:
        return KeybindButton(self._base_config(config))

    def create_Tooltip(self, config: dict) -> Tooltip:
        return Tooltip(self._base_config(config, include_sounds=False))

    def create_Panel(self, config: dict) -> Panel:
        return Panel(self._base_config(config))

    def create_StackLayout(self, config: dict) -> StackLayout:
        return StackLayout(self._base_config(config, include_font=False, include_sounds=False))

    def create_GridLayout(self, config: dict) -> GridLayout:
        return GridLayout(self._base_config(config, include_font=False, include_sounds=False))

    def create_Modal(self, config: dict) -> Modal:
        return Modal(self._base_config(config))

    def create_DialogBox(self, config: dict) -> DialogBox:
        return DialogBox(self._base_config(config))

    def create_TabContainer(self, config: dict) -> TabContainer:
        return TabContainer(self._base_config(config))

    def create_UIManager(self, config: dict | None = None) -> UIManager:
        cfg = {"screen": self.screen, "window": self.window, "font": self.font, **(config or {})}
        return UIManager(cfg)

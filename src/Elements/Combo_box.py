from ..Behavior.Element_behavior import *
from ..Elements.Text_button import TextButton
class ComboBox(TextButton):
    def __init__(self, config: dict):
        super().__init__(config)
        self.type_dropdown = self.icon_dropdown(config.get("type_dropdown", "down"))
        self.dropdown = config.get("size", (self.font.size(self.text)[0]+self.font.size(self.type_dropdown)[0], 200))
        self.hover_dropdown=config.get("hover_dropdown",(135,206,235))
        self.is_dropdown_open = False
        self.selected_index = None
        self.options = []
        self.option_buttons = []
        self.button_dropdown = TextButton({
            "screen": self.screen,
            "font": self.font,
            "color": self.color,
            "hover_color": self.hover_dropdown,
            "position": (self.position[0]+self.font.size(self.text)[0], int(self.position[1])),
            "text": self.type_dropdown,
            "sound_hover": self.sound_hover,
            "sound_touch": self.sound_touch,
            "command1": lambda: setattr(self, 'is_dropdown_open', not self.is_dropdown_open)})
        self.rect = {"button": pygame.Rect(*self.position, *self.font.size(self.text)),
                    "dropdown": self.button_dropdown}

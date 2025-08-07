from ..Behavior.Element_behavior import *
from ..Elements.Text_button import TextButton
class ComboBox(TextButton):
    def __init__(self, config: dict):
        super().__init__(config)
        self.type_dropdown = self.icon_dropdown(config.get("type_dropdown", "down"))
        self.dropdown = config.get("size", (self.font.size(self.text)[0]+self.font.size(self.type_dropdown)[0], 200))
        self.hover_dropdown=config.get("hover_dropdown",(135,206,235))
        self.replace_text = config.get("replace_text", False)
        self.anim_height_dropdown = 0
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
    def icon_dropdown(self,type_dropdown):
        match type_dropdown:
            case "down":return " V"
            case "up":return " Λ"
            case "right":return " >"
            case "left":return " <"
    def get_rect_dropdown(self):
        match self.type_dropdown:
            case " V":
                self.anim_height_dropdown += 1 if self.anim_height_dropdown<=self.dropdown[1] else 0
                return pygame.Rect(self.position[0], self.position[1] + self.font.get_height(), self.dropdown[0], self.anim_height_dropdown)
            case " Λ":return None
            case " >":return None
            case " <":return None
    def draw(self):
        self.screen.blit(self.font.render(self.text, True,self.color),(self.position))
        self.button_dropdown.draw()
        if self.is_dropdown_open:self.draw_rect_dropdown()
        else:
            self.anim_height_dropdown = 0
            self.button_dropdown.change_item({"color": self.color})
        if self.detect_mouse:self.mouse_collision(self.rect["button"],pygame.mouse.get_pos(),self.draw_hover_effect)
        if self.pressed:self.pressed_button(self.rect["button"],pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self):return self.screen.blit(self.font.render(f"{self.text}{self.type_dropdown}", True,self.hover_color), (self.position))
    def draw_rect_dropdown(self):
        self.button_dropdown.change_item({"color": self.hover_dropdown})
        self.dropdown_rect = self.get_rect_dropdown()
        pygame.draw.rect(self.screen, self.hover_dropdown, self.dropdown_rect)
        for button in self.option_buttons:button.draw()
        if hasattr(self, 'scroll'):self.scroll.draw()
    def charge_elements(self, options: list[str]):
        self.options = options
        for i, option in enumerate(options):
            button = TextButton({
                "screen": self.screen,
                "font": self.font,
                "color": self.color,
                "hover_color": self.hover_color,
                "position": (self.position[0], self.position[1] + self.font.get_height() + i * (self.font.get_height() + 5)),
                "text": option,
                "command1": lambda idx=i: self.select_option(idx) if self.replace_text else None})
            self.option_buttons.append(button)
            self.rect[f"option_{i}"] = button
        if self.option_buttons[-1].rect[1]>self.dropdown[1]:
            self.scroll = ScrollBar({
                "screen": self.screen,
                "position": (self.position[0] + self.font.size(self.text)[0]+self.font.size(self.type_dropdown)[0], self.position[1] + self.font.get_height(), 20, self.dropdown[1]),
                "thumb_height": 20,
                "color": (200, 200, 200),
                "color_bar": (135, 206, 235),
                "hover_color": (255, 199, 51)})
            self.rect["rect"] = self.scroll.rect
            self.scroll.update_elements(self.option_buttons)
        if (options and not self.text) and self.replace_text:
            self.text = options[0]
            self.selected_index = 0
    def select_option(self, index):
        if 0 <= index < len(self.options):
            self.text = self.options[index]
            self.selected_index = index
            self.is_dropdown_open = False
    def events(self, event):
        if hasattr(self, 'scroll'):self.scroll.events(event)
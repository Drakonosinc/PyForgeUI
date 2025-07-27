from ..Behavior.Element_behavior import *
from ..Elements.Text_button import TextButton
class ComboBox(TextButton):
    def __init__(self, config: dict):
        super().__init__(config)
        self.dropdown = config.get("size", (self.font.size(self.text)[0], 200))
        self.type_dropdown = self.icon_dropdown(config.get("type_dropdown", "down"))
        self.hover_dropdown=config.get("hover_dropdown",(135,206,235))
        self.is_dropdown_open = False
        self.selected_index = None
        self.options = []
        self.dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.button_dropdown = TextButton({
            "screen": self.screen,
            "font": self.font,
            "color": self.color,
            "hover_color": self.hover_dropdown,
            "position": (self.position[0]+self.font.size(self.text)[0], int(self.position[1])),
            "text": self.type_dropdown,
            "sound_hover": self.sound_hover,
            "sound_touch": self.sound_touch})
        self.rect = {"button": pygame.Rect(*self.position, *self.font.size(self.text)),
                    "dropdown": self.button_dropdown}
    def icon_dropdown(self,type_dropdown):
        match type_dropdown:
            case "down":return " V"
            case "up":return " Λ"
            case "right":return " >"
            case "left":return " <"
    def events(self, event):pass
    def draw(self):
        self.screen.blit(self.font.render(self.text, True,self.color),(self.position))
        self.button_dropdown.draw()
        if self.detect_mouse:self.mouse_collision(self.rect["button"],pygame.mouse.get_pos(),self.draw_hover_effect)
        if self.pressed:pass
    def draw_hover_effect(self):return self.screen.blit(self.font.render(f"{self.text}{self.type_dropdown}", True,self.hover_color), (self.position))
    def draw_pressed_effect(self):pass
    def charge_elements(self, options: list[str]):
        self.options = options
        self.option_buttons = []
        for i, option in enumerate(options):
            x = self.position[0]
            y = self.position[1] + self.font.get_height() + i * (self.font.get_height() + 5)
            position = (x, y)
            button = TextButton({
                "screen": self.screen,
                "font": self.font,
                "color": self.color,
                "hover_color": self.hover_color,
                "position": position,
                "text": option,
                "command1": lambda idx=i: self.select_option(idx)})
            self.option_buttons.append(button)
        if options and not self.text:
            self.text = options[0]
            self.selected_index = 0
    def select_option(self, index):
        if 0 <= index < len(self.options):
            self.text = self.options[index]
            self.selected_index = index
            self.is_dropdown_open = False
    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect["dropdown"].collidepoint(event.pos):self.is_dropdown_open = not self.is_dropdown_open
            elif self.is_dropdown_open and not self.dropdown_rect.collidepoint(event.pos):self.is_dropdown_open = False
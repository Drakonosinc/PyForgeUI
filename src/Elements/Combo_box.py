from ..Elements_Factory import ElementsFactory
from ..Behavior.Element_behavior import *
from ..Elements.Text_button import TextButton
class ComboBox(TextButton):
    def __init__(self, config: dict):
        super().__init__(config)
        self.type_dropdown = self.icon_dropdown(config.get("type_dropdown", "down"))
        self.dropdown = config.get("size", [self.font.size(self.text)[0]+self.font.size(self.type_dropdown)[0], 200])
        self.hover_dropdown=config.get("hover_dropdown",(135,206,235))
        self.replace_text = config.get("replace_text", False)
        self.adapt_dropdown = config.get("adapt_dropdown", True)
        self.anim_height_dropdown = 0
        self.is_dropdown_open = False
        self.selected_index = None
        self.options = []
        self.option_buttons = {}
        self.factory = ElementsFactory({
            "screen": self.screen,
            "font": self.font,
            "color": self.color,
            "hover_color": self.hover_color,
            "sound_hover": self.sound_hover,
            "sound_touch": self.sound_touch})
        self.button_dropdown = self.factory.create_TextButton({
            "position": (self.position[0]+self.font.size(self.text)[0], int(self.position[1])),
            "text": self.type_dropdown,
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
        def anim_height():pass
        match self.type_dropdown:
            case " V":
                self.anim_height_dropdown += 1 if self.anim_height_dropdown<self.dropdown[1] else 0
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
        pygame.draw.rect(self.screen, self.color, self.dropdown_rect, 2)
        for button in self.option_buttons.values():
            if button.rect.bottom<=self.dropdown_rect.bottom and button.rect.top>=self.dropdown_rect.top:button.draw()
        if hasattr(self, 'scroll'):
            self.scroll.rect["rect"].height = self.dropdown_rect.height
            self.scroll.draw()
    def charge_elements(self, options: dict, scroll: bool = True):
        for i, (option,action) in enumerate(options.items()):
            button = self.factory.create_TextButton({
                "text": option,
                "position": (self.position[0], self.position[1] + self.font.get_height() + i * (self.font.get_height() + 5)),
                "command1": lambda idx=i: self.select_option(idx) if self.replace_text else None,
                "command2": action if callable(action) else None})
            self._repeat_charge(f"elements_{i}",option,button)
            self.options.append(option)
            if len(self.options[i]) >= len(option):self.dropdown[0] = self.font.size(option)[0] + 5
        if self.adapt_dropdown:self.dropdown[1] = len(self.option_buttons) * (self.font.get_height() + 5)
        if scroll:self._create_scroll()
        if (options and not self.text) and self.replace_text:
            self.text = self.options[0]
            self.selected_index = 0
    def charge_buttons(self,buttons: list, scroll: bool = True):
        for i, button in enumerate(buttons):
            if not self.option_buttons:button.position = (self.position[0], self.position[1] + self.font.get_height() + i * (self.font.get_height() + 5))
            else:button.position = (self.position[0], self.option_buttons[list(self.option_buttons.keys())[-1]].rect.bottom + 5)
            self._repeat_charge(f"buttons_{i}",button.text,button)
            if len(buttons[i].text) >= len(button.text):self.dropdown[0] = self.font.size(button.text)[0] + 5
        self.dropdown[1] = len(self.option_buttons) * (self.font.get_height() + 5)
        if scroll:self._create_scroll()
    def _repeat_charge(self,i,option,button):
        self.option_buttons[option] = button
        self.rect[i] = button
    def _create_scroll(self):
        self.scroll = self.factory.create_ScrollBar({
            "position": (self.position[0] + self.dropdown[0], self.position[1] + self.font.get_height(), 20, self.dropdown[1]),
            "thumb_height": 20,
            "color_bar": (135, 206, 235)})
        self.rect["scroll"] = self.scroll.rect
        self.scroll.update_elements([*self.option_buttons.values()])
    def select_option(self, index):
        if 0 <= index < len(self.options):
            self.text = self.options[index]
            self.selected_index = index
            self.is_dropdown_open = False
    def events(self, event):
        if hasattr(self, 'scroll'):self.scroll.events(event)
    def return_buttons(self, button:str):return self.option_buttons[button]
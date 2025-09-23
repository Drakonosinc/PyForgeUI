from ..Elements_Factory import ElementsFactory
from ..Behavior.Element_behavior import *
from ..Elements.Text_button import TextButton
class ComboBox(TextButton):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.type_dropdown: str = self.icon_dropdown((config.get("type_dropdown", "down")).lower())
        self.dropdown: list[int] = config.get("size", [self.font.size(self.text)[0]+self.font.size(self.type_dropdown)[0], 100])
        self.hover_dropdown: tuple[int, int, int] = config.get("hover_dropdown",(135,206,235))
        self.replace_text: bool = config.get("replace_text", False)
        self.adapt_dropdown: bool = config.get("adapt_dropdown", True)
        self.draw_scroll: bool = config.get("draw_scroll", True)
        self.command_dropdown = config.get("command_dropdown", None)
        self.anim_height_dropdown: int = 0
        self.is_dropdown_open: bool = False
        self.options: list[str] = []
        self.option_buttons: dict = {}
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
            "command1": lambda: setattr(self, 'is_dropdown_open', not self.is_dropdown_open),
            "command2": self.command_dropdown if callable(self.command_dropdown) else None})
        self.rect: dict[str, object] = {"button": pygame.Rect(*self.position, *self.font.size(self.text)),
                    "dropdown": self.button_dropdown}
    def icon_dropdown(self,type_dropdown: str) -> str:
        match type_dropdown:
            case "down":return " V"
            case "up":return " ^"
            case "right":return " >"
            case "left":return " <"
    def _get_rect_dropdown(self)  -> pygame.Rect:
        def anim_motion(index:int):self.anim_height_dropdown += 1 if self.anim_height_dropdown<self.dropdown[index] else 0
        match self.type_dropdown:
            case " V":
                anim_motion(1)
                return pygame.Rect(self.position[0], self.position[1] + self.font.get_height(), self.dropdown[0], self.anim_height_dropdown)
            case " ^":
                anim_motion(1)
                return pygame.Rect(self.position[0], self.position[1] - self.anim_height_dropdown, self.dropdown[0], self.anim_height_dropdown)
            case " >":
                anim_motion(0)
                return pygame.Rect(self.position[0] + (self.font.size(self.text)[0] + self.font.size(self.type_dropdown)[0]), self.position[1] + (self.font.get_height()/2), self.anim_height_dropdown, self.dropdown[1])
            case " <":
                anim_motion(0)
                return pygame.Rect(self.position[0] - self.anim_height_dropdown, self.position[1] + (self.font.get_height()/2), self.anim_height_dropdown, self.dropdown[1])
    def draw(self) -> None:
        self.screen.blit(self.font.render(self.text, True,self.color),(self.position))
        self.button_dropdown.draw()
        if self.is_dropdown_open:self.draw_rect_dropdown()
        else:
            self.anim_height_dropdown = 0
            self.button_dropdown.change_item({"color": self.color})
        if self.detect_mouse:self.mouse_collision(self.rect["button"],pygame.mouse.get_pos(),self.draw_hover_effect)
        if self.pressed:self.pressed_button(self.rect["button"],pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self) -> pygame.Rect:return self.screen.blit(self.font.render(f"{self.text}{self.type_dropdown}", True,self.hover_color), (self.position))
    def draw_rect_dropdown(self) -> None:
        self.button_dropdown.change_item({"color": self.hover_dropdown})
        self.dropdown_rect = self._get_rect_dropdown()
        pygame.draw.rect(self.screen, self.hover_dropdown, self.dropdown_rect)
        pygame.draw.rect(self.screen, self.color, self.dropdown_rect, 2)
        if self.adapt_dropdown and self.option_buttons:self._adapt_size_dropdown()
        if self.draw_scroll and self.option_buttons and self.type_dropdown in (" V", " ^"):self._create_scroll()
        for button in self.option_buttons.values():self._draw_option_buttons(button)
        if hasattr(self, 'scroll'):self._draw_scroll()
    def _draw_option_buttons(self,button: object) -> None:
        if (button.rect.bottom<=self.dropdown_rect.bottom and button.rect.top>=self.dropdown_rect.top) and (self.type_dropdown in (" V", " ^")):button.draw()
        elif (button.rect.right<=self.dropdown_rect.right and button.rect.left>=self.dropdown_rect.left) and (self.type_dropdown in (" <", " >")):button.draw()
    def _adapt_size_dropdown(self) -> None:
        if self.type_dropdown in (" V", " ^"):self.dropdown[1], self.adapt_dropdown = (len(self.option_buttons) * (self.font.get_height() + 5)), False
        elif self.type_dropdown == " >":self.dropdown[0], self.dropdown[1], self.adapt_dropdown = (self.option_buttons[list(self.option_buttons.keys())[-1]].rect.right - self.option_buttons[list(self.option_buttons.keys())[0]].rect.left) + 10, (self.font.get_height() + 5), False
        elif self.type_dropdown == " <":self.dropdown[0], self.dropdown[1], self.adapt_dropdown = (self.option_buttons[list(self.option_buttons.keys())[0]].rect.right - self.option_buttons[list(self.option_buttons.keys())[-1]].rect.left) + 10, (self.font.get_height() + 5), False
    def _draw_scroll(self) -> None:
        if self.type_dropdown == " V":self.scroll.rect["rect"].height = self.dropdown_rect.height
        elif self.type_dropdown == " ^":
            if self.dropdown_rect.height != self.dropdown[1]:self.scroll.rect["rect"].y = self.scroll.rect["thumb"].y = self.dropdown_rect.y
            self.scroll.rect["rect"].height = self.dropdown_rect.height
        self.scroll.draw()
    def charge_elements(self, options: dict) -> None:
        for i, (option,action) in enumerate(options.items()):
            button = self.factory.create_TextButton({
                "text": option,
                "position": self._check_buttons_position(i, option),
                "command1": lambda idx=i: self._select_option(idx) if self.replace_text else None,
                "command2": action if callable(action) else None})
            self._repeat_charge(f"elements_{i}", option, button, i)
    def charge_buttons(self, buttons: list, first: bool = False) -> None:
        for i, button in enumerate(buttons):
            button.position = self._check_buttons_position(i, button.text,first)
            if hasattr(button, 'rect'):
                if isinstance(button.rect, pygame.Rect):button.rect.topleft = button.position
                elif isinstance(button.rect, dict) and "button" in button.rect:button.rect["button"].topleft = button.position
            self._repeat_charge(f"buttons_{i}",button.text,button,i)
    def _repeat_charge(self,key,text,button,i) -> None:
        self.option_buttons[text] = button
        self.rect[key] = button
        self.options.append(text)
        if len(text) >= len(self.options[i]) and (self.type_dropdown in (" V", " ^")):self.dropdown[0] = self.font.size(button.text)[0] + 5
    def _check_buttons_position(self,i: int, text: str = "", first: bool = False) -> tuple[int, int]:
        last_rect = self.option_buttons[list(self.option_buttons.keys())[-1]].rect if self.option_buttons else None
        if self.type_dropdown == " V":return (self.position[0], (self.position[1] + self.font.get_height() + i * (self.font.get_height() + 5)) if not last_rect or first else (last_rect.bottom + 5))
        elif self.type_dropdown == " ^":return (self.position[0], (self.position[1] - self.font.get_height() + i * (self.font.get_height() + 5)) if not last_rect or first else (last_rect.top - self.font.get_height()))
        elif self.type_dropdown == " >":return ((self.position[0] + ((self.font.size(self.text)[0] + self.font.size(self.type_dropdown)[0]) + 5)) if not last_rect or first else (last_rect.right + 5), self.position[1] + (self.font.get_height()/2))
        elif self.type_dropdown == " <":return ((self.position[0] - (self.font.size(text)[0] + 5)) if not last_rect or first else (last_rect.left - (self.font.size(text)[0] + 5)), self.position[1] + (self.font.get_height()/2))
    def _create_scroll(self) -> None:
        self.scroll = self.factory.create_ScrollBar({
            "position": (self.position[0] + self.dropdown[0], self.position[1] + self.font.get_height(), 20, self.dropdown[1]),
            "thumb_height": 20,
            "color_bar": (135, 206, 235)})
        self.rect["scroll"] = self.scroll.rect
        self.scroll.update_elements([*self.option_buttons.values()])
        self.draw_scroll = False
    def _select_option(self, index: int) -> None:
        if 0 <= index < len(self.options):
            self.text = self.options[index]
            self.option_buttons[self.options[index]].position = self.position
            self.option_buttons[self.options[index]].rect = pygame.Rect(*self.position, *self.font.size(self.text))
            self.button_dropdown.change_item({"position": (self.position[0] + self.font.size(self.text)[0], int(self.position[1]))})
            self.button_dropdown.rect = pygame.Rect(self.button_dropdown.position, self.font.size(self.button_dropdown.text))
            self.is_dropdown_open = False
        self.charge_buttons([button for button in self.option_buttons.values() if button.text != self.text],True)
        if self.type_dropdown in (" V", " ^"):self._create_scroll()
    def events(self, event):
        if hasattr(self, 'scroll'):self.scroll.events(event)
    def return_buttons(self, button:str):return self.option_buttons[button]
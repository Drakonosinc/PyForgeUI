import pygame
from ..Behavior.Element_behavior import ElementBehavior
from .Text import Text
class TextButton(Text,ElementBehavior):
    def __init__(self,config:dict):
        Text.__init__(self, config)
        ElementBehavior.__init__(self, config)
    def draw(self):
        super().draw()
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),self.get_mouse_pos())
    def change_item(self,config:dict):
        super().change_item(config)
        self.pressed=config.get("pressed",self.pressed)

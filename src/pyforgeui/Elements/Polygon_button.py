import pygame
from ..Behavior.Element_behavior import ElementBehavior
class PolygonButton(ElementBehavior):
    def __init__(self,config:dict):
        super().__init__(config)
        self.hover_position = config.get("hover_position",self.position)
        self.color = config.get("color", (255, 255, 255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.rect = pygame.draw.polygon(self.screen, self.color, self.position).copy()
    def draw(self):
        pygame.draw.polygon(self.screen, self.color, self.position)
        if self.detect_mouse:self.mouse_collision(self.rect,self.get_mouse_pos())
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),self.get_mouse_pos())
    def draw_hover_effect(self):return pygame.draw.polygon(self.screen, self.hover_color, self.hover_position)
    def change_item(self,config:dict):
        self.color=config.get("color",self.color)
        self.detect_mouse=config.get("detect_mouse",self.detect_mouse)
        self.pressed=config.get("pressed",self.pressed)

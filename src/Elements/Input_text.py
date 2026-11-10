import pygame
from pygame.locals import *
from ..Behavior.Element_behavior import ElementBehavior
class InputText(ElementBehavior):
    def __init__(self,config:dict):
        super().__init__(config)
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text","")
        self.color=config.get("color",(0,0,0))
        self.color_back=config.get("color_back",(255,255,255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.pressed_color=config.get("pressed_color",(135,206,235))
        self.border_color=config.get("border_color",(127,127,127))
        self.border=config.get("border",2)
        self.rect = pygame.Rect(*self.position)
        self._text_surface = self.font.render(self.text, True, self.color)
    def change_text(self,event):
        if self.states["active"] and event.type==KEYDOWN:
            if event.key == K_BACKSPACE:self.text=self.text[:-1]
            else:self.text+=event.unicode
            self._text_surface = self.font.render(self.text, True, self.color)
    def events(self, event):
        self.change_text(event)
    def draw(self):
        pygame.draw.rect(self.screen,self.color_back,self.rect)
        if self.detect_mouse:self.mouse_collision(self.rect,self.get_mouse_pos())
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),self.get_mouse_pos())
        input_player=pygame.draw.rect(self.screen,self.border_color,self.rect,self.border)
        self.screen.blit(self._text_surface, (input_player.x+5, input_player.y-2))
    def pressed_button(self, rect, pressed_mouse, mouse_pos, draw=None, repeat: bool = None):
        if pressed_mouse[0] and self.states["presses_touch"]:
            if rect.collidepoint(mouse_pos):
                self.states["active"] = True
                self.states["presses_touch"] = False
                if self.sound_touch: self.sound_touch.play(loops=0)
            else: self.states["active"], self.states["presses_touch"] = False, False
        if not pressed_mouse[0]: self.states["presses_touch"] = True
        if self.states["active"]: self.draw_pressed_effect() if draw is None else draw()
    def draw_hover_effect(self):return pygame.draw.rect(self.screen,self.hover_color,self.rect)
    def draw_pressed_effect(self):return pygame.draw.rect(self.screen,self.pressed_color,self.rect)
    def show_player(self):return self.text
Input_text = InputText

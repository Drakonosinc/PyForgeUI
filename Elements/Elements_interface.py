import pygame
from pygame.locals import *
    def icon_dropdown(self,type_dropdown):
        match type_dropdown:
            case "down":return "V"
            case "up":return "Λ"
            case "right":return ">"
            case "left":return "<"
    def events(self, event):pass
    def draw(self):
        if self.detect_mouse:self.mouse_collision(self.rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self):pass
    def pressed_button(self,rect,pressed_mouse,mouse_pos):
        super().pressed_button(rect,pressed_mouse,mouse_pos)
        if pressed_mouse[0] and not rect.collidepoint(mouse_pos):self.states["active"],self.states["presses_touch"]=False,True
        if self.states["active"]:pass
    def charge_elements(self, elements: list):
        if self.elements is None:
            self.elements = elements
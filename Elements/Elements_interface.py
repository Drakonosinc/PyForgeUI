import pygame
from pygame.locals import *
    def pressed_button(self,rect,pressed_mouse,mouse_pos):
        super().pressed_button(rect,pressed_mouse,mouse_pos)
        if pressed_mouse[0] and not rect.collidepoint(mouse_pos):self.states["active"],self.states["presses_touch"]=False,True
        if self.states["active"]:pass
    def charge_elements(self, elements: list):
        if self.elements is None:
            self.elements = elements
import pygame
from pygame.locals import *

    def scroll_elements(self):
        max_scroll = self.content_height
        if max_scroll == 0:proportion = 0.0
        else:proportion = (self.thumb_rect.y - self.rect.y) / (self.rect.height - self.thumb_height)
        offset = int(proportion * max_scroll)
        for el, (x0, y0) in zip(self.elements, self.initial_positions):
            new_y = y0 - offset
            el.position = (x0, new_y)
            el.rect.y = new_y
        if callable(self.commands):self.commands(proportion)
    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
        pygame.draw.rect(self.screen, self.color_thumb, self.thumb_rect)
        if self.detect_mouse:self.mouse_collision(self.thumb_rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.thumb_rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self):return pygame.draw.rect(self.screen, self.hover_color, self.thumb_rect)
    def update_elements(self, elements: list):
        if self.elements is None:
            self.elements = elements
            self.initial_positions = [(el.position[0], el.position[1]) for el in self.elements]
            if self.elements:
                top = min(y for _, y in self.initial_positions)
                bottom = max(el.rect.bottom for el in self.elements)
                self.content_height = bottom - top
            else:self.content_height = self.rect.height
class Combo_Box(ElementBehavior):
    def __init__(self, config: dict):
        ElementBehavior.__init__(self, config)
        self.screen = config["screen"]
        self.position = config["position"]
        self.dropdown = config.get("size", (100, 200))
        self.type_dropdown = self.icon_dropdown(config.get("type_dropdown", "down"))
        self.color = config.get("color", (255, 255, 255))
        self.elements = None
        self.rect = pygame.Rect(*self.position)
        self.rect_dropdown = pygame.Rect(*self.position,*self.dropdown)
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
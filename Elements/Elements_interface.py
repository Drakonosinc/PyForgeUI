import pygame
from pygame.locals import *

    def draw(self):
        self.screen.blit(self.font.render(self.text, True,self.color), self.position)
        if self.Behavior.detect_mouse:self.Behavior.mouse_collision(self.rect,pygame.mouse.get_pos(),self.draw_hover_effect)
    def draw_hover_effect(self):return self.screen.blit(self.font.render(self.text,True,self.hover_color),self.position)
    def change_item(self,config:dict):
        self.position = config.get("position",self.position)
        self.color=config.get("color",self.color)
        self.text=config.get("text",self.text)
class TextButton(Text,ElementBehavior):
    def __init__(self,config:dict):
        Text.__init__(self, config)
        ElementBehavior.__init__(self, config)
    def draw(self):
        super().draw()
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def change_item(self,config:dict):
        super().change_item(config)
        self.detect_mouse=config.get("detect_mouse",self.detect_mouse)
        self.pressed=config.get("pressed",self.pressed)
class PolygonButton(ElementBehavior):
    def __init__(self,config:dict):
        super().__init__(config)
        self.screen = config["screen"]
        self.position = config["position"]
        self.hover_position = config.get("hover_position",self.position)
        self.color = config.get("color", (255, 255, 255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.detect_mouse=config.get("detect_mouse",True)
        self.rect = pygame.draw.polygon(self.screen, self.color, self.position).copy()
    def draw(self):
        pygame.draw.polygon(self.screen, self.color, self.position)
        if self.detect_mouse:self.mouse_collision(self.rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self):return pygame.draw.polygon(self.screen, self.hover_color, self.hover_position)
    def change_item(self,config:dict):
        self.color=config.get("color",self.color)
        self.detect_mouse=config.get("detect_mouse",self.detect_mouse)
        self.pressed=config.get("pressed",self.pressed)
class Input_text(ElementBehavior):
    def __init__(self,config:dict):
        super().__init__(config)
        self.screen = config["screen"]
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text","")
        self.color=config.get("color",(0,0,0))
        self.color_back=config.get("color_back",(255,255,255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.position = config["position"]
        self.detect_mouse=config.get("detect_mouse",True)
        self.pressed_color=config.get("pressed_color",(135,206,235))
        self.border_color=config.get("border_color",(127,127,127))
        self.border=config.get("border",2)
        self.rect = pygame.Rect(*self.position)
    def change_text(self,event):
        if self.states["active"] and event.type==KEYDOWN:
            if event.key == K_BACKSPACE:self.text=self.text[:-1]
            else:self.text+=event.unicode
    def draw(self):
        pygame.draw.rect(self.screen,self.color_back,self.rect)
        if self.detect_mouse:self.mouse_collision(self.rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
        input_player=pygame.draw.rect(self.screen,self.border_color,self.rect,self.border)
        self.screen.blit(self.font.render(self.text, True, self.color), (input_player.x+5, input_player.y-2))
    def draw_hover_effect(self):return pygame.draw.rect(self.screen,self.hover_color,self.rect)
    def pressed_button(self,rect,pressed_mouse,mouse_pos):
        super().pressed_button(rect,pressed_mouse,mouse_pos)
        if pressed_mouse[0] and not rect.collidepoint(mouse_pos):self.states["active"],self.states["presses_touch"]=False,True
        if self.states["active"]:pygame.draw.rect(self.screen,self.pressed_color,self.rect)
    def show_player(self):return self.text
class ScrollBar(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        self.screen = config["screen"]
        position = config["position"]
        self.rect = pygame.Rect(*position)
        self.hover_color=config.get("hover_color",(255, 199, 51))
        self.thumb_height = config.get("thumb_height", max(20, int(position[3] * config.get("thumb_ratio", 0.2))))
        self.thumb_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.thumb_height)
        self.color = config.get("color", (200, 200, 200))
        self.color_thumb = config.get("color_bar", (135, 206, 235))
        self.commands = config.get("command1")
        self.elements = None
        self.dragging = False
        self.drag_offset = 0
    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.thumb_rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = event.pos[1] - self.thumb_rect.y
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_y = event.pos[1] - self.drag_offset
            new_y = max(self.rect.top, min(new_y, self.rect.bottom - self.thumb_height))
            self.thumb_rect.y = new_y
            self.scroll_elements()
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
import pygame
from pygame.locals import *
from .Mouse_collision import MouseCollision
from .Pressed_button import PressedButton
class ElementBehavior(MouseCollision,PressedButton):
    _timer_initialized = False
    def __init__(self, config: dict):
        MouseCollision.__init__(self, config)
        PressedButton.__init__(self, config)
        self.states=config.get("states",{"detect_hover":True,"presses_touch":True,"click_time": None,"active":False})
        self.new_events(time=config.get("time",500))
    def events(self, event):pass
    def reactivate_pressed(self,event):
        if event.type==self.EVENT_NEW:self.states["presses_touch"]=True
    def new_events(self,time):
        self.EVENT_NEW = pygame.USEREVENT + self.define_event()
        if not ElementBehavior._timer_initialized or time != 500:
            pygame.time.set_timer(self.EVENT_NEW,time)
            ElementBehavior._timer_initialized = True
    def define_event(self):return 1
    def filter_rects_collision(self,rects: dict, mouse_pos, draws: list, option: bool=False):
        for rect, draw in zip(rects, draws):
            if rects[rect].collidepoint(mouse_pos):
                if option is True: self.pressed_button(rects[rect], pygame.mouse.get_pressed(), mouse_pos, draw)
                else:self.mouse_collision(rects[rect], mouse_pos, draw)
            if all(not rects[rect].collidepoint(mouse_pos) for rect in rects):self.states["detect_hover"],self.states["presses_touch"] = True,True

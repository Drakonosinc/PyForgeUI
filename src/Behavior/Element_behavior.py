import pygame
from pygame.locals import *
class ElementBehavior:
    def __init__(self, config: dict):
        self.states=config.get("states",{"detect_hover":True,"presses_touch":True,"click_time": None,"active":False})
        self.commands = [config.get(f"command{i}") for i in range(1,4)]
        self.new_events(time=config.get("time",500))
    def events(self, event):pass
    def new_events(self,time):
        self.EVENT_NEW = pygame.USEREVENT + self.define_event()
        pygame.time.set_timer(self.EVENT_NEW,time)
    def define_event(self):return 1
    def reactivate_pressed(self,event):
        if event.type==self.EVENT_NEW:self.states["presses_touch"]=True
    def draw_hover_effect(self):raise NotImplementedError
    def mouse_collision(self,rect,mouse_pos,draw=None):
        if rect.collidepoint(mouse_pos):
            self.draw_hover_effect() if draw is None else draw()
            if self.states["detect_hover"]:
                if self.sound_hover:self.sound_hover.play(loops=0)
                self.states["detect_hover"]=False
        else:self.states["detect_hover"]=True
    def pressed_button(self,rect,pressed_mouse,mouse_pos):
        current_time = pygame.time.get_ticks()
        if pressed_mouse[0] and rect.collidepoint(mouse_pos) and self.states["presses_touch"]:
            self.states["active"]=True
            self.states["presses_touch"]=False
            self.states["click_time"] = current_time
        if self.states["click_time"] is not None:
            if current_time - self.states["click_time"] >= 200:
                if self.sound_touch:self.sound_touch.play(loops=0)
                self.states["click_time"] = None
                self.states["presses_touch"] = True
                self.execute_commands()
    def execute_commands(self):
        try:
            for command in self.commands:
                if callable(command):command()
        except TypeError:return None

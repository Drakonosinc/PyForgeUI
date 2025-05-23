import pygame
class PressedButton:
    def __init__(self,config: dict):
        self.sound_touch = config.get("sound_touch")
        self.pressed = config.get("pressed",True)
        self.states=config.get("states",{"presses_touch":True,"click_time": None,"active":False})
    def pressed_button(self,rect,pressed_mouse,mouse_pos):
        current_time = pygame.time.get_ticks()
        if pressed_mouse[0] and rect.collidepoint(mouse_pos) and self.states["presses_touch"]:
            self.states["active"]=True
            self.states["presses_touch"]=False
            self.states["click_time"] = current_time
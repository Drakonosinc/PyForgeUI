import pygame
class PressedButton:
    def __init__(self,config: dict):
        self.sound_touch = config.get("sound_touch")
        self.pressed = config.get("pressed",True)
        self.states=config.get("states",{"presses_touch":True,"click_time": None,"active":False})
        self.repeat = config.get("repeat_button",False)
        self.commands = [config.get(f"command{i}") for i in range(1,config.get("number_commands", 4))]
    def pressed_button(self,rect,pressed_mouse,mouse_pos,draw=None,repeat:bool = None):
        def execute(sound = False, active = False, presses = True, time = None, command = True):
            if sound and self.sound_touch:self.sound_touch.play(loops=0)
            self.states["active"] = active
            self.states["presses_touch"] = presses
            self.states["click_time"] = None if time is None else time
            if command:self.execute_commands()
        repeat = self.repeat if repeat is None else repeat
        current_time = pygame.time.get_ticks()
        if pressed_mouse[0] and rect.collidepoint(mouse_pos) and self.states["presses_touch"]:execute(False,True,False,current_time,False)
        if not repeat and not pressed_mouse[0] and self.states["active"]:
            if rect.collidepoint(mouse_pos):execute()
        elif self.states["click_time"] is not None and repeat:
            if current_time - self.states["click_time"] >= 200:execute()
        if pressed_mouse[0] and not rect.collidepoint(mouse_pos) and self.states["active"]:self.states["active"],self.states["presses_touch"]=False,True
        if self.states["active"]:self.draw_pressed_effect() if draw is None else draw()
    def draw_pressed_effect(self):return NotImplementedError
    def execute_commands(self):
        try:
            for command in self.commands:
                if callable(command):command()
        except TypeError:return None
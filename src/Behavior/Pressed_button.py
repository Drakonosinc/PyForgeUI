import pygame
class PressedButton:
    def __init__(self,config: dict):
        self.sound_touch = config.get("sound_touch")
        self.pressed = config.get("pressed",True)
        self.states=config.get("states",{"presses_touch":True,"click_time": None,"active":False})
        self.commands = [config.get(f"command{i}") for i in range(1,config.get("number_commands", 4))]
    
    def draw_pressed_effect(self):return NotImplementedError
    def execute_commands(self):
        try:
            for command in self.commands:
                if callable(command):command()
        except TypeError:return None
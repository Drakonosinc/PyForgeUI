class PressedButton:
    def __init__(self,config: dict):
        self.sound_touch = config.get("sound_touch")
        self.pressed = config.get("pressed",True)
        self.states=config.get("states",{"presses_touch":True,"click_time": None,"active":False})
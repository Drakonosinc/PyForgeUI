from pygame.locals import *
from ..Behavior import *
class ElementBehavior(MouseCollision,PressedButton):
    def __init__(self, config: dict):
        MouseCollision.__init__(self, config)
        PressedButton.__init__(self, config)
        self.states=config.get("states",{"detect_hover":True,"presses_touch":True,"click_time": None,"active":False})
        self.commands = [config.get(f"command{i}") for i in range(1,4)]
        self.new_events(time=config.get("time",500))
    def events(self, event):pass
    def new_events(self,time):
        self.EVENT_NEW = pygame.USEREVENT + self.define_event()
        pygame.time.set_timer(self.EVENT_NEW,time)
    def define_event(self):return 1
    
    
    def execute_commands(self):
        try:
            for command in self.commands:
                if callable(command):command()
        except TypeError:return None
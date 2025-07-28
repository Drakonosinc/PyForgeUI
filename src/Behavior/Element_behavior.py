from pygame.locals import *
from ..Behavior import *
class ElementBehavior(MouseCollision,PressedButton):
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
        pygame.time.set_timer(self.EVENT_NEW,time)
    def define_event(self):return 1
    def filter_rects_collision(self,rects: dict, mouse_pos, draws: list, option: bool=False):
        
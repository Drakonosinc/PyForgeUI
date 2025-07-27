class MouseCollision:
    def __init__(self,config: dict):
        self.sound_hover = config.get("sound_hover")
        self.detect_mouse=config.get("detect_mouse",True)
        self.states=config.get("states",{"detect_hover":True})
    def mouse_collision(self,rect,mouse_pos,draw=None):
        if rect.collidepoint(mouse_pos):
            self.draw_hover_effect() if draw is None else draw()
            if self.states["detect_hover"]:
                if self.sound_hover:self.sound_hover.play(loops=0)
                self.states["detect_hover"]=False
        else:self.states["detect_hover"]=True
    def draw_hover_effect(self):raise NotImplementedError
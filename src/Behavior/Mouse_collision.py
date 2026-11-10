import pygame
class MouseCollision:
    def __init__(self,config: dict):
        self.screen = config["screen"]
        self.window = config.get("window", None)
        self.position = config["position"]
        self.sound_hover = config.get("sound_hover")
        self.detect_mouse = config.get("detect_mouse", True)
        if not hasattr(self, "states"):
            self.states = {}
        self.states.update({"detect_hover": True, **config.get("states", {})})
    def get_mouse_pos(self):
        return self.window.get_mouse_pos() if self.window else pygame.mouse.get_pos()
    def mouse_collision(self,rect,mouse_pos,draw=None):
        if rect.collidepoint(mouse_pos):
            self.draw_hover_effect() if draw is None else draw()
            if self.states["detect_hover"]:
                if self.sound_hover:self.sound_hover.play(loops=0)
                self.states["detect_hover"]=False
        else:self.states["detect_hover"]=True
    def draw_hover_effect(self):raise NotImplementedError

from ..Behavior.Element_behavior import *
class Text:
    def __init__(self,config:dict):
        self.screen = config["screen"]
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.Behavior = ElementBehavior(config)
        self.text = config["text"]
        self.color = config.get("color", (255, 255, 255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.position = config["position"]
        self.rect = pygame.Rect(*self.position, *self.font.size(self.text))
    def draw(self):
        self.screen.blit(self.font.render(self.text, True,self.color), self.position)
        if self.Behavior.detect_mouse:self.Behavior.mouse_collision(self.rect,pygame.mouse.get_pos(),self.draw_hover_effect)
    def draw_hover_effect(self):return self.screen.blit(self.font.render(self.text,True,self.hover_color),self.position)
    def change_item(self,config:dict):
        self.position = config.get("position",self.position)
        self.color=config.get("color",self.color)
        self.text=config.get("text",self.text)
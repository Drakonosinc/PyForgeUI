import pygame
from ..Behavior.Mouse_collision import MouseCollision
class Text(MouseCollision):
    def __init__(self,config:dict):
        MouseCollision.__init__(self, config)
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text", "")
        self.color = config.get("color", (255, 255, 255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self._update_surfaces()
    def _update_surfaces(self):
        self._text_surface = self.font.render(self.text, True, self.color)
        self._hover_surface = self.font.render(self.text, True, self.hover_color)
        self.rect = pygame.Rect(*self.position, *self._text_surface.get_size())
    def draw(self):
        if not getattr(self, "visible", True):
            return
        if self._is_visual_occluded_by_popup(self.rect if isinstance(self.rect, pygame.Rect) else None):
            self.states["is_hovered"] = False
            if "active" in self.states:
                self.states["active"] = False
            return
        self.screen.blit(self._text_surface, self.position)
        if self.detect_mouse:self.mouse_collision(self.rect,self.get_mouse_pos(),self.draw_hover_effect)
    def draw_hover_effect(self):return self.screen.blit(self._hover_surface, self.position)
    def change_item(self,config:dict):
        self.position = config.get("position",self.position)
        self.color=config.get("color",self.color)
        self.hover_color=config.get("hover_color",self.hover_color)
        self.text=config.get("text",self.text)
        self.detect_mouse=config.get("detect_mouse",self.detect_mouse)
        self._update_surfaces()

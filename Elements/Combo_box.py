from ..Behavior.Element_behavior import *
class ComboBox(ElementBehavior):
    def __init__(self, config: dict):
        ElementBehavior.__init__(self, config)
        self.screen = config["screen"]
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text","")
        self.position = config["position"]
        self.dropdown = config.get("size", (100, 200))
        self.type_dropdown = self.icon_dropdown(config.get("type_dropdown", "down"))
        self.color = config.get("color", (255, 255, 255))
        self.elements = None
        self.rect = pygame.Rect(*self.position)
        self.rect_dropdown = pygame.Rect(*self.position,*self.dropdown)
    def icon_dropdown(self,type_dropdown):
        match type_dropdown:
            case "down":return "V"
            case "up":return "Λ"
            case "right":return ">"
            case "left":return "<"
    def events(self, event):pass
    def draw(self):
        if self.detect_mouse:self.mouse_collision(self.rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self):pass
    def pressed_button(self,rect,pressed_mouse,mouse_pos):
        super().pressed_button(rect,pressed_mouse,mouse_pos)
        if pressed_mouse[0] and not rect.collidepoint(mouse_pos):self.states["active"],self.states["presses_touch"]=False,True
        if self.states["active"]:pass
    def charge_elements(self, elements: list):
        if self.elements is None:
            self.elements = elements
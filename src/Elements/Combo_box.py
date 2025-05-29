from ..Behavior.Element_behavior import *
class ComboBox(ElementBehavior):
    def __init__(self, config: dict):
        ElementBehavior.__init__(self, config)
        self.screen = config["screen"]
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text","")
        self.position = config["position"]
        self.dropdown = config.get("size", (self.font.size(self.text)[0], 200))
        self.type_dropdown = self.icon_dropdown(config.get("type_dropdown", "down"))
        self.color = config.get("color", (255, 255, 255))
        self.hover_color=config.get("hover_color",(255, 199, 51))
        self.hover_dropdown=config.get("hover_dropdown",(135,206,235))
        self.elements = None
        self.rect = pygame.Rect(*self.position,*self.font.size(self.text))
        self.rect_dropdown = pygame.Rect(self.position[0]+self.font.size(self.text)[0], self.position[1],*self.font.size(self.type_dropdown))
    def icon_dropdown(self,type_dropdown):
        match type_dropdown:
            case "down":return " V"
            case "up":return " Λ"
            case "right":return " >"
            case "left":return " <"
    def events(self, event):pass
    def draw(self):
        self.screen.blit(self.font.render(f"{self.text}{self.type_dropdown}", True,self.color), (self.position))
        if self.detect_mouse:self.mouse_collision(self.rect,pygame.mouse.get_pos(),self.draw_hover_effect1)
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self):pass
    def draw_pressed_effect(self):pass
    def charge_elements(self, elements: list):
        if self.elements is None:
            self.elements = elements
            for i in range(len(self.elements)):
                self.elements[i].position = None
class PolygonButton(ElementBehavior):
    def __init__(self,config:dict):
        super().__init__(config)
        self.screen = config["screen"]
        self.position = config["position"]
        self.hover_position = config.get("hover_position",self.position)
        self.color = config.get("color", (255, 255, 255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.detect_mouse=config.get("detect_mouse",True)
        self.rect = pygame.draw.polygon(self.screen, self.color, self.position).copy()
    def draw(self):
        pygame.draw.polygon(self.screen, self.color, self.position)
        if self.detect_mouse:self.mouse_collision(self.rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    
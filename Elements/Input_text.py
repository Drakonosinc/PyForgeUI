class Input_text(ElementBehavior):
    def __init__(self,config:dict):
        super().__init__(config)
        self.screen = config["screen"]
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text","")
        self.color=config.get("color",(0,0,0))
        self.color_back=config.get("color_back",(255,255,255))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.position = config["position"]
        self.detect_mouse=config.get("detect_mouse",True)
        self.pressed_color=config.get("pressed_color",(135,206,235))
        self.border_color=config.get("border_color",(127,127,127))
        self.border=config.get("border",2)
        self.rect = pygame.Rect(*self.position)
    
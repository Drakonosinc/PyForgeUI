class ScrollBar(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        self.screen = config["screen"]
        position = config["position"]
        self.rect = pygame.Rect(*position)
        self.hover_color=config.get("hover_color",(255, 199, 51))
        self.thumb_height = config.get("thumb_height", max(20, int(position[3] * config.get("thumb_ratio", 0.2))))
        self.thumb_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.thumb_height)
        self.color = config.get("color", (200, 200, 200))
        self.color_thumb = config.get("color_bar", (135, 206, 235))
        self.commands = config.get("command1")
        self.elements = None
        self.dragging = False
        self.drag_offset = 0
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
    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.thumb_rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = event.pos[1] - self.thumb_rect.y
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_y = event.pos[1] - self.drag_offset
            new_y = max(self.rect.top, min(new_y, self.rect.bottom - self.thumb_height))
            self.thumb_rect.y = new_y
            self.scroll_elements()
    def scroll_elements(self):
        max_scroll = self.content_height
        if max_scroll == 0:proportion = 0.0
        else:proportion = (self.thumb_rect.y - self.rect.y) / (self.rect.height - self.thumb_height)
        offset = int(proportion * max_scroll)
        for el, (x0, y0) in zip(self.elements, self.initial_positions):
            new_y = y0 - offset
            el.position = (x0, new_y)
            el.rect.y = new_y
        if callable(self.commands):self.commands(proportion)
    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
        pygame.draw.rect(self.screen, self.color_thumb, self.thumb_rect)
        if self.detect_mouse:self.mouse_collision(self.thumb_rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.thumb_rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    
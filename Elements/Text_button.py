class TextButton(Text,ElementBehavior):
    def __init__(self,config:dict):
        Text.__init__(self, config)
        ElementBehavior.__init__(self, config)
    def draw(self):
        super().draw()
        if self.pressed:self.pressed_button(self.rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def change_item(self,config:dict):
        super().change_item(config)
        self.detect_mouse=config.get("detect_mouse",self.detect_mouse)
        self.pressed=config.get("pressed",self.pressed)
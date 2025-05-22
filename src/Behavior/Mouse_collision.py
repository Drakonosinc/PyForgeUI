class MouseCollision:
    def __init__(self,config: dict):
        self.sound_hover = config.get("sound_hover")
        self.detect_mouse=config.get("detect_mouse",True)
    def draw_hover_effect(self):raise NotImplementedError
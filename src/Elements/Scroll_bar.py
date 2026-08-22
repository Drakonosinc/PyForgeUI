from ..Behavior.Element_behavior import *
class ScrollBar(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        rect = pygame.Rect(*self.position)
        self.type_of_orientation = config.get("type_of_orientation", "vertical").lower()
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.color = config.get("color", (200, 200, 200))
        self.color_thumb = config.get("color_bar", (135, 206, 235))

        self.elements = None
        self.dragging = False
        self.drag_offset = 0
        self.rect = {"rect": rect, "thumb": self.thumb_rect} 
    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.thumb_rect.collidepoint(event.pos):
                self.dragging = True


            self.scroll_elements()
    
    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect["rect"])
        pygame.draw.rect(self.screen, self.color_thumb, self.thumb_rect)
        if self.detect_mouse: self.mouse_collision(self.thumb_rect, self.get_mouse_pos())
        if self.pressed: self.pressed_button(self.thumb_rect, pygame.mouse.get_pressed(), self.get_mouse_pos())
    def draw_hover_effect(self):
        return pygame.draw.rect(self.screen, self.hover_color, self.thumb_rect)
    def update_elements(self, elements: list):
        if self.elements is None:
            self.elements = elements
            self.initial_positions = [(el.position[0], el.position[1]) for el in self.elements]
            if self.elements:
                if self.type_of_orientation == "vertical": start_pos = min(y for _, y in self.initial_positions)
                else: start_pos = min(x for x, _ in self.initial_positions)
                end_pos = self.return_rect()
                self.content_size = end_pos - start_pos
            else: self.content_size = self.rect["rect"].height if self.type_of_orientation == "vertical" else self.rect["rect"].width
    def return_rect(self):
        def get_bound(val):
            if isinstance(val, pygame.Rect): return val.bottom if self.type_of_orientation == "vertical" else val.right
            elif isinstance(val, dict): return max(get_bound(v) for v in val.values() if isinstance(v, (pygame.Rect, dict)))
            elif hasattr(val, 'rect'): return get_bound(val.rect)
            return 0
        max_bound = 0
        if self.elements:
            for el in self.elements:
                rect = getattr(el, 'rect', None)
                if isinstance(rect, dict):
                    for v in rect.values(): max_bound = max(max_bound, get_bound(v))
                else: max_bound = max(max_bound, get_bound(rect))
        return max_bound
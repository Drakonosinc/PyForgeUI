from ..Behavior.Element_behavior import *
class ScrollBar(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        rect = pygame.Rect(*self.position)
        self.type_of_orientation = config.get("type_of_orientation", "vertical").lower()
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.color = config.get("color", (200, 200, 200))
        self.color_thumb = config.get("color_bar", (135, 206, 235))
        if self.type_of_orientation == "vertical":
            self.thumb_size = config.get("thumb_height", max(20, int(self.position[3] * config.get("thumb_ratio", 0.2))))
            self.thumb_rect = pygame.Rect(rect.x, rect.y, rect.width, self.thumb_size)
        else:
            self.thumb_size = config.get("thumb_width", max(20, int(self.position[2] * config.get("thumb_ratio", 0.2))))
            self.thumb_rect = pygame.Rect(rect.x, rect.y, self.thumb_size, rect.height)
        self.elements = None
        self.dragging = False
        self.drag_offset = 0
        self.rect = {"rect": rect, "thumb": self.thumb_rect} 
    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.thumb_rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = (event.pos[1] - self.thumb_rect.y) if self.type_of_orientation == "vertical" else (event.pos[0] - self.thumb_rect.x)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            if self.type_of_orientation == "vertical":
                new_pos = event.pos[1] - self.drag_offset
                new_pos = max(self.rect["rect"].top, min(new_pos, self.rect["rect"].bottom - self.thumb_size))
                self.thumb_rect.y = new_pos
            else:
                new_pos = event.pos[0] - self.drag_offset
                new_pos = max(self.rect["rect"].left, min(new_pos, self.rect["rect"].right - self.thumb_size))
                self.thumb_rect.x = new_pos
            self.scroll_elements()
    def scroll_elements(self):
        max_scroll = self.content_size
        if max_scroll == 0:  proportion = 0.0
        else: 
            if self.type_of_orientation == "vertical": proportion = (self.thumb_rect.y - self.rect["rect"].y) / (self.rect["rect"].height - self.thumb_size)
            else: proportion = (self.thumb_rect.x - self.rect["rect"].x) / (self.rect["rect"].width - self.thumb_size)
        offset = int(proportion * max_scroll)

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
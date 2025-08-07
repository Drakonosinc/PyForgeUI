from ..Behavior.Element_behavior import *
class ScrollBar(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        rect = pygame.Rect(*self.position)
        self.hover_color=config.get("hover_color",(255, 199, 51))
        self.thumb_height = config.get("thumb_height", max(20, int(self.position[3] * config.get("thumb_ratio", 0.2))))
        self.thumb_rect = pygame.Rect(rect.x, rect.y, rect.width, self.thumb_height)
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
                self.drag_offset = event.pos[1] - self.thumb_rect.y
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_y = event.pos[1] - self.drag_offset
            new_y = max(self.rect["rect"].top, min(new_y, self.rect["rect"].bottom - self.thumb_height))
            self.thumb_rect.y = new_y
            self.scroll_elements()
    def scroll_elements(self):
        max_scroll = self.content_height
        if max_scroll == 0: proportion = 0.0
        else: proportion = (self.thumb_rect.y - self.rect["rect"].y) / (self.rect["rect"].height - self.thumb_height)
        offset = int(proportion * max_scroll)
        for el, (x0, y0) in zip(self.elements, self.initial_positions):
            old_y = el.position[1]
            new_y = y0 - offset
            el.position = (x0, new_y)
            delta = new_y - old_y
            def add_delta(item, delta):
                if isinstance(item, pygame.Rect):item.y += delta
                elif isinstance(item, dict):
                    for v in item.values():add_delta(v, delta)
                elif hasattr(item, 'rect') and hasattr(item, 'position'):
                    add_delta(item.rect, delta)
                    item.position = (item.position[0], item.position[1] + delta)
            if isinstance(el.rect, dict):
                for key in el.rect:add_delta(el.rect[key], delta)
            else:add_delta(el.rect, delta)
        if hasattr(el, 'scroll') and isinstance(el.scroll, ScrollBar):el.scroll.initial_positions = [(sub_el.position[0], sub_el.position[1]) for sub_el in el.scroll.elements]
        if callable(self.commands): self.commands(proportion)
    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect["rect"])
        pygame.draw.rect(self.screen, self.color_thumb, self.thumb_rect)
        if self.detect_mouse:self.mouse_collision(self.thumb_rect,pygame.mouse.get_pos())
        if self.pressed:self.pressed_button(self.thumb_rect,pygame.mouse.get_pressed(),pygame.mouse.get_pos())
    def draw_hover_effect(self):return pygame.draw.rect(self.screen, self.hover_color, self.thumb_rect)
    def update_elements(self, elements: list):
        if self.elements is None:
            self.elements = elements
            self.initial_positions = [(el.position[0], el.position[1]) for el in self.elements]
            if self.elements:
                top = min(y for _, y in self.initial_positions)
                bottom = self.return_rect()
                self.content_height = bottom - top
            else:self.content_height = self.rect.height
    def return_rect(self):
        def get_bottom(val):
            if isinstance(val, pygame.Rect):return val.bottom
            elif isinstance(val, dict):return max(get_bottom(v) for v in val.values() if isinstance(v, (pygame.Rect, dict)))
            elif hasattr(val, 'rect'):return get_bottom(val.rect)
            return 0
        max_bottom = 0
        if self.elements:
            for el in self.elements:
                rect = getattr(el, 'rect', None)
                if isinstance(rect, dict):
                    for v in rect.values():max_bottom = max(max_bottom, get_bottom(v))
                else:max_bottom = max(max_bottom, get_bottom(rect))
        return max_bottom
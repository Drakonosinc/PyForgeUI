import pygame
from ..Behavior.Element_behavior import ElementBehavior


class Panel(ElementBehavior):
    """Container widget with optional header bar, dragging, clipping, and child management."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 24))
        self.title: str = config.get("title", config.get("text", ""))
        self.draggable: bool = config.get("draggable", False)
        self.clip_children: bool = config.get("clip_children", False)
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (32, 36, 44))
        self.header_color: tuple = config.get("header_color", (48, 54, 66))
        self.border_color: tuple = config.get("border_color", (110, 120, 140))
        self.border: int = config.get("border", 2)
        self.border_radius: int = config.get("border_radius", 6)
        self.header_height: int = config.get("header_height", 30 if self.title else 0)

        if len(self.position) >= 4:
            self.rect = pygame.Rect(*self.position[:4])
        else:
            self.rect = pygame.Rect(self.position[0], self.position[1], config.get("width", 300), config.get("height", 220))

        self.children: list = list(config.get("children", []))
        self.dragging: bool = False
        self._drag_offset: tuple[int, int] = (0, 0)
        self._update_surfaces()

    def _update_surfaces(self) -> None:
        self._title_surface = self.font.render(self.title, True, self.color) if self.title else None
        self.header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.header_height if self.header_height > 0 else 28)

    def add_child(self, child, relative_pos: tuple[int, int] | None = None):
        if relative_pos is not None and hasattr(child, "set_position"):
            y_off = self.header_height if self.title else 0
            child.set_position(self.rect.x + relative_pos[0], self.rect.y + y_off + relative_pos[1])
        if child not in self.children:
            self.children.append(child)
        return child

    def remove_child(self, child) -> None:
        if child in self.children:
            self.children.remove(child)

    def move(self, dx: int, dy: int) -> None:
        if dx == 0 and dy == 0:
            return
        super().move(dx, dy)
        self.header_rect.move_ip(dx, dy)
        for child in self.children:
            if hasattr(child, "move"):
                child.move(dx, dy)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        for child in reversed(self.children):
            if hasattr(child, "events") and child.events(event):
                return True

        if self.draggable:
            drag_zone = self.header_rect if self.title else self.rect
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if drag_zone.collidepoint(event.pos):
                    self.dragging = True
                    self._drag_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                    return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    self.dragging = False
                    return True
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                new_x = event.pos[0] - self._drag_offset[0]
                new_y = event.pos[1] - self._drag_offset[1]
                self.move(new_x - self.rect.x, new_y - self.rect.y)
                return True

        return False

    def draw(self) -> None:
        if not self.visible:
            return
        pygame.draw.rect(self.screen, self.color_back, self.rect, border_radius=self.border_radius)
        if self.title and self.header_height > 0:
            hdr = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.header_height)
            pygame.draw.rect(
                self.screen,
                self.header_color,
                hdr,
                border_top_left_radius=self.border_radius,
                border_top_right_radius=self.border_radius,
            )
            if self._title_surface:
                ty = hdr.centery - self._title_surface.get_height() // 2
                self.screen.blit(self._title_surface, (hdr.x + 10, ty))

        if self.border > 0:
            pygame.draw.rect(self.screen, self.border_color, self.rect, self.border, border_radius=self.border_radius)

        prev_clip = self.screen.get_clip()
        if self.clip_children:
            content_rect = pygame.Rect(
                self.rect.x + self.border,
                self.rect.y + self.header_height + self.border,
                max(0, self.rect.width - self.border * 2),
                max(0, self.rect.height - self.header_height - self.border * 2),
            )
            self.screen.set_clip(content_rect)

        for child in self.children:
            if getattr(child, "visible", True) and hasattr(child, "draw"):
                child.draw()


        if self.clip_children:
            self.screen.set_clip(prev_clip)

    def draw_hover_effect(self) -> None:
        pass

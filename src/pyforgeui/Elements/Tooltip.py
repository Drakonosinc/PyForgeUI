import pygame
from ..Behavior.Mouse_collision import MouseCollision


class Tooltip(MouseCollision):
    """Floating tooltip widget that renders after a hover delay or on demand."""

    def __init__(self, config: dict) -> None:
        config.setdefault("position", (0, 0))
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 20))
        self.text: str = config.get("text", "")
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (35, 38, 45))
        self.border_color: tuple = config.get("border_color", (255, 199, 51))
        self.border: int = config.get("border", 1)
        self.padding: int = config.get("padding", 6)
        self.delay_ms: int = config.get("delay_ms", 350)
        self.offset: tuple[int, int] = config.get("offset", (14, 18))
        self.target = config.get("target", None)
        self._hover_start_time: int | None = None
        self._update_surfaces()

    def _update_surfaces(self) -> None:
        lines = self.text.split("\n") if self.text else [""]
        self._line_surfaces = [self.font.render(line, True, self.color) for line in lines]
        width = max((s.get_width() for s in self._line_surfaces), default=0) + self.padding * 2
        height = sum(s.get_height() for s in self._line_surfaces) + self.padding * 2
        self._box_surface = pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)
        self._box_surface.fill((*self.color_back[:3], 240))
        if self.border > 0:
            pygame.draw.rect(self._box_surface, self.border_color, self._box_surface.get_rect(), self.border, border_radius=4)
        y_cursor = self.padding
        for surf in self._line_surfaces:
            self._box_surface.blit(surf, (self.padding, y_cursor))
            y_cursor += surf.get_height()
        self.rect = pygame.Rect(self.position[0], self.position[1], width, height)

    def set_text(self, text: str) -> None:
        if text != self.text:
            self.text = text
            self._update_surfaces()

    def change_item(self, config: dict) -> None:
        self.text = config.get("text", self.text)
        self.color = config.get("color", self.color)
        self.color_back = config.get("color_back", self.color_back)
        self.border_color = config.get("border_color", self.border_color)
        self._update_surfaces()

    def draw_at(self, mouse_pos: tuple[int, int], text: str | None = None) -> None:
        if text is not None and text != self.text:
            self.set_text(text)
        if not self.text:
            return
        screen_w, screen_h = self.screen.get_size()
        x = mouse_pos[0] + self.offset[0]
        y = mouse_pos[1] + self.offset[1]
        if x + self.rect.width > screen_w - 4:
            x = max(4, mouse_pos[0] - self.rect.width - 8)
        if y + self.rect.height > screen_h - 4:
            y = max(4, mouse_pos[1] - self.rect.height - 8)
        self.position = (x, y)
        self.rect.topleft = self.position
        self.screen.blit(self._box_surface, self.position)

    def draw(self) -> None:
        if not self.visible or not self.text:
            return
        mouse_pos = self.get_mouse_pos()
        if self.target is not None:
            bounds = self.target.get_bounding_rect() if hasattr(self.target, "get_bounding_rect") else getattr(self.target, "rect", None)
            is_over = bounds.collidepoint(mouse_pos) if isinstance(bounds, pygame.Rect) else False
            if is_over:
                now = pygame.time.get_ticks()
                if self._hover_start_time is None:
                    self._hover_start_time = now
                elif now - self._hover_start_time >= self.delay_ms:
                    self.draw_at(mouse_pos)
            else:
                self._hover_start_time = None
        else:
            self.draw_at(mouse_pos)

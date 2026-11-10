import pygame
from ..Behavior.Element_behavior import ElementBehavior


class Slider(ElementBehavior):
    """Numeric range slider supporting horizontal/vertical orientation, step snapping, and value display."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 22))
        self.orientation: str = config.get("orientation", config.get("type_of_orientation", "horizontal")).lower()
        self.min_value: float = float(config.get("min_value", 0.0))
        self.max_value: float = float(config.get("max_value", 100.0))
        self.step: float = float(config.get("step", 0.0))
        initial_val = float(config.get("value", self.min_value))
        self.value: float = max(self.min_value, min(self.max_value, initial_val))
        self.show_value: bool = config.get("show_value", True)
        self.label: str = config.get("label", config.get("text", ""))
        self.color: tuple = config.get("color", (255, 255, 255))
        self.track_color: tuple = config.get("track_color", (65, 70, 82))
        self.fill_color: tuple = config.get("fill_color", (85, 170, 255))
        self.thumb_color: tuple = config.get("thumb_color", (240, 245, 255))
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self.on_change = config.get("on_change", None)
        self.dragging: bool = False

        if len(self.position) >= 4:
            self.rect = pygame.Rect(*self.position[:4])
        else:
            w, h = (180, 12) if self.orientation == "horizontal" else (12, 180)
            self.rect = pygame.Rect(self.position[0], self.position[1], w, h)

        self.thumb_radius: int = config.get("thumb_radius", max(8, (self.rect.height if self.orientation == "horizontal" else self.rect.width) // 2 + 4))
        self._update_surfaces()

    def _format_value(self) -> str:
        if self.step >= 1 or (self.step == 0 and self.min_value.is_integer() and self.max_value.is_integer()):
            val_str = str(int(round(self.value)))
        else:
            val_str = f"{self.value:.2f}"
        return f"{self.label}: {val_str}" if self.label else val_str

    def _update_surfaces(self) -> None:
        txt = self._format_value() if (self.show_value or self.label) else ""
        self._value_surface = self.font.render(txt, True, self.color) if txt else None

    def get_ratio(self) -> float:
        span = self.max_value - self.min_value
        if span <= 0:
            return 0.0
        return max(0.0, min(1.0, (self.value - self.min_value) / span))

    def _thumb_center(self) -> tuple[int, int]:
        ratio = self.get_ratio()
        if self.orientation == "horizontal":
            cx = int(self.rect.left + ratio * self.rect.width)
            cy = self.rect.centery
        else:
            cx = self.rect.centerx
            cy = int(self.rect.bottom - ratio * self.rect.height)
        return (cx, cy)

    def get_thumb_rect(self) -> pygame.Rect:
        cx, cy = self._thumb_center()
        r = self.thumb_radius
        return pygame.Rect(cx - r, cy - r, r * 2, r * 2)

    def set_value(self, new_val: float, trigger_callback: bool = True) -> None:
        clamped = max(self.min_value, min(self.max_value, float(new_val)))
        if self.step > 0:
            steps = round((clamped - self.min_value) / self.step)
            clamped = max(self.min_value, min(self.max_value, self.min_value + steps * self.step))
        if abs(clamped - self.value) > 1e-6:
            self.value = clamped
            self._update_surfaces()
            if trigger_callback:
                if callable(self.on_change):
                    self.on_change(self.value)
                self.execute_commands(self.value)

    def get_value(self) -> float:
        return self.value

    def _set_from_mouse(self, pos: tuple[int, int]) -> None:
        if self.orientation == "horizontal":
            ratio = (pos[0] - self.rect.left) / max(1, self.rect.width)
        else:
            ratio = (self.rect.bottom - pos[1]) / max(1, self.rect.height)
        ratio = max(0.0, min(1.0, ratio))
        raw_val = self.min_value + ratio * (self.max_value - self.min_value)
        self.set_value(raw_val, trigger_callback=True)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        hit_rect = self.rect.union(self.get_thumb_rect())
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hit_rect.collidepoint(event.pos):
                self.dragging = True
                if self.sound_touch:
                    self.sound_touch.play(loops=0)
                self._set_from_mouse(event.pos)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos)
            return True
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        border_rad = min(self.rect.width, self.rect.height) // 2
        pygame.draw.rect(self.screen, self.track_color, self.rect, border_radius=border_rad)

        ratio = self.get_ratio()
        if self.orientation == "horizontal":
            fill_w = int(self.rect.width * ratio)
            if fill_w > 0:
                fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
                pygame.draw.rect(self.screen, self.fill_color, fill_rect, border_radius=border_rad)
        else:
            fill_h = int(self.rect.height * ratio)
            if fill_h > 0:
                fill_rect = pygame.Rect(self.rect.x, self.rect.bottom - fill_h, self.rect.width, fill_h)
                pygame.draw.rect(self.screen, self.fill_color, fill_rect, border_radius=border_rad)

        cx, cy = self._thumb_center()
        pygame.draw.circle(self.screen, self.thumb_color, (cx, cy), self.thumb_radius)

        if self.detect_mouse:
            self.mouse_collision(self.rect.union(self.get_thumb_rect()), self.get_mouse_pos(), self.draw_hover_effect)

        if self._value_surface:
            if self.orientation == "horizontal":
                val_pos = (self.rect.x, self.rect.y - self._value_surface.get_height() - 6)
            else:
                val_pos = (self.rect.right + 10, self.rect.centery - self._value_surface.get_height() // 2)
            self.screen.blit(self._value_surface, val_pos)

    def draw_hover_effect(self) -> None:
        cx, cy = self._thumb_center()
        pygame.draw.circle(self.screen, self.hover_color, (cx, cy), self.thumb_radius, 2)

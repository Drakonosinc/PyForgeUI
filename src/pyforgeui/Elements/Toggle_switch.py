import pygame
from ..Behavior.Element_behavior import ElementBehavior


class ToggleSwitch(ElementBehavior):
    """Animated pill-shaped boolean toggle switch with optional label."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 25))
        self.text: str = config.get("text", "")
        self.width: int = config.get("width", 48)
        self.height: int = config.get("height", 24)
        self.value: bool = config.get("value", config.get("checked", False))
        self.color: tuple = config.get("color", (255, 255, 255))
        self.off_color: tuple = config.get("off_color", (90, 95, 110))
        self.on_color: tuple = config.get("on_color", (65, 195, 115))
        self.knob_color: tuple = config.get("knob_color", (250, 250, 250))
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self.spacing: int = config.get("spacing", 10)
        self.on_change = config.get("on_change", None)
        self._anim_progress: float = 1.0 if self.value else 0.0
        self._update_surfaces()

    def _update_surfaces(self) -> None:
        x, y = int(self.position[0]), int(self.position[1])
        self.track_rect = pygame.Rect(x, y, self.width, self.height)
        self._label_surface = self.font.render(self.text, True, self.color) if self.text else None
        self._label_hover_surface = self.font.render(self.text, True, self.hover_color) if self.text else None
        if self._label_surface:
            label_y = y + (self.height - self._label_surface.get_height()) // 2
            self.label_pos = (x + self.width + self.spacing, label_y)
            total_w = self.width + self.spacing + self._label_surface.get_width()
            total_h = max(self.height, self._label_surface.get_height())
            self.rect = pygame.Rect(x, min(y, label_y), total_w, total_h)
        else:
            self.label_pos = (x, y)
            self.rect = self.track_rect.copy()

    def move(self, dx: int, dy: int) -> None:
        super().move(dx, dy)
        self.track_rect.x += dx
        self.track_rect.y += dy
        self.label_pos = (self.label_pos[0] + dx, self.label_pos[1] + dy)

    def toggle(self) -> bool:
        self.set_value(not self.value)
        return self.value

    def set_value(self, value: bool) -> None:
        new_val = bool(value)
        if self.value != new_val:
            self.value = new_val
            if callable(self.on_change):
                self.on_change(self.value)
            self.execute_commands(self.value)

    def get_value(self) -> bool:
        return self.value

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.sound_touch:
                    self.sound_touch.play(loops=0)
                self.toggle()
                self.states["presses_touch"] = False
                return True
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        target = 1.0 if self.value else 0.0
        if abs(self._anim_progress - target) > 0.01:
            self._anim_progress += (target - self._anim_progress) * 0.25
        else:
            self._anim_progress = target

        track_col = tuple(
            int(self.off_color[i] + (self.on_color[i] - self.off_color[i]) * self._anim_progress)
            for i in range(3)
        )
        radius = self.height // 2
        pygame.draw.rect(self.screen, track_col, self.track_rect, border_radius=radius)

        if self._label_surface:
            self.screen.blit(self._label_surface, self.label_pos)

        mouse_pos = self.get_mouse_pos()
        if self.detect_mouse:
            self.mouse_collision(self.rect, mouse_pos, self.draw_hover_effect)

        pad = 3
        knob_radius = radius - pad
        min_cx = self.track_rect.left + radius
        max_cx = self.track_rect.right - radius
        cx = int(min_cx + (max_cx - min_cx) * self._anim_progress)
        cy = self.track_rect.centery
        pygame.draw.circle(self.screen, self.knob_color, (cx, cy), knob_radius)

    def draw_hover_effect(self) -> None:
        pygame.draw.rect(self.screen, self.hover_color, self.track_rect, 2, border_radius=self.height // 2)
        if self._label_hover_surface:
            self.screen.blit(self._label_hover_surface, self.label_pos)

    def change_item(self, config: dict) -> None:
        self.position = config.get("position", self.position)
        self.text = config.get("text", self.text)
        if "value" in config or "checked" in config:
            self.value = bool(config.get("value", config.get("checked", self.value)))
        self._update_surfaces()

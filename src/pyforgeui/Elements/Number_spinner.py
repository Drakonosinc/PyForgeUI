import pygame
from ..Behavior.Element_behavior import ElementBehavior


class NumberSpinner(ElementBehavior):
    """Numeric selector with decrement (-) and increment (+) buttons and display box."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 24))
        self.min_value: float = float(config.get("min_value", 0))
        self.max_value: float = float(config.get("max_value", 99))
        self.step: float = float(config.get("step", 1))
        self.value: float = max(self.min_value, min(self.max_value, float(config.get("value", self.min_value))))
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (45, 48, 56))
        self.button_color: tuple = config.get("button_color", (65, 72, 86))
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self.border_color: tuple = config.get("border_color", (160, 165, 175))
        self.on_change = config.get("on_change", None)

        if len(self.position) >= 4:
            x, y, w, h = [int(v) for v in self.position[:4]]
        else:
            x, y = int(self.position[0]), int(self.position[1])
            w, h = config.get("width", 120), config.get("height", 30)

        btn_w = max(24, h)
        self.minus_rect = pygame.Rect(x, y, btn_w, h)
        self.value_rect = pygame.Rect(x + btn_w, y, max(36, w - btn_w * 2), h)
        self.plus_rect = pygame.Rect(self.value_rect.right, y, btn_w, h)
        self.rect = pygame.Rect(x, y, self.plus_rect.right - x, h)
        self._minus_surf = self.font.render("-", True, self.color)
        self._plus_surf = self.font.render("+", True, self.color)
        self._update_surfaces()

    def _format_val(self) -> str:
        if self.step.is_integer() and self.value.is_integer():
            return str(int(self.value))
        return f"{self.value:.2f}"

    def _update_surfaces(self) -> None:
        self._val_surf = self.font.render(self._format_val(), True, self.color)

    def move(self, dx: int, dy: int) -> None:
        super().move(dx, dy)
        self.minus_rect.move_ip(dx, dy)
        self.value_rect.move_ip(dx, dy)
        self.plus_rect.move_ip(dx, dy)

    def set_value(self, val: float) -> None:
        clamped = max(self.min_value, min(self.max_value, float(val)))
        if abs(clamped - self.value) > 1e-6:
            self.value = clamped
            self._update_surfaces()
            if callable(self.on_change):
                self.on_change(self.value)
            self.execute_commands(self.value)

    def get_value(self) -> float:
        return int(self.value) if (self.step.is_integer() and self.value.is_integer()) else self.value

    def increment(self) -> None:
        self.set_value(self.value + self.step)

    def decrement(self) -> None:
        self.set_value(self.value - self.step)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.minus_rect.collidepoint(event.pos):
                if self.sound_touch:
                    self.sound_touch.play(loops=0)
                self.decrement()
                return True
            if self.plus_rect.collidepoint(event.pos):
                if self.sound_touch:
                    self.sound_touch.play(loops=0)
                self.increment()
                return True
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        mouse_pos = self.get_mouse_pos()
        pygame.draw.rect(self.screen, self.button_color, self.minus_rect, border_top_left_radius=4, border_bottom_left_radius=4)
        pygame.draw.rect(self.screen, self.color_back, self.value_rect)
        pygame.draw.rect(self.screen, self.button_color, self.plus_rect, border_top_right_radius=4, border_bottom_right_radius=4)
        pygame.draw.rect(self.screen, self.border_color, self.rect, 2, border_radius=4)

        if self.detect_mouse:
            if self.minus_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, self.hover_color, self.minus_rect, 2, border_top_left_radius=4, border_bottom_left_radius=4)
            elif self.plus_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, self.hover_color, self.plus_rect, 2, border_top_right_radius=4, border_bottom_right_radius=4)

        self.screen.blit(self._minus_surf, (self.minus_rect.centerx - self._minus_surf.get_width() // 2, self.minus_rect.centery - self._minus_surf.get_height() // 2))
        self.screen.blit(self._val_surf, (self.value_rect.centerx - self._val_surf.get_width() // 2, self.value_rect.centery - self._val_surf.get_height() // 2))
        self.screen.blit(self._plus_surf, (self.plus_rect.centerx - self._plus_surf.get_width() // 2, self.plus_rect.centery - self._plus_surf.get_height() // 2))

    def draw_hover_effect(self) -> None:
        pass

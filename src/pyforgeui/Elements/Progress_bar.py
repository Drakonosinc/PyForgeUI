import pygame
from ..Behavior.Mouse_collision import MouseCollision


class ProgressBar(MouseCollision):
    """HUD / Loading progress bar with smooth interpolation and optional text overlay."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 20))
        self.min_value: float = float(config.get("min_value", 0.0))
        self.max_value: float = float(config.get("max_value", 100.0))
        self.value: float = float(config.get("value", self.max_value))
        self._display_value: float = self.value
        self.smooth_speed: float = float(config.get("smooth_speed", 0.2))
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (40, 44, 52))
        self.fill_color: tuple = config.get("fill_color", (75, 200, 110))
        self.border_color: tuple = config.get("border_color", (180, 185, 195))
        self.border: int = config.get("border", 2)
        self.border_radius: int = config.get("border_radius", 5)
        self.show_text: bool = config.get("show_text", True)
        self.show_percentage: bool = config.get("show_percentage", False)
        self.label: str = config.get("label", config.get("text", ""))
        if len(self.position) >= 4:
            self.rect = pygame.Rect(*self.position[:4])
        else:
            self.rect = pygame.Rect(self.position[0], self.position[1], config.get("width", 200), config.get("height", 24))
        self._update_surfaces()

    def _format_text(self) -> str:
        if not self.show_text:
            return ""
        span = max(1e-6, self.max_value - self.min_value)
        pct = int(round(((self.value - self.min_value) / span) * 100))
        if self.show_percentage:
            val_part = f"{pct}%"
        else:
            val_part = f"{int(round(self.value))}/{int(round(self.max_value))}"
        return f"{self.label}: {val_part}" if self.label else val_part

    def _update_surfaces(self) -> None:
        txt = self._format_text()
        self._text_surface = self.font.render(txt, True, self.color) if txt else None

    def set_value(self, value: float) -> None:
        clamped = max(self.min_value, min(self.max_value, float(value)))
        if abs(clamped - self.value) > 1e-6:
            self.value = clamped
            self._update_surfaces()

    def get_value(self) -> float:
        return self.value

    def events(self, event: pygame.event.Event) -> bool:
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        if abs(self._display_value - self.value) > 0.05:
            self._display_value += (self.value - self._display_value) * self.smooth_speed
        else:
            self._display_value = self.value

        pygame.draw.rect(self.screen, self.color_back, self.rect, border_radius=self.border_radius)

        span = self.max_value - self.min_value
        ratio = max(0.0, min(1.0, (self._display_value - self.min_value) / span)) if span > 0 else 0.0
        fill_w = int(self.rect.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            pygame.draw.rect(self.screen, self.fill_color, fill_rect, border_radius=self.border_radius)

        if self.border > 0:
            pygame.draw.rect(self.screen, self.border_color, self.rect, self.border, border_radius=self.border_radius)

        if self._text_surface:
            tx = self.rect.centerx - self._text_surface.get_width() // 2
            ty = self.rect.centery - self._text_surface.get_height() // 2
            self.screen.blit(self._text_surface, (tx, ty))

    def draw_hover_effect(self) -> None:
        pass

    def change_item(self, config: dict) -> None:
        if "value" in config:
            self.set_value(config["value"])
        if "max_value" in config:
            self.max_value = float(config["max_value"])
        if "fill_color" in config:
            self.fill_color = config["fill_color"]
        if "label" in config or "text" in config:
            self.label = config.get("label", config.get("text", self.label))
        self._update_surfaces()

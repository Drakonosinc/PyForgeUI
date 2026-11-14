import pygame
from ..Behavior.Element_behavior import ElementBehavior
from ..VisualFX import RetroVisualFX


class PolygonButton(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        self.hover_position = config.get("hover_position", config.get("position2", self.position))
        self.color = config.get("color", (255, 255, 255))
        self.outline_color = config.get("outline_color", config.get("color2", None))
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.modern_style: bool = config.get("modern_style", True)
        self._hover_anim: float = 0.0
        base_rect = pygame.draw.polygon(self.screen, self.color, self.position).copy()
        if self.hover_position and len(self.hover_position) >= 3:
            min_x = int(min(p[0] for p in (*self.position, *self.hover_position)))
            max_x = int(max(p[0] for p in (*self.position, *self.hover_position)))
            min_y = int(min(p[1] for p in (*self.position, *self.hover_position)))
            max_y = int(max(p[1] for p in (*self.position, *self.hover_position)))
            self.rect = pygame.Rect(min_x, min_y, max(1, max_x - min_x + 1), max(1, max_y - min_y + 1))
        else:
            self.rect = base_rect

    def _get_interpolated_points(self, t: float) -> list[tuple[float, float]]:
        if t <= 0.01 or not self.hover_position or len(self.hover_position) != len(self.position):
            return list(self.position)
        return [
            (
                p1[0] + (p2[0] - p1[0]) * t,
                p1[1] + (p2[1] - p1[1]) * t,
            )
            for p1, p2 in zip(self.position, self.hover_position)
        ]

    def draw(self):
        if not getattr(self, "visible", True) or self._is_visual_occluded_by_popup(self.rect):
            return

        mouse_pos = self.get_mouse_pos()
        is_hovered = (
            self.detect_mouse
            and not self._is_occluded_by_popup(self.rect, mouse_pos)
            and self.rect.collidepoint(mouse_pos)
        )
        target = 1.0 if is_hovered else 0.0
        if abs(self._hover_anim - target) > 0.01:
            self._hover_anim += (target - self._hover_anim) * 0.35
        else:
            self._hover_anim = target

        if self.modern_style:
            pts = self._get_interpolated_points(self._hover_anim)
            RetroVisualFX.draw_glow_polygon(
                self.screen,
                pts,
                fill_color=self.color,
                outline_color=self.outline_color,
                hover_color=self.hover_color,
                hover_progress=self._hover_anim,
                enabled=bool(self.detect_mouse or self.pressed or self.outline_color is not None),
            )
        else:
            pygame.draw.polygon(self.screen, self.color, self.position)
            if self.outline_color is not None:
                pygame.draw.polygon(self.screen, self.outline_color, self.position, 2)

        if self.detect_mouse:
            self.mouse_collision(self.rect, mouse_pos)
        if self.pressed:
            self.pressed_button(self.rect, pygame.mouse.get_pressed(), mouse_pos)

    def draw_hover_effect(self):
        if self.modern_style:
            return self.rect
        return pygame.draw.polygon(self.screen, self.hover_color, self.hover_position)

    def change_item(self, config: dict):
        self.color = config.get("color", self.color)
        self.outline_color = config.get("outline_color", config.get("color2", self.outline_color))
        self.hover_color = config.get("hover_color", self.hover_color)
        self.detect_mouse = config.get("detect_mouse", self.detect_mouse)
        self.pressed = config.get("pressed", self.pressed)

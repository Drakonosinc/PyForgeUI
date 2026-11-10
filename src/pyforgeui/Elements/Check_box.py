import pygame
from ..Behavior.Element_behavior import ElementBehavior


class CheckBox(ElementBehavior):
    """Boolean checkbox control with optional text label and callback support."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 25))
        self.text: str = config.get("text", "")
        self.size: int = config.get("size", 22)
        self.checked: bool = config.get("checked", config.get("value", False))
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (45, 48, 56))
        self.check_color: tuple = config.get("check_color", (80, 210, 120))
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self.border_color: tuple = config.get("border_color", (180, 185, 195))
        self.border: int = config.get("border", 2)
        self.spacing: int = config.get("spacing", 8)
        self.on_change = config.get("on_change", None)
        self._update_surfaces()

    def _update_surfaces(self) -> None:
        x, y = int(self.position[0]), int(self.position[1])
        self.box_rect = pygame.Rect(x, y, self.size, self.size)
        self._label_surface = self.font.render(self.text, True, self.color) if self.text else None
        self._label_hover_surface = self.font.render(self.text, True, self.hover_color) if self.text else None
        if self._label_surface:
            label_y = y + (self.size - self._label_surface.get_height()) // 2
            self.label_pos = (x + self.size + self.spacing, label_y)
            total_w = self.size + self.spacing + self._label_surface.get_width()
            total_h = max(self.size, self._label_surface.get_height())
            self.rect = pygame.Rect(x, min(y, label_y), total_w, total_h)
        else:
            self.label_pos = (x, y)
            self.rect = self.box_rect.copy()

    def move(self, dx: int, dy: int) -> None:
        super().move(dx, dy)
        self.box_rect.x += dx
        self.box_rect.y += dy
        self.label_pos = (self.label_pos[0] + dx, self.label_pos[1] + dy)

    def toggle(self) -> bool:
        self.set_checked(not self.checked)
        return self.checked

    def set_checked(self, value: bool) -> None:
        new_val = bool(value)
        if self.checked != new_val:
            self.checked = new_val
            if callable(self.on_change):
                self.on_change(self.checked)
            self.execute_commands(self.checked)

    def get_value(self) -> bool:
        return self.checked

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
        pygame.draw.rect(self.screen, self.color_back, self.box_rect, border_radius=4)
        pygame.draw.rect(self.screen, self.border_color, self.box_rect, self.border, border_radius=4)
        if self._label_surface:
            self.screen.blit(self._label_surface, self.label_pos)

        mouse_pos = self.get_mouse_pos()
        if self.detect_mouse:
            self.mouse_collision(self.rect, mouse_pos, self.draw_hover_effect)

        if self.checked:
            inner = self.box_rect.inflate(-6, -6)
            pygame.draw.rect(self.screen, self.check_color, inner, border_radius=2)

    def draw_hover_effect(self) -> None:
        pygame.draw.rect(self.screen, self.hover_color, self.box_rect, self.border, border_radius=4)
        if self._label_hover_surface:
            self.screen.blit(self._label_hover_surface, self.label_pos)

    def change_item(self, config: dict) -> None:
        self.position = config.get("position", self.position)
        self.text = config.get("text", self.text)
        self.checked = config.get("checked", self.checked)
        self.color = config.get("color", self.color)
        self.hover_color = config.get("hover_color", self.hover_color)
        self.detect_mouse = config.get("detect_mouse", self.detect_mouse)
        self.pressed = config.get("pressed", self.pressed)
        self._update_surfaces()

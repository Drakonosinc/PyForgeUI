import pygame
from ..Behavior.Element_behavior import ElementBehavior


class RadioGroup:
    """Controller managing mutually exclusive RadioButton instances."""

    def __init__(self, config: dict | None = None) -> None:
        config = config or {}
        self.buttons: list["RadioButton"] = []
        self.selected: "RadioButton | None" = None
        self.on_change = config.get("on_change", None)

    def add(self, button: "RadioButton") -> "RadioButton":
        if button not in self.buttons:
            self.buttons.append(button)
            button.group = self
            if button.selected or self.selected is None:
                self.select(button, trigger_callback=False)
        return button

    def select(self, target: "RadioButton", trigger_callback: bool = True) -> None:
        changed = self.selected is not target
        self.selected = target
        for btn in self.buttons:
            btn.selected = (btn is target)
        if changed and trigger_callback:
            if callable(self.on_change):
                self.on_change(self.get_value())

    def get_value(self):
        if self.selected is None:
            return None
        return self.selected.value if self.selected.value is not None else self.selected.text

    def events(self, event: pygame.event.Event) -> bool:
        for btn in self.buttons:
            if btn.events(event):
                return True
        return False

    def draw(self) -> None:
        for btn in self.buttons:
            btn.draw()


class RadioButton(ElementBehavior):
    """Single circular radio option button that can belong to a RadioGroup."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 25))
        self.text: str = config.get("text", "")
        self.value = config.get("value", self.text)
        self.radius: int = config.get("radius", 10)
        self.selected: bool = config.get("selected", False)
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (45, 48, 56))
        self.active_color: tuple = config.get("active_color", (85, 170, 255))
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self.border_color: tuple = config.get("border_color", (180, 185, 195))
        self.spacing: int = config.get("spacing", 8)
        self.group: RadioGroup | None = None
        self._update_surfaces()
        grp = config.get("group", None)
        if isinstance(grp, RadioGroup):
            grp.add(self)

    def _update_surfaces(self) -> None:
        x, y = int(self.position[0]), int(self.position[1])
        diameter = self.radius * 2
        self.circle_rect = pygame.Rect(x, y, diameter, diameter)
        self._label_surface = self.font.render(self.text, True, self.color) if self.text else None
        self._label_hover_surface = self.font.render(self.text, True, self.hover_color) if self.text else None
        if self._label_surface:
            label_y = y + (diameter - self._label_surface.get_height()) // 2
            self.label_pos = (x + diameter + self.spacing, label_y)
            total_w = diameter + self.spacing + self._label_surface.get_width()
            total_h = max(diameter, self._label_surface.get_height())
            self.rect = pygame.Rect(x, min(y, label_y), total_w, total_h)
        else:
            self.label_pos = (x, y)
            self.rect = self.circle_rect.copy()

    def move(self, dx: int, dy: int) -> None:
        super().move(dx, dy)
        self.circle_rect.x += dx
        self.circle_rect.y += dy
        self.label_pos = (self.label_pos[0] + dx, self.label_pos[1] + dy)

    def select(self) -> None:
        if self.group is not None:
            self.group.select(self, trigger_callback=True)
        else:
            self.selected = True
        self.execute_commands(self.value)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.sound_touch:
                    self.sound_touch.play(loops=0)
                self.select()
                return True
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        center = self.circle_rect.center
        pygame.draw.circle(self.screen, self.color_back, center, self.radius)
        pygame.draw.circle(self.screen, self.border_color, center, self.radius, 2)

        if self._label_surface:
            self.screen.blit(self._label_surface, self.label_pos)

        if self.detect_mouse:
            self.mouse_collision(self.rect, self.get_mouse_pos(), self.draw_hover_effect)

        if self.selected:
            pygame.draw.circle(self.screen, self.active_color, center, max(3, self.radius - 4))

    def draw_hover_effect(self) -> None:
        pygame.draw.circle(self.screen, self.hover_color, self.circle_rect.center, self.radius, 2)
        if self._label_hover_surface:
            self.screen.blit(self._label_hover_surface, self.label_pos)

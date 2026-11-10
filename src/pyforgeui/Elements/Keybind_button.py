import pygame
from ..Behavior.Element_behavior import ElementBehavior


class KeybindButton(ElementBehavior):
    """Control-mapping button that listens for the next key press when clicked."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 24))
        self.action_label: str = config.get("action_label", config.get("label", ""))
        self.key_code: int = config.get("key", pygame.K_SPACE)
        self.listening: bool = False
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (50, 55, 68))
        self.listening_color: tuple = config.get("listening_color", (215, 130, 40))
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self.border_color: tuple = config.get("border_color", (160, 165, 175))
        self.on_change = config.get("on_change", None)
        if len(self.position) >= 4:
            self.rect = pygame.Rect(*self.position[:4])
        else:
            self.rect = pygame.Rect(self.position[0], self.position[1], config.get("width", 180), config.get("height", 32))
        self._update_surfaces()

    def get_key_name(self) -> str:
        return pygame.key.name(self.key_code).upper()

    def _format_display(self) -> str:
        key_txt = "PRESS KEY..." if self.listening else f"[{self.get_key_name()}]"
        return f"{self.action_label}: {key_txt}" if self.action_label else key_txt

    def _update_surfaces(self) -> None:
        txt = self._format_display()
        self._text_surface = self.font.render(txt, True, self.color)
        self._hover_surface = self.font.render(txt, True, self.hover_color)

    def set_key(self, key_code: int) -> None:
        self.key_code = key_code
        self.listening = False
        self._update_surfaces()
        if callable(self.on_change):
            self.on_change(self.key_code)
        self.execute_commands(self.key_code)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if self.listening and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.listening = False
                self._update_surfaces()
            else:
                self.set_key(event.key)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.sound_touch:
                    self.sound_touch.play(loops=0)
                self.listening = not self.listening
                self._update_surfaces()
                return True
            elif self.listening:
                self.listening = False
                self._update_surfaces()
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        bg = self.listening_color if self.listening else self.color_back
        pygame.draw.rect(self.screen, bg, self.rect, border_radius=4)
        pygame.draw.rect(self.screen, self.border_color, self.rect, 2, border_radius=4)
        tx = self.rect.centerx - self._text_surface.get_width() // 2
        ty = self.rect.centery - self._text_surface.get_height() // 2
        self.screen.blit(self._text_surface, (tx, ty))
        if self.detect_mouse:
            self.mouse_collision(self.rect, self.get_mouse_pos(), self.draw_hover_effect)

    def draw_hover_effect(self) -> None:
        pygame.draw.rect(self.screen, self.hover_color, self.rect, 2, border_radius=4)

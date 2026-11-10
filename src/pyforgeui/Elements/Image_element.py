import pygame
from ..Behavior.Mouse_collision import MouseCollision
from ..Behavior.Element_behavior import ElementBehavior


class Image(MouseCollision):
    """Static or hoverable image/sprite element supporting surfaces, file paths, and scaling."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.size: tuple[int, int] | None = config.get("size", None)
        self.border_color: tuple | None = config.get("border_color", None)
        self.border: int = config.get("border", 0)
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self._raw_surface = self._load_surface(config.get("image", config.get("surface", None)))
        self._update_surfaces()

    def _load_surface(self, source) -> pygame.Surface:
        if isinstance(source, pygame.Surface):
            return source.convert_alpha() if pygame.display.get_init() and pygame.display.get_surface() else source.copy()
        if isinstance(source, str) and source:
            loaded = pygame.image.load(source)
            return loaded.convert_alpha() if pygame.display.get_init() and pygame.display.get_surface() else loaded
        # Fallback placeholder icon surface if no image path/surface provided
        w, h = self.size if self.size else (48, 48)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((70, 80, 100, 255))
        pygame.draw.rect(surf, (140, 160, 190), surf.get_rect(), 2)
        pygame.draw.line(surf, (140, 160, 190), (4, h - 8), (w // 2, h // 2), 2)
        pygame.draw.line(surf, (140, 160, 190), (w // 2, h // 2), (w - 4, h - 12), 2)
        return surf

    def _update_surfaces(self) -> None:
        if self.size:
            self.surface = pygame.transform.smoothscale(self._raw_surface, self.size)
        else:
            self.surface = self._raw_surface
        x, y = int(self.position[0]), int(self.position[1])
        self.rect = pygame.Rect(x, y, *self.surface.get_size())

    def draw(self) -> None:
        if not self.visible:
            return
        self.screen.blit(self.surface, self.position[:2])
        if self.border > 0 and self.border_color:
            pygame.draw.rect(self.screen, self.border_color, self.rect, self.border)
        if self.detect_mouse:
            self.mouse_collision(self.rect, self.get_mouse_pos(), self.draw_hover_effect)

    def draw_hover_effect(self) -> None:
        pygame.draw.rect(self.screen, self.hover_color, self.rect, max(2, self.border))

    def change_item(self, config: dict) -> None:
        if "image" in config or "surface" in config:
            self._raw_surface = self._load_surface(config.get("image", config.get("surface")))
        if "size" in config:
            self.size = config["size"]
        if "position" in config:
            self.position = config["position"]
        self._update_surfaces()


class ImageButton(Image, ElementBehavior):
    """Interactive image/sprite button supporting hover, click tint/border, and commands."""

    def __init__(self, config: dict) -> None:
        Image.__init__(self, config)
        ElementBehavior.__init__(self, config)
        self.pressed_color: tuple = config.get("pressed_color", (135, 206, 235))

    def draw(self) -> None:
        if not self.visible:
            return
        super().draw()
        if self.pressed:
            self.pressed_button(self.rect, pygame.mouse.get_pressed(), self.get_mouse_pos())

    def draw_pressed_effect(self) -> None:
        pygame.draw.rect(self.screen, self.pressed_color, self.rect, max(3, self.border + 1))

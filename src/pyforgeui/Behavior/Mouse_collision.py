import pygame


class MouseCollision:
    """Mixin/Base providing hover detection, coordinate translation, and spatial geometry."""

    def __init__(self, config: dict) -> None:
        self.screen: pygame.Surface = config["screen"]
        self.window = config.get("window", None)
        pos = config.get("position", (0, 0))
        self.position: tuple = tuple(pos) if isinstance(pos, (tuple, list)) else pos
        self.sound_hover = config.get("sound_hover", None)
        self.detect_mouse: bool = config.get("detect_mouse", True)
        self.visible: bool = config.get("visible", True)
        self.enabled: bool = config.get("enabled", True)
        self.tooltip_text: str | None = config.get("tooltip", None)
        if not hasattr(self, "states") or not isinstance(self.states, dict):
            self.states = {}
        self.states.update({"detect_hover": True, "is_hovered": False, **config.get("states", {})})

    def get_mouse_pos(self) -> tuple[int, int]:
        return self.window.get_mouse_pos() if self.window else pygame.mouse.get_pos()

    def get_bounding_rect(self) -> pygame.Rect:
        """Returns a single bounding pygame.Rect for layout and container calculations."""
        rect_attr = getattr(self, "rect", None)
        if isinstance(rect_attr, pygame.Rect):
            return rect_attr
        if isinstance(rect_attr, dict):
            rects = []
            for v in rect_attr.values():
                if isinstance(v, pygame.Rect):
                    rects.append(v)
                elif hasattr(v, "get_bounding_rect"):
                    rects.append(v.get_bounding_rect())
                elif hasattr(v, "rect") and isinstance(v.rect, pygame.Rect):
                    rects.append(v.rect)
            if rects:
                base = rects[0].copy()
                for r in rects[1:]:
                    base.union_ip(r)
                return base
        if isinstance(self.position, (tuple, list)):
            if len(self.position) >= 4 and isinstance(self.position[0], (int, float)):
                return pygame.Rect(int(self.position[0]), int(self.position[1]), int(self.position[2]), int(self.position[3]))
            if len(self.position) == 2 and isinstance(self.position[0], (int, float)):
                return pygame.Rect(int(self.position[0]), int(self.position[1]), 0, 0)
        return pygame.Rect(0, 0, 0, 0)

    def move(self, dx: int, dy: int) -> None:
        """Translates this element and any nested rects/children by (dx, dy)."""
        if dx == 0 and dy == 0:
            return
        if isinstance(self.position, (tuple, list)) and self.position:
            if isinstance(self.position[0], (tuple, list)):
                # Polygon points
                self.position = [(p[0] + dx, p[1] + dy) for p in self.position]
                if hasattr(self, "hover_position") and isinstance(self.hover_position, (tuple, list)):
                    self.hover_position = [(p[0] + dx, p[1] + dy) for p in self.hover_position]
            elif len(self.position) == 2:
                self.position = (self.position[0] + dx, self.position[1] + dy)
            elif len(self.position) >= 4:
                self.position = (self.position[0] + dx, self.position[1] + dy, *self.position[2:])

        self._translate_rect_obj(getattr(self, "rect", None), dx, dy)

    @classmethod
    def _translate_rect_obj(cls, obj, dx: int, dy: int) -> None:
        if isinstance(obj, pygame.Rect):
            obj.x += dx
            obj.y += dy
        elif isinstance(obj, dict):
            for v in obj.values():
                if isinstance(v, (pygame.Rect, dict)):
                    cls._translate_rect_obj(v, dx, dy)
                elif hasattr(v, "move"):
                    v.move(dx, dy)

    def set_position(self, x: int, y: int) -> None:
        """Moves the element so its top-left corner is at (x, y)."""
        if isinstance(self.position, (tuple, list)) and self.position and isinstance(self.position[0], (int, float)):
            dx = int(x - self.position[0])
            dy = int(y - self.position[1])
        else:
            bounds = self.get_bounding_rect()
            dx = int(x - bounds.x)
            dy = int(y - bounds.y)
        self.move(dx, dy)

    def mouse_collision(self, rect: pygame.Rect, mouse_pos: tuple[int, int], draw=None) -> bool:
        if not self.visible or not self.enabled:
            self.states["is_hovered"] = False
            return False
        if rect.collidepoint(mouse_pos):
            self.states["is_hovered"] = True
            self.draw_hover_effect() if draw is None else draw()
            if self.states["detect_hover"]:
                if self.sound_hover:
                    self.sound_hover.play(loops=0)
                self.states["detect_hover"] = False
            return True
        else:
            self.states["is_hovered"] = False
            self.states["detect_hover"] = True
            return False

    def draw_hover_effect(self):
        raise NotImplementedError

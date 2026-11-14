import pygame


class MouseCollision:
    """Mixin/Base providing hover detection, coordinate translation, and spatial geometry."""

    _active_popup = None
    _popup_block_until_release: bool = False
    _popup_closed_tick: int = -1000
    _popup_closed_rect: pygame.Rect | None = None

    @classmethod
    def set_active_popup(cls, popup) -> None:
        if cls._active_popup is not None and cls._active_popup is not popup:
            prev = cls._active_popup
            cls._active_popup = None
            if getattr(prev, "is_dropdown_open", False):
                prev.close_dropdown(block_click=False)
        cls._active_popup = popup

    @classmethod
    def clear_active_popup(cls, popup=None, block_click: bool = False) -> None:
        target = popup if popup is not None else cls._active_popup
        if target is not None and hasattr(target, "get_total_interactive_rect"):
            try:
                cls._popup_closed_rect = target.get_total_interactive_rect()
            except Exception:
                cls._popup_closed_rect = None
        if popup is None or cls._active_popup is popup:
            cls._active_popup = None
        if block_click:
            cls._popup_block_until_release = True
            try:
                cls._popup_closed_tick = pygame.time.get_ticks()
            except Exception:
                cls._popup_closed_tick = 0

    @classmethod
    def get_active_popup(cls):
        popup = cls._active_popup
        if popup is not None:
            if not getattr(popup, "is_dropdown_open", False) or not getattr(popup, "visible", True):
                cls._active_popup = None
                return None
            last_tick = getattr(popup, "_last_draw_tick", None)
            if last_tick is not None:
                try:
                    if (pygame.time.get_ticks() - last_tick) > 250:
                        popup._is_dropdown_open = False
                        cls._active_popup = None
                        return None
                except Exception:
                    pass
        return popup

    def _is_visual_occluded_by_popup(self, check_rect: pygame.Rect | None = None) -> bool:
        popup = MouseCollision.get_active_popup()
        owner = getattr(self, "_owner_popup", None)
        if popup is None or owner is popup or self is popup:
            return False
        if getattr(self, "screen", None) is not getattr(popup, "screen", None):
            return False
        overlay_rect = popup.get_dropdown_overlay_rect() if hasattr(popup, "get_dropdown_overlay_rect") else None
        if not isinstance(overlay_rect, pygame.Rect):
            return False
        rect_to_check = check_rect if isinstance(check_rect, pygame.Rect) else self.get_bounding_rect()
        if isinstance(rect_to_check, pygame.Rect) and rect_to_check.width > 0 and rect_to_check.height > 0:
            return overlay_rect.colliderect(rect_to_check)
        return False

    def _is_occluded_by_popup(self, check_rect: pygame.Rect | None = None, mouse_pos: tuple[int, int] | None = None) -> bool:
        try:
            pressed = pygame.mouse.get_pressed()[0]
            now = pygame.time.get_ticks()
        except Exception:
            pressed = False
            now = 0

        if not pressed and MouseCollision._popup_block_until_release and (now - MouseCollision._popup_closed_tick) > 45:
            MouseCollision._popup_block_until_release = False

        popup = MouseCollision.get_active_popup()
        owner = getattr(self, "_owner_popup", None)
        is_owned_by_active = (popup is not None) and (owner is popup or self is popup)

        if not is_owned_by_active and isinstance(MouseCollision._popup_closed_rect, pygame.Rect):
            if MouseCollision._popup_block_until_release or (now - MouseCollision._popup_closed_tick) <= 45:
                if mouse_pos is not None and MouseCollision._popup_closed_rect.collidepoint(mouse_pos):
                    return True
                rect_to_check = check_rect if isinstance(check_rect, pygame.Rect) else self.get_bounding_rect()
                if isinstance(rect_to_check, pygame.Rect) and MouseCollision._popup_closed_rect.colliderect(rect_to_check):
                    return True

        if popup is None or is_owned_by_active:
            vp = getattr(self, "_scroll_viewport", None)
            if isinstance(vp, pygame.Rect):
                if mouse_pos is not None and not vp.collidepoint(mouse_pos):
                    return True
                rect_to_check = check_rect if isinstance(check_rect, pygame.Rect) else self.get_bounding_rect()
                if isinstance(rect_to_check, pygame.Rect) and (rect_to_check.top < vp.top or rect_to_check.bottom > vp.bottom):
                    return True
            return False
        if getattr(self, "screen", None) is not getattr(popup, "screen", None):
            return False

        overlay_rect = popup.get_dropdown_overlay_rect() if hasattr(popup, "get_dropdown_overlay_rect") else None
        if isinstance(overlay_rect, pygame.Rect):
            if mouse_pos is not None and overlay_rect.collidepoint(mouse_pos):
                return True
            rect_to_check = check_rect if isinstance(check_rect, pygame.Rect) else self.get_bounding_rect()
            if isinstance(rect_to_check, pygame.Rect) and rect_to_check.width > 0 and rect_to_check.height > 0:
                if overlay_rect.colliderect(rect_to_check):
                    return True
        return False

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
        if not self.visible or not self.enabled or self._is_occluded_by_popup(rect, mouse_pos):
            self.states["is_hovered"] = False
            self.states["detect_hover"] = True
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

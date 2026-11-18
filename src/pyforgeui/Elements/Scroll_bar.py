import pygame
from ..Behavior.Element_behavior import ElementBehavior
from ..VisualFX import RetroVisualFX


class ScrollBar(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        rect = pygame.Rect(*self.position)
        self.type_of_orientation = config.get("type_of_orientation", "vertical").lower()
        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.color = config.get("color", (200, 200, 200))
        self.color_thumb = config.get("color_bar", (56, 189, 248))
        self.modern_style: bool = config.get("modern_style", True)
        self.wheel_step = config.get("wheel_step", 18)
        self.scroll_area: pygame.Rect | None = config.get("scroll_area", None)
        if self.type_of_orientation == "vertical":
            self.thumb_size = config.get("thumb_height", max(24, int(self.position[3] * config.get("thumb_ratio", 0.2))))
            self.thumb_rect = pygame.Rect(rect.x, rect.y, rect.width, self.thumb_size)
            self.content_size = rect.height
        else:
            self.thumb_size = config.get("thumb_width", max(24, int(self.position[2] * config.get("thumb_ratio", 0.2))))
            self.thumb_rect = pygame.Rect(rect.x, rect.y, self.thumb_size, rect.height)
            self.content_size = rect.width
        self.elements = None
        self.initial_positions = []
        self.dragging = False
        self.drag_offset = 0
        self._hover_anim: float = 0.0
        self.rect = {"rect": rect, "thumb": self.thumb_rect}

    def move(self, dx: int, dy: int) -> None:
        if dx == 0 and dy == 0:
            return
        super().move(dx, dy)
        if isinstance(self.scroll_area, pygame.Rect):
            self.scroll_area.move_ip(dx, dy)
        if self.initial_positions:
            self.initial_positions = [(x + dx, y + dy) for (x, y) in self.initial_positions]

    def _get_wheel_hit_rect(self) -> pygame.Rect:
        hit = self.rect["rect"].copy()
        if isinstance(self.scroll_area, pygame.Rect):
            hit.union_ip(self.scroll_area)
        if self.elements and self.initial_positions:
            min_x = min(x for x, _ in self.initial_positions)
            min_y = min(y for _, y in self.initial_positions)
            content_rect = pygame.Rect(min_x, min_y, max(hit.right - min_x, 100), max(hit.height, 40))
            hit.union_ip(content_rect)
        return hit

    def _step_thumb(self, delta_pixels: int) -> None:
        if self.type_of_orientation == "vertical":
            new_pos = self.thumb_rect.y + delta_pixels
            new_pos = max(self.rect["rect"].top, min(new_pos, self.rect["rect"].bottom - self.thumb_size))
            self.thumb_rect.y = new_pos
        else:
            new_pos = self.thumb_rect.x + delta_pixels
            new_pos = max(self.rect["rect"].left, min(new_pos, self.rect["rect"].right - self.thumb_size))
            self.thumb_rect.x = new_pos
        self.scroll_elements()

    def events(self, event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = self.get_mouse_pos()
            if self._get_wheel_hit_rect().collidepoint(mouse_pos):
                direction = -event.y if event.y != 0 else event.x
                if direction != 0:
                    self._step_thumb(int(direction * self.wheel_step))
                    return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5):
                if self._get_wheel_hit_rect().collidepoint(event.pos):
                    direction = -1 if event.button == 4 else 1
                    self._step_thumb(direction * self.wheel_step)
                    return True
            elif event.button == 1:
                if self.thumb_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = (
                        (event.pos[1] - self.thumb_rect.y)
                        if self.type_of_orientation == "vertical"
                        else (event.pos[0] - self.thumb_rect.x)
                    )
                    return True
                elif self.rect["rect"].collidepoint(event.pos):
                    if self.type_of_orientation == "vertical":
                        target = event.pos[1] - self.thumb_size // 2
                        self.thumb_rect.y = max(self.rect["rect"].top, min(target, self.rect["rect"].bottom - self.thumb_size))
                    else:
                        target = event.pos[0] - self.thumb_size // 2
                        self.thumb_rect.x = max(self.rect["rect"].left, min(target, self.rect["rect"].right - self.thumb_size))
                    self.scroll_elements()
                    return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            if self.type_of_orientation == "vertical":
                new_pos = event.pos[1] - self.drag_offset
                new_pos = max(self.rect["rect"].top, min(new_pos, self.rect["rect"].bottom - self.thumb_size))
                self.thumb_rect.y = new_pos
            else:
                new_pos = event.pos[0] - self.drag_offset
                new_pos = max(self.rect["rect"].left, min(new_pos, self.rect["rect"].right - self.thumb_size))
                self.thumb_rect.x = new_pos
            self.scroll_elements()
            return True
        return False

    def scroll_elements(self):
        if not self.elements:
            return
        max_scroll = self.content_size
        if max_scroll <= 0:
            proportion = 0.0
        else:
            if self.type_of_orientation == "vertical":
                denom = self.rect["rect"].height - self.thumb_size
                proportion = (self.thumb_rect.y - self.rect["rect"].y) / denom if denom > 0 else 0.0
            else:
                denom = self.rect["rect"].width - self.thumb_size
                proportion = (self.thumb_rect.x - self.rect["rect"].x) / denom if denom > 0 else 0.0
        offset = int(proportion * max_scroll)
        for el, (x0, y0) in zip(self.elements, self.initial_positions):
            if self.type_of_orientation == "vertical":
                old_pos = el.position[1]
                new_pos = y0 - offset
                el.position = (x0, new_pos)
            else:
                old_pos = el.position[0]
                new_pos = x0 - offset
                el.position = (new_pos, y0)
            delta = new_pos - old_pos

            def add_delta(item, d):
                if isinstance(item, pygame.Rect):
                    if self.type_of_orientation == "vertical":
                        item.y += d
                    else:
                        item.x += d
                elif isinstance(item, dict):
                    for v in item.values():
                        add_delta(v, d)
                elif hasattr(item, "rect") and hasattr(item, "position"):
                    add_delta(item.rect, d)
                    if self.type_of_orientation == "vertical":
                        item.position = (item.position[0], item.position[1] + d)
                    else:
                        item.position = (item.position[0] + d, item.position[1])

            if isinstance(el.rect, dict):
                for key in el.rect:
                    add_delta(el.rect[key], delta)
            else:
                add_delta(el.rect, delta)
            if hasattr(el, "scroll") and isinstance(el.scroll, ScrollBar) and el.scroll.elements:
                el.scroll.initial_positions = [(sub_el.position[0], sub_el.position[1]) for sub_el in el.scroll.elements]
        if callable(self.commands):
            self.commands(proportion)

    def get_viewport_rect(self) -> pygame.Rect | None:
        if not self.initial_positions or not self.screen:
            return None
        scr_w, scr_h = self.screen.get_size()
        if isinstance(self.scroll_area, pygame.Rect):
            if self.type_of_orientation == "vertical":
                return pygame.Rect(0, self.scroll_area.top, scr_w, self.scroll_area.height)
            return pygame.Rect(self.scroll_area.left, 0, self.scroll_area.width, scr_h)
        if self.type_of_orientation == "vertical":
            top = int(min(y for _, y in self.initial_positions)) - 2
            return pygame.Rect(0, top, scr_w, max(1, scr_h - top))
        else:
            left = int(min(x for x, _ in self.initial_positions)) - 2
            return pygame.Rect(left, 0, max(1, scr_w - left), scr_h)

    def draw(self):
        track = self.rect["rect"]
        thumb = self.thumb_rect
        mouse_pos = self.get_mouse_pos()

        if self.modern_style:
            is_hovered = (
                self.dragging
                or (
                    self.detect_mouse
                    and not self._is_occluded_by_popup(thumb, mouse_pos)
                    and thumb.collidepoint(mouse_pos)
                )
            )
            target = 1.0 if is_hovered else 0.0
            if abs(self._hover_anim - target) > 0.01:
                self._hover_anim += (target - self._hover_anim) * 0.3
            else:
                self._hover_anim = target

            rad = max(4, min(track.width, track.height) // 2)
            # Recessed dark-glass track
            track_surf = pygame.Surface((track.width, track.height), pygame.SRCALPHA)
            pygame.draw.rect(track_surf, (10, 16, 32, 210), track_surf.get_rect(), border_radius=rad)
            pygame.draw.rect(track_surf, (45, 78, 125, 165), track_surf.get_rect(), 1, border_radius=rad)
            self.screen.blit(track_surf, track.topleft)

            # Glowing pill thumb
            base_c = RetroVisualFX.normalize_color(self.color_thumb)
            hov_c = RetroVisualFX.normalize_color(self.hover_color)
            thumb_c = RetroVisualFX.lerp_color(base_c, hov_c, self._hover_anim)

            pad = 4
            t_surf = pygame.Surface((thumb.width + pad * 2, thumb.height + pad * 2), pygame.SRCALPHA)
            local_t = pygame.Rect(pad, pad, thumb.width, thumb.height)
            if self._hover_anim > 0.02:
                pygame.draw.rect(t_surf, (*thumb_c, int(85 * self._hover_anim)), local_t.inflate(4, 4), border_radius=rad + 2)
            pygame.draw.rect(t_surf, (*thumb_c, 235), local_t.inflate(-2, -2), border_radius=rad)
            pygame.draw.rect(t_surf, (*RetroVisualFX.brighten(thumb_c, 45), 255), local_t.inflate(-2, -2), 1, border_radius=rad)

            # Grip lines in center of thumb
            cx, cy = local_t.centerx, local_t.centery
            if self.type_of_orientation == "vertical" and thumb.height >= 16:
                for dy in (-3, 0, 3):
                    pygame.draw.line(t_surf, (10, 16, 32, 190), (cx - 4, cy + dy), (cx + 4, cy + dy), 1)
            elif self.type_of_orientation != "vertical" and thumb.width >= 16:
                for dx in (-3, 0, 3):
                    pygame.draw.line(t_surf, (10, 16, 32, 190), (cx + dx, cy - 4), (cx + dx, cy + 4), 1)

            self.screen.blit(t_surf, (thumb.x - pad, thumb.y - pad))
        else:
            pygame.draw.rect(self.screen, self.color, track)
            pygame.draw.rect(self.screen, self.color_thumb, thumb)

        if self.detect_mouse:
            self.mouse_collision(thumb, mouse_pos)
        if self.pressed:
            self.pressed_button(thumb, pygame.mouse.get_pressed(), mouse_pos)

    def draw_hover_effect(self):
        if self.modern_style:
            return self.thumb_rect
        return pygame.draw.rect(self.screen, self.hover_color, self.thumb_rect)

    def update_elements(self, elements: list):
        if self.elements == elements and self.initial_positions and len(self.initial_positions) == len(elements):
            return
        self.elements = elements
        self.initial_positions = [(el.position[0], el.position[1]) for el in self.elements]
        if self.elements:
            if self.type_of_orientation == "vertical":
                start_pos = min(y for _, y in self.initial_positions)
                end_pos = self.return_rect()
                visible_span = self.rect["rect"].height
            else:
                start_pos = min(x for x, _ in self.initial_positions)
                end_pos = self.return_rect()
                visible_span = self.rect["rect"].width
            self.content_size = max(0, (end_pos - start_pos) - visible_span + 24)
            vp = self.get_viewport_rect()
            for el in self.elements:
                if getattr(el, "_owner_popup", None) is None:
                    el._scroll_viewport = vp
        else:
            self.content_size = 0

    def return_rect(self):
        def get_bound(val):
            if isinstance(val, pygame.Rect):
                return val.bottom if self.type_of_orientation == "vertical" else val.right
            elif isinstance(val, dict):
                return max(get_bound(v) for v in val.values() if isinstance(v, (pygame.Rect, dict)))
            elif hasattr(val, "rect"):
                return get_bound(val.rect)
            return 0

        max_bound = 0
        if self.elements:
            for el in self.elements:
                rect = getattr(el, "rect", None)
                if isinstance(rect, dict):
                    for v in rect.values():
                        max_bound = max(max_bound, get_bound(v))
                else:
                    max_bound = max(max_bound, get_bound(rect))
        return max_bound

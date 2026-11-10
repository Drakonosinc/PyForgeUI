import pygame
from ..Behavior.Element_behavior import ElementBehavior


class TabContainer(ElementBehavior):
    """Tabbed container switching between named pages of child widgets."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 24))
        self.tab_height: int = config.get("tab_height", 32)
        self.color: tuple = config.get("color", (255, 255, 255))
        self.color_back: tuple = config.get("color_back", (34, 38, 46))
        self.tab_color: tuple = config.get("tab_color", (50, 56, 68))
        self.active_tab_color: tuple = config.get("active_tab_color", (75, 135, 215))
        self.hover_color: tuple = config.get("hover_color", (255, 199, 51))
        self.border_color: tuple = config.get("border_color", (110, 120, 140))
        self.border: int = config.get("border", 2)

        if len(self.position) >= 4:
            self.rect = pygame.Rect(*self.position[:4])
        else:
            self.rect = pygame.Rect(self.position[0], self.position[1], config.get("width", 400), config.get("height", 260))

        self.tabs: dict[str, list] = {}
        self.tab_rects: dict[str, pygame.Rect] = {}
        self._tab_surfaces: dict[str, pygame.Surface] = {}
        self.active_tab: str | None = None

        for tab_name in config.get("tabs", []):
            self.add_tab(tab_name)

    def add_tab(self, name: str, children: list | None = None) -> None:
        if name not in self.tabs:
            self.tabs[name] = list(children) if children else []
            if self.active_tab is None:
                self.active_tab = name
            self._rebuild_tab_headers()

    def add_to_tab(self, tab_name: str, widget, relative_pos: tuple[int, int] | None = None):
        if tab_name not in self.tabs:
            self.add_tab(tab_name)
        if relative_pos is not None and hasattr(widget, "set_position"):
            widget.set_position(self.rect.x + relative_pos[0], self.rect.y + self.tab_height + relative_pos[1])
        self.tabs[tab_name].append(widget)
        return widget

    def select_tab(self, name: str) -> None:
        if name in self.tabs:
            self.active_tab = name
            self.execute_commands(name)

    def _rebuild_tab_headers(self) -> None:
        self.tab_rects.clear()
        self._tab_surfaces.clear()
        x_cursor = self.rect.x
        for name in self.tabs:
            surf = self.font.render(name, True, self.color)
            w = max(80, surf.get_width() + 24)
            self.tab_rects[name] = pygame.Rect(x_cursor, self.rect.y, w, self.tab_height)
            self._tab_surfaces[name] = surf
            x_cursor += w + 4

    def move(self, dx: int, dy: int) -> None:
        if dx == 0 and dy == 0:
            return
        super().move(dx, dy)
        for r in self.tab_rects.values():
            r.move_ip(dx, dy)
        for widget_list in self.tabs.values():
            for w in widget_list:
                if hasattr(w, "move"):
                    w.move(dx, dy)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, trect in self.tab_rects.items():
                if trect.collidepoint(event.pos):
                    if self.sound_touch:
                        self.sound_touch.play(loops=0)
                    self.select_tab(name)
                    return True
        if self.active_tab and self.active_tab in self.tabs:
            for widget in reversed(self.tabs[self.active_tab]):
                if hasattr(widget, "events") and widget.events(event):
                    return True
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        body_rect = pygame.Rect(self.rect.x, self.rect.y + self.tab_height, self.rect.width, max(0, self.rect.height - self.tab_height))
        pygame.draw.rect(self.screen, self.color_back, body_rect, border_bottom_left_radius=6, border_bottom_right_radius=6, border_top_right_radius=6)
        pygame.draw.rect(self.screen, self.border_color, body_rect, self.border, border_bottom_left_radius=6, border_bottom_right_radius=6, border_top_right_radius=6)

        mouse_pos = self.get_mouse_pos()
        for name, trect in self.tab_rects.items():
            bg = self.active_tab_color if name == self.active_tab else self.tab_color
            pygame.draw.rect(self.screen, bg, trect, border_top_left_radius=6, border_top_right_radius=6)
            if self.detect_mouse and trect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, self.hover_color, trect, 2, border_top_left_radius=6, border_top_right_radius=6)
            else:
                pygame.draw.rect(self.screen, self.border_color, trect, 1, border_top_left_radius=6, border_top_right_radius=6)
            surf = self._tab_surfaces[name]
            self.screen.blit(surf, (trect.centerx - surf.get_width() // 2, trect.centery - surf.get_height() // 2))

        if self.active_tab and self.active_tab in self.tabs:
            for widget in self.tabs[self.active_tab]:
                if getattr(widget, "visible", True) and hasattr(widget, "draw"):
                    widget.draw()


    def draw_hover_effect(self) -> None:
        pass

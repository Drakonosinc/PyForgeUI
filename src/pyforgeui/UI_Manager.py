import pygame
from .Elements.Tooltip import Tooltip


class UIManager:
    """High-level UI orchestrator handling Z-order rendering, modal input blocking, and automatic tooltips."""

    def __init__(self, config: dict) -> None:
        self.screen: pygame.Surface = config["screen"]
        self.window = config.get("window", None)
        self.font: pygame.font.Font = config.get("font", pygame.font.Font(None, 20))
        self.widgets: list = []
        self.modals: list = []
        self.shared_tooltip = Tooltip({
            "screen": self.screen,
            "window": self.window,
            "font": self.font,
            "delay_ms": config.get("tooltip_delay_ms", 350),
        })
        self._hovered_widget = None
        self._hover_start_ticks: int | None = None

    def add(self, *widgets):
        for w in widgets:
            if w.__class__.__name__ in ("Modal", "DialogBox"):
                if w not in self.modals:
                    self.modals.append(w)
            else:
                if w not in self.widgets:
                    self.widgets.append(w)
        return widgets[0] if len(widgets) == 1 else widgets

    def remove(self, widget) -> None:
        if widget in self.widgets:
            self.widgets.remove(widget)
        if widget in self.modals:
            self.modals.remove(widget)

    def clear(self) -> None:
        self.widgets.clear()
        self.modals.clear()

    def events(self, event: pygame.event.Event) -> bool:
        for modal in reversed(self.modals):
            if getattr(modal, "visible", False):
                if modal.events(event):
                    return True
        for widget in reversed(self.widgets):
            if getattr(widget, "visible", True) and hasattr(widget, "events"):
                if hasattr(widget, "reactivate_pressed"):
                    widget.reactivate_pressed(event)
                if widget.events(event):
                    return True
        return False

    def _iter_visible_candidates(self, container_list):
        for item in reversed(container_list):
            if not getattr(item, "visible", True):
                continue
            if hasattr(item, "tabs") and getattr(item, "active_tab", None) in item.tabs:
                yield from self._iter_visible_candidates(item.tabs[item.active_tab])
            if hasattr(item, "children"):
                yield from self._iter_visible_candidates(item.children)
            yield item

    def _find_tooltip_target(self, mouse_pos: tuple[int, int]):
        for modal in reversed(self.modals):
            if getattr(modal, "visible", False):
                for item in self._iter_visible_candidates(getattr(modal, "children", [])):
                    if getattr(item, "tooltip_text", None):
                        bounds = item.get_bounding_rect() if hasattr(item, "get_bounding_rect") else getattr(item, "rect", None)
                        if isinstance(bounds, pygame.Rect) and bounds.collidepoint(mouse_pos):
                            return item
                return None

        for item in self._iter_visible_candidates(self.widgets):
            if getattr(item, "tooltip_text", None):
                bounds = item.get_bounding_rect() if hasattr(item, "get_bounding_rect") else getattr(item, "rect", None)
                if isinstance(bounds, pygame.Rect) and bounds.collidepoint(mouse_pos):
                    return item
        return None


    def draw(self) -> None:
        for widget in self.widgets:
            if getattr(widget, "visible", True) and hasattr(widget, "draw"):
                widget.draw()

        for modal in self.modals:
            if getattr(modal, "visible", False) and hasattr(modal, "draw"):
                modal.draw()

        mouse_pos = self.window.get_mouse_pos() if self.window else pygame.mouse.get_pos()
        target = self._find_tooltip_target(mouse_pos)
        if target is not None:
            now = pygame.time.get_ticks()
            if self._hovered_widget is not target:
                self._hovered_widget = target
                self._hover_start_ticks = now
            elif self._hover_start_ticks is not None and (now - self._hover_start_ticks) >= self.shared_tooltip.delay_ms:
                self.shared_tooltip.draw_at(mouse_pos, target.tooltip_text)
        else:
            self._hovered_widget = None
            self._hover_start_ticks = None

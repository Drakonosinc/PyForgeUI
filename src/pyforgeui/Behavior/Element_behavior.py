import pygame
from pygame.locals import *
from .Mouse_collision import MouseCollision
from .Pressed_button import PressedButton


class ElementBehavior(MouseCollision, PressedButton):
    """Unified base behavior for all interactive PyForgeUI widgets."""

    _timer_initialized = False

    def __init__(self, config: dict) -> None:
        MouseCollision.__init__(self, config)
        PressedButton.__init__(self, config)
        self.new_events(time=config.get("time", 500))

    def events(self, event: pygame.event.Event) -> bool:
        """Process a Pygame event. Returns True if the event was consumed by this widget."""
        return False

    def reactivate_pressed(self, event: pygame.event.Event) -> None:
        if event.type == self.EVENT_NEW:
            self.states["presses_touch"] = True

    def new_events(self, time: int) -> None:
        self.EVENT_NEW = pygame.USEREVENT + self.define_event()
        if not ElementBehavior._timer_initialized or time != 500:
            pygame.time.set_timer(self.EVENT_NEW, time)
            ElementBehavior._timer_initialized = True

    def define_event(self) -> int:
        return 1

    def filter_rects_collision(self, rects: dict, mouse_pos: tuple[int, int], draws: list, option: bool = False) -> None:
        for rect, draw in zip(rects, draws):
            if rects[rect].collidepoint(mouse_pos):
                if option is True:
                    self.pressed_button(rects[rect], pygame.mouse.get_pressed(), mouse_pos, draw)
                else:
                    self.mouse_collision(rects[rect], mouse_pos, draw)
            if all(not rects[r].collidepoint(mouse_pos) for r in rects):
                self.states["detect_hover"], self.states["presses_touch"] = True, True

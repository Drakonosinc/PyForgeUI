import pygame
from .Panel import Panel


class Modal(Panel):
    """Modal dialog box with backdrop dimming, input blocking, message text, and action buttons."""

    def __init__(self, config: dict) -> None:
        screen_w, screen_h = config["screen"].get_size()
        w = config.get("width", 360)
        h = config.get("height", 180)
        if "position" not in config:
            config["position"] = ((screen_w - w) // 2, (screen_h - h) // 2, w, h)
        config.setdefault("visible", False)
        config.setdefault("draggable", True)
        super().__init__(config)
        self.message: str = config.get("message", "")
        self.overlay_alpha: int = config.get("overlay_alpha", 150)
        self.block_background: bool = config.get("block_background", True)
        self.on_confirm = config.get("on_confirm", None)
        self.on_cancel = config.get("on_cancel", None)

        from ..Elements_Factory import ElementsFactory
        self.factory = ElementsFactory({
            "screen": self.screen,
            "window": self.window,
            "font": self.font,
            "color": self.color,
            "hover_color": config.get("hover_color", (255, 199, 51)),
            "sound_hover": self.sound_hover,
            "sound_touch": self.sound_touch,
        })

        self._overlay_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self._overlay_surface.fill((0, 0, 0, self.overlay_alpha))
        self._msg_surfaces = [self.font.render(line, True, self.color) for line in self.message.split("\n")] if self.message else []

        confirm_text = config.get("confirm_text", "OK")
        cancel_text = config.get("cancel_text", "Cancel")
        btn_y = self.rect.bottom - 38
        if confirm_text:
            self.confirm_button = self.factory.create_TextButton({
                "position": (self.rect.centerx - 70 if cancel_text else self.rect.centerx - 20, btn_y),
                "text": confirm_text,
                "command1": self._handle_confirm,
            })
            self.add_child(self.confirm_button)
        if cancel_text:
            self.cancel_button = self.factory.create_TextButton({
                "position": (self.rect.centerx + 25, btn_y),
                "text": cancel_text,
                "command1": self._handle_cancel,
            })
            self.add_child(self.cancel_button)

    def _handle_confirm(self) -> None:
        self.close()
        if callable(self.on_confirm):
            self.on_confirm()

    def _handle_cancel(self) -> None:
        self.close()
        if callable(self.on_cancel):
            self.on_cancel()

    def open(self) -> None:
        self.visible = True

    def close(self) -> None:
        self.visible = False

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for child in self.children:
                bounds = child.get_bounding_rect() if hasattr(child, "get_bounding_rect") else getattr(child, "rect", None)
                if isinstance(bounds, pygame.Rect) and bounds.collidepoint(event.pos):
                    if hasattr(child, "execute_commands"):
                        if getattr(child, "sound_touch", None):
                            child.sound_touch.play(loops=0)
                        child.execute_commands()
                        return True
        super().events(event)
        return self.block_background

    def draw(self) -> None:
        if not self.visible:
            return
        if self._overlay_surface.get_size() != self.screen.get_size():
            self._overlay_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            self._overlay_surface.fill((0, 0, 0, self.overlay_alpha))
        self.screen.blit(self._overlay_surface, (0, 0))
        super().draw()
        y_cursor = self.rect.y + self.header_height + 20
        for surf in self._msg_surfaces:
            tx = self.rect.centerx - surf.get_width() // 2
            self.screen.blit(surf, (tx, y_cursor))
            y_cursor += surf.get_height() + 4


DialogBox = Modal

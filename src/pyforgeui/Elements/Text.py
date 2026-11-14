import pygame
from ..Behavior.Mouse_collision import MouseCollision
from ..VisualFX import RetroVisualFX


class Text(MouseCollision):
    def __init__(self, config: dict):
        MouseCollision.__init__(self, config)
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text", "")
        self.color = config.get("color", (255, 255, 255))
        self.hover_color = config.get("hover_color", config.get("color2", (255, 199, 51)))
        self.modern_style: bool = config.get("modern_style", True)
        self.shadow: bool = config.get("shadow", True)
        self.glow: bool = config.get("glow", False)
        self.hover_glow: bool = config.get("hover_glow", True)
        self.highlight_second_line: bool = config.get("highlight_second_line", ("\n" in str(self.text) and not self.detect_mouse))
        self._pad = (0, 0)
        self._hover_pad = (0, 0)
        self._ink_rel = pygame.Rect(0, 0, 0, 0)
        self._update_surfaces()

    def _update_surfaces(self):
        if self.modern_style:
            has_multiline_val = "\n" in str(self.text) and not self.detect_mouse
            is_accent_color = RetroVisualFX.normalize_color(self.color) in ((135, 206, 235), (56, 189, 248), (255, 199, 51), (255, 0, 0))
            self._text_surface, self._pad, (bw, bh), self._ink_rel = RetroVisualFX.render_text_styled(
                self.font,
                str(self.text),
                self.color,
                shadow=self.shadow,
                glow=self.glow or is_accent_color,
                glow_color=self.color,
                glow_radius=3,
                highlight_second_line=has_multiline_val,
            )
            self._hover_surface, self._hover_pad, _, _ = RetroVisualFX.render_text_styled(
                self.font,
                str(self.text),
                self.hover_color,
                shadow=self.shadow,
                glow=self.hover_glow,
                glow_color=self.hover_color,
                glow_radius=4,
                highlight_second_line=has_multiline_val,
            )
            self.rect = pygame.Rect(int(self.position[0]), int(self.position[1]), bw, bh)
        else:
            self._text_surface = self.font.render(self.text, True, self.color)
            self._hover_surface = self.font.render(self.text, True, self.hover_color)
            self._pad = (0, 0)
            self._hover_pad = (0, 0)
            self._ink_rel = self._text_surface.get_bounding_rect()
            self.rect = pygame.Rect(*self.position, *self._text_surface.get_size())

    def get_visual_rect(self) -> pygame.Rect:
        """Returns the tight visual bounding rectangle of the rendered ink glyphs at the current position."""
        if hasattr(self, "_ink_rel") and isinstance(self._ink_rel, pygame.Rect) and self._ink_rel.width > 0:
            return pygame.Rect(
                int(self.position[0]) + self._ink_rel.x,
                int(self.position[1]) + self._ink_rel.y,
                self._ink_rel.width,
                self._ink_rel.height,
            )
        return self.rect if isinstance(self.rect, pygame.Rect) else self.get_bounding_rect()

    def _blit_normal(self):
        px, py = self._pad
        self.screen.blit(self._text_surface, (self.position[0] - px, self.position[1] - py))

    def draw(self):
        if not getattr(self, "visible", True):
            return
        if self._is_visual_occluded_by_popup(self.rect if isinstance(self.rect, pygame.Rect) else None):
            self.states["is_hovered"] = False
            if "active" in self.states:
                self.states["active"] = False
            return
        vp = getattr(self, "_scroll_viewport", None)
        if isinstance(vp, pygame.Rect):
            if isinstance(self.rect, pygame.Rect) and not vp.colliderect(self.rect):
                self.states["is_hovered"] = False
                if "active" in self.states:
                    self.states["active"] = False
                return
            prev_clip = self.screen.get_clip()
            self.screen.set_clip(vp)
            try:
                self._blit_normal()
                if self.detect_mouse:
                    self.mouse_collision(self.rect, self.get_mouse_pos(), self.draw_hover_effect)
            finally:
                self.screen.set_clip(prev_clip)
            return
        self._blit_normal()
        if self.detect_mouse:
            self.mouse_collision(self.rect, self.get_mouse_pos(), self.draw_hover_effect)

    def draw_hover_effect(self):
        hx, hy = self._hover_pad
        return self.screen.blit(self._hover_surface, (self.position[0] - hx, self.position[1] - hy))

    def change_item(self, config: dict):
        self.position = config.get("position", self.position)
        self.color = config.get("color", self.color)
        self.hover_color = config.get("hover_color", config.get("color2", self.hover_color))
        self.text = config.get("text", self.text)
        self.detect_mouse = config.get("detect_mouse", self.detect_mouse)
        self._update_surfaces()

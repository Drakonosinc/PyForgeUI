import pygame
from ..Behavior.Element_behavior import ElementBehavior
from ..VisualFX import RetroVisualFX
from .Text import Text


class TextButton(Text, ElementBehavior):
    _STEPPER_GLYPHS = {"<", ">", "Λ", "v", "▲", "▼"}

    def __init__(self, config: dict):
        self._hover_anim: float = 0.0
        self.hover_bg: bool = config.get("hover_bg", True)
        Text.__init__(self, config)
        ElementBehavior.__init__(self, config)

    def _is_combo_chevron(self) -> bool:
        owner = getattr(self, "_owner_popup", None)
        return owner is not None and getattr(owner, "button_dropdown", None) is self

    def _is_stepper_button(self) -> bool:
        return str(self.text).strip() in self._STEPPER_GLYPHS and not self._is_combo_chevron()

    def _draw_modern_backdrop(self) -> None:
        if not self.modern_style or not isinstance(self.rect, pygame.Rect):
            return
        if self._is_combo_chevron():
            return

        is_hovered = bool(self.states.get("is_hovered", False)) and self.detect_mouse
        target = 1.0 if is_hovered else 0.0
        if abs(self._hover_anim - target) > 0.01:
            self._hover_anim += (target - self._hover_anim) * 0.32
        else:
            self._hover_anim = target

        vis_rect = self.get_visual_rect()

        if self._is_stepper_button():
            RetroVisualFX.draw_stepper_badge(
                self.screen,
                vis_rect,
                hover_progress=self._hover_anim,
                base_color=(56, 189, 248),
                hover_color=self.hover_color,
            )
            return

        if self.hover_bg:
            c_rgb = RetroVisualFX.normalize_color(self.color)
            is_selected = c_rgb in ((135, 206, 235), (56, 189, 248)) and len(str(self.text).strip()) > 3
            if self._hover_anim > 0.02 or is_selected:
                RetroVisualFX.draw_hover_pill(
                    self.screen,
                    vis_rect,
                    progress=self._hover_anim,
                    hover_color=self.hover_color,
                    accent_color=c_rgb if is_selected else (56, 189, 248),
                    compact=(getattr(self, "_owner_popup", None) is not None),
                    is_selected=is_selected,
                )

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
                if self.detect_mouse and isinstance(self.rect, pygame.Rect):
                    self.states["is_hovered"] = (
                        not self._is_occluded_by_popup(self.rect, self.get_mouse_pos())
                        and self.rect.collidepoint(self.get_mouse_pos())
                    )
                else:
                    self.states["is_hovered"] = False
                self._draw_modern_backdrop()
                self._blit_normal()
                if self.detect_mouse:
                    self.mouse_collision(self.rect, self.get_mouse_pos(), self.draw_hover_effect)
                if self.pressed:
                    self.pressed_button(self.rect, pygame.mouse.get_pressed(), self.get_mouse_pos())
            finally:
                self.screen.set_clip(prev_clip)
            return

        if self.detect_mouse and isinstance(self.rect, pygame.Rect):
            self.states["is_hovered"] = (
                not self._is_occluded_by_popup(self.rect, self.get_mouse_pos())
                and self.rect.collidepoint(self.get_mouse_pos())
            )
        else:
            self.states["is_hovered"] = False

        self._draw_modern_backdrop()
        self._blit_normal()
        if self.detect_mouse:
            self.mouse_collision(self.rect, self.get_mouse_pos(), self.draw_hover_effect)
        if self.pressed:
            self.pressed_button(self.rect, pygame.mouse.get_pressed(), self.get_mouse_pos())

    def change_item(self, config: dict):
        super().change_item(config)
        self.pressed = config.get("pressed", self.pressed)

import pygame
from pygame.locals import *
from ..Behavior.Element_behavior import ElementBehavior
from ..VisualFX import RetroVisualFX


class InputText(ElementBehavior):
    def __init__(self, config: dict):
        super().__init__(config)
        self.font = config.get("font", pygame.font.Font(None, 25))
        self.text = config.get("text", "")
        self.modern_style: bool = config.get("modern_style", True)
        raw_color = config.get("color", (0, 0, 0))
        raw_back = config.get("color_back", (255, 255, 255))
        if self.modern_style and RetroVisualFX.normalize_color(raw_color) == (0, 0, 0) and RetroVisualFX.normalize_color(raw_back) == (255, 255, 255):
            self.color = (235, 248, 255)
            self.color_back = (12, 20, 40)
        else:
            self.color = raw_color
            self.color_back = raw_back

        self.hover_color = config.get("hover_color", (255, 199, 51))
        self.pressed_color = config.get("pressed_color", (56, 189, 248))
        self.border_color = config.get("border_color", (56, 189, 248))
        self.border = config.get("border", 2)
        self.rect = pygame.Rect(*self.position)
        self._hover_anim: float = 0.0
        self._update_text_surface()

    def _update_text_surface(self):
        if self.modern_style:
            self._text_surface, self._pad, (self._tw, self._th), self._ink_rel = RetroVisualFX.render_text_styled(
                self.font,
                self.text,
                self.color,
                shadow=True,
                glow=True,
                glow_color=(56, 189, 248),
                glow_radius=2,
            )
        else:
            self._text_surface = self.font.render(self.text, True, self.color)
            self._pad = (0, 0)
            self._tw, self._th = self._text_surface.get_size()
            self._ink_rel = self._text_surface.get_bounding_rect()

    def change_text(self, event):
        if self.states["active"] and event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (K_RETURN, K_ESCAPE, K_TAB) and event.unicode:
                self.text += event.unicode
            self._update_text_surface()

    def events(self, event):
        self.change_text(event)

    def draw(self):
        if not getattr(self, "visible", True) or self._is_visual_occluded_by_popup(self.rect):
            return

        mouse_pos = self.get_mouse_pos()
        if self.modern_style:
            is_hovered = (
                self.detect_mouse
                and not self._is_occluded_by_popup(self.rect, mouse_pos)
                and self.rect.collidepoint(mouse_pos)
            )
            target = 1.0 if (is_hovered or self.states.get("active", False)) else 0.0
            if abs(self._hover_anim - target) > 0.01:
                self._hover_anim += (target - self._hover_anim) * 0.3
            else:
                self._hover_anim = target

            if self.detect_mouse:
                self.mouse_collision(self.rect, mouse_pos)
            if self.pressed:
                self.pressed_button(self.rect, pygame.mouse.get_pressed(), mouse_pos)

            is_active = bool(self.states.get("active", False))
            base_b = RetroVisualFX.normalize_color(self.border_color)
            hov_b = RetroVisualFX.normalize_color(self.hover_color)
            act_b = RetroVisualFX.normalize_color(self.pressed_color)
            rim_col = act_b if is_active else RetroVisualFX.lerp_color(base_b, hov_b, self._hover_anim)

            pad = 4
            surf = pygame.Surface((self.rect.width + pad * 2, self.rect.height + pad * 2), pygame.SRCALPHA)
            local = pygame.Rect(pad, pad, self.rect.width, self.rect.height)

            if self._hover_anim > 0.02 or is_active:
                pygame.draw.rect(surf, (*rim_col, int(65 * max(self._hover_anim, 0.7 if is_active else 0.0))), local.inflate(4, 4), border_radius=6)

            bg_col = (18, 30, 58, 240) if is_active else (12, 20, 40, 225)
            pygame.draw.rect(surf, bg_col, local, border_radius=5)

            # Top glass highlight
            shine = pygame.Rect(local.x + 2, local.y + 2, max(1, local.width - 4), max(2, local.height // 3))
            pygame.draw.rect(surf, (255, 255, 255, 16), shine, border_top_left_radius=4, border_top_right_radius=4)

            pygame.draw.rect(surf, (*rim_col, 240), local, self.border, border_radius=5)
            self.screen.blit(surf, (self.rect.x - pad, self.rect.y - pad))

            # Clip & vertically align text inside the input box
            prev_clip = self.screen.get_clip()
            inner_clip = self.rect.inflate(-6, -2)
            self.screen.set_clip(inner_clip)
            try:
                px, py = self._pad
                tx = self.rect.x + 8
                ty = self.rect.y + (self.rect.height - self._th) // 2 - 1
                self.screen.blit(self._text_surface, (tx - px, ty - py))

                if is_active:
                    try:
                        ticks = pygame.time.get_ticks()
                    except Exception:
                        ticks = 0
                    if (ticks // 450) % 2 == 0:
                        cx = min(inner_clip.right - 3, tx + self._tw + 3)
                        pygame.draw.line(self.screen, rim_col, (cx, self.rect.y + 4), (cx, self.rect.bottom - 4), 2)
            finally:
                self.screen.set_clip(prev_clip)
            return

        pygame.draw.rect(self.screen, self.color_back, self.rect)
        if self.detect_mouse:
            self.mouse_collision(self.rect, mouse_pos)
        if self.pressed:
            self.pressed_button(self.rect, pygame.mouse.get_pressed(), mouse_pos)
        input_player = pygame.draw.rect(self.screen, self.border_color, self.rect, self.border)
        self.screen.blit(self._text_surface, (input_player.x + 5, input_player.y - 2))

    def pressed_button(self, rect, pressed_mouse, mouse_pos, draw=None, repeat: bool = None):
        if not getattr(self, "visible", True) or not getattr(self, "enabled", True) or self._is_occluded_by_popup(rect, mouse_pos):
            return False
        if pressed_mouse[0] and self.states["presses_touch"]:
            if rect.collidepoint(mouse_pos):
                self.states["active"] = True
                self.states["presses_touch"] = False
                if self.sound_touch:
                    self.sound_touch.play(loops=0)
            else:
                self.states["active"], self.states["presses_touch"] = False, False
        if not pressed_mouse[0]:
            self.states["presses_touch"] = True
        if self.states["active"] and not self.modern_style:
            self.draw_pressed_effect() if draw is None else draw()

    def draw_hover_effect(self):
        if self.modern_style:
            return self.rect
        return pygame.draw.rect(self.screen, self.hover_color, self.rect)

    def draw_pressed_effect(self):
        if self.modern_style:
            return self.rect
        return pygame.draw.rect(self.screen, self.pressed_color, self.rect)

    def show_player(self):
        return self.text


Input_text = InputText

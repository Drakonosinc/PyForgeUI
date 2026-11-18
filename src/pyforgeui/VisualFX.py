import math
import random
import pygame


class RetroVisualFX:
    """High-performance retro-modern visual effects, neon typography, HUD glass cards, and widget styling primitives."""

    _text_cache: dict = {}
    _MAX_CACHE_SIZE: int = 512

    @classmethod
    def _trim_cache(cls, cache_dict: dict) -> None:
        if len(cache_dict) > cls._MAX_CACHE_SIZE:
            keys = list(cache_dict.keys())
            for k in keys[: len(keys) // 2]:
                cache_dict.pop(k, None)

    @staticmethod
    def normalize_color(color, default=(255, 255, 255)) -> tuple[int, int, int]:
        if isinstance(color, str):
            try:
                c = pygame.Color(color)
                return (c.r, c.g, c.b)
            except Exception:
                return default
        if isinstance(color, (tuple, list)) and len(color) >= 3:
            return (
                max(0, min(255, int(color[0]))),
                max(0, min(255, int(color[1]))),
                max(0, min(255, int(color[2]))),
            )
        return default

    @staticmethod
    def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
        t = max(0.0, min(1.0, float(t)))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    @staticmethod
    def brighten(color: tuple[int, int, int], amount: int = 45) -> tuple[int, int, int]:
        r, g, b = RetroVisualFX.normalize_color(color)
        return (min(255, r + amount), min(255, g + amount), min(255, b + amount))

    @classmethod
    def render_text_styled(
        cls,
        font: pygame.font.Font,
        text: str,
        color,
        shadow: bool = True,
        shadow_color: tuple[int, int, int] = (4, 8, 18),
        shadow_offset: tuple[int, int] = (2, 2),
        glow: bool = False,
        glow_color=None,
        glow_radius: int = 3,
        highlight_second_line: bool = False,
        second_line_color: tuple[int, int, int] = (56, 189, 248),
    ) -> tuple[pygame.Surface, tuple[int, int], tuple[int, int], pygame.Rect]:
        """
        Renders single-line or multi-line text with drop shadow and optional neon glow.
        Returns (styled_surface, (pad_x, pad_y), (base_width, base_height), ink_bounds_rel).
        ink_bounds_rel is the tight bounding rect of the visible glyphs relative to position (0, 0).
        """
        rgb = cls.normalize_color(color)
        g_rgb = cls.normalize_color(glow_color if glow_color is not None else rgb)
        s_rgb = cls.normalize_color(shadow_color, (4, 8, 18))
        sec_rgb = cls.normalize_color(second_line_color, (56, 189, 248))

        cache_key = (
            id(font),
            font.get_height(),
            font.get_linesize(),
            text,
            rgb,
            shadow,
            s_rgb,
            shadow_offset,
            glow,
            g_rgb,
            glow_radius,
            highlight_second_line,
            sec_rgb,
        )
        cached = cls._text_cache.get(cache_key)
        if cached is not None:
            return cached

        lines = text.split("\n") if "\n" in text else [text]
        line_surfaces = []
        line_glow_surfaces = []
        line_shadow_surfaces = []

        for idx, line in enumerate(lines):
            use_sec = highlight_second_line and idx > 0 and line.strip() != ""
            line_col = sec_rgb if use_sec else rgb
            line_g_col = sec_rgb if use_sec else g_rgb
            surf = font.render(line, True, line_col)
            line_surfaces.append(surf)
            if shadow:
                s_surf = font.render(line, True, s_rgb)
                s_surf.set_alpha(210)
                line_shadow_surfaces.append(s_surf)
            if glow or use_sec:
                g_surf = font.render(line, True, line_g_col)
                line_glow_surfaces.append(g_surf)
            else:
                line_glow_surfaces.append(None)

        base_w = max((s.get_width() for s in line_surfaces), default=0)
        line_h = font.get_linesize()
        base_h = max(line_h * len(lines), line_surfaces[0].get_height() if line_surfaces else 0)

        # Compute tight visible ink bounding rect relative to (0, 0)
        ink_rects = []
        for idx, surf in enumerate(line_surfaces):
            b = surf.get_bounding_rect()
            if b.width > 0 and b.height > 0:
                ink_rects.append(pygame.Rect(b.x, idx * line_h + b.y, b.width, b.height))
        if ink_rects:
            ink_rel = ink_rects[0].copy()
            for r in ink_rects[1:]:
                ink_rel.union_ip(r)
        else:
            ink_rel = pygame.Rect(0, 0, base_w, base_h)

        pad = max(glow_radius + 2 if (glow or highlight_second_line) else 0, abs(shadow_offset[0]) + 2, abs(shadow_offset[1]) + 2)
        total_w = max(1, base_w + pad * 2)
        total_h = max(1, base_h + pad * 2)

        canvas = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

        for idx, surf in enumerate(line_surfaces):
            ly = pad + idx * line_h
            lx = pad
            g_surf = line_glow_surfaces[idx]
            if g_surf is not None:
                offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]
                g_copy = g_surf.copy()
                g_copy.set_alpha(38 if glow else 28)
                for ox, oy in offsets:
                    canvas.blit(g_copy, (lx + ox, ly + oy))

            if shadow and idx < len(line_shadow_surfaces):
                canvas.blit(line_shadow_surfaces[idx], (lx + shadow_offset[0], ly + shadow_offset[1]))

            canvas.blit(surf, (lx, ly))

        result = (canvas, (pad, pad), (base_w, base_h), ink_rel)
        cls._trim_cache(cls._text_cache)
        cls._text_cache[cache_key] = result
        return result

    @classmethod
    def draw_hover_pill(
        cls,
        screen: pygame.Surface,
        rect: pygame.Rect,
        progress: float,
        hover_color=(255, 199, 51),
        accent_color=(56, 189, 248),
        compact: bool = False,
        is_selected: bool = False,
    ) -> None:
        """Draws a retro-modern glass pill, neon border, and expanding underline tightly around the visible text."""
        if rect.width <= 0 or rect.height <= 0:
            return
        progress = max(0.0, min(1.0, float(progress)))
        if progress <= 0.01 and not is_selected:
            return

        h_col = cls.normalize_color(hover_color)
        a_col = cls.normalize_color(accent_color)
        active_col = h_col if progress > 0.05 else a_col

        pad_x = 6 if compact else 9
        pad_y = 3 if compact else 4
        pill_rect = rect.inflate(pad_x * 2, pad_y * 2)

        surf = pygame.Surface((pill_rect.width + 8, pill_rect.height + 8), pygame.SRCALPHA)
        local_rect = pygame.Rect(4, 4, pill_rect.width, pill_rect.height)

        fill_alpha = int(145 * progress) if progress > 0.05 else 90
        border_alpha = int(225 * progress) if progress > 0.05 else 145

        glow_rect = local_rect.inflate(4, 4)
        pygame.draw.rect(surf, (*active_col, int(50 * max(progress, 0.4))), glow_rect, border_radius=6)
        pygame.draw.rect(surf, (14, 22, 42, fill_alpha), local_rect, border_radius=5)
        pygame.draw.rect(surf, (*active_col, border_alpha), local_rect, 1, border_radius=5)

        if not compact:
            bar_ratio = progress if progress > 0.05 else 0.65
            bar_w = max(4, int((local_rect.width - 10) * bar_ratio))
            bar_x = local_rect.centerx - bar_w // 2
            bar_y = local_rect.bottom - 2
            pygame.draw.line(surf, (*active_col, min(255, border_alpha + 30)), (bar_x, bar_y), (bar_x + bar_w, bar_y), 2)

        screen.blit(surf, (pill_rect.x - 4, pill_rect.y - 4))

    @classmethod
    def draw_stepper_badge(
        cls,
        screen: pygame.Surface,
        rect: pygame.Rect,
        hover_progress: float = 0.0,
        base_color=(56, 189, 248),
        hover_color=(255, 199, 51),
    ) -> None:
        """Draws a compact arcade button badge tightly centered on the visible stepper glyph (<, >, +, -, Λ, v)."""
        if rect.width <= 0 or rect.height <= 0:
            return
        t = max(0.0, min(1.0, float(hover_progress)))
        b_col = cls.normalize_color(base_color)
        h_col = cls.normalize_color(hover_color)
        rim_col = cls.lerp_color(b_col, h_col, t)

        bw = max(rect.width + 8, 16)
        bh = max(rect.height + 6, 16)
        box = pygame.Rect(0, 0, bw, bh)
        box.center = rect.center

        surf = pygame.Surface((box.width + 6, box.height + 6), pygame.SRCALPHA)
        local = pygame.Rect(3, 3, box.width, box.height)
        if t > 0.05:
            pygame.draw.rect(surf, (*rim_col, int(80 * t)), local.inflate(4, 4), border_radius=5)
        pygame.draw.rect(surf, (14, 22, 42, int(175 + 55 * t)), local, border_radius=4)
        pygame.draw.rect(surf, (*rim_col, int(140 + 110 * t)), local, 1, border_radius=4)
        screen.blit(surf, (box.x - 3, box.y - 3))

    @classmethod
    def draw_glow_polygon(
        cls,
        screen: pygame.Surface,
        points: list[tuple[float, float]] | tuple,
        fill_color,
        outline_color=None,
        hover_color=(255, 199, 51),
        hover_progress: float = 0.0,
        enabled: bool = True,
    ) -> pygame.Rect:
        """Draws a vector-arcade glowing polygon with smooth hover color interpolation."""
        pts = [(int(round(p[0])), int(round(p[1]))) for p in points]
        if len(pts) < 3:
            return pygame.Rect(0, 0, 0, 0)

        f_col = cls.normalize_color(fill_color)
        h_col = cls.normalize_color(hover_color)
        o_col = cls.normalize_color(outline_color) if outline_color is not None else None

        is_hollow_style = f_col == (0, 0, 0) and o_col is not None
        if not enabled:
            main_fill = (55, 62, 78)
            rim_col = (95, 105, 125)
            glow_col = None
        elif is_hollow_style:
            base_rim = o_col if o_col is not None else (56, 189, 248)
            rim_col = cls.lerp_color(base_rim, h_col, hover_progress)
            main_fill = cls.lerp_color((16, 28, 52), h_col, hover_progress * 0.65)
            glow_col = rim_col
        else:
            main_fill = cls.lerp_color(f_col, h_col, hover_progress)
            rim_col = cls.lerp_color((56, 189, 248), h_col, hover_progress)
            glow_col = rim_col

        min_x = min(p[0] for p in pts)
        max_x = max(p[0] for p in pts)
        min_y = min(p[1] for p in pts)
        max_y = max(p[1] for p in pts)
        pad = 8
        w = max(1, (max_x - min_x) + pad * 2)
        h = max(1, (max_y - min_y) + pad * 2)

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        local_pts = [(p[0] - min_x + pad, p[1] - min_y + pad) for p in pts]

        if glow_col is not None:
            glow_alpha = int(75 + 95 * hover_progress)
            pygame.draw.polygon(surf, (*glow_col, glow_alpha // 2), local_pts, width=5)
            pygame.draw.polygon(surf, (*glow_col, glow_alpha), local_pts, width=3)

        pygame.draw.polygon(surf, (*main_fill, 240 if enabled else 140), local_pts)
        pygame.draw.polygon(surf, (*rim_col, 255 if enabled else 160), local_pts, width=2)

        screen.blit(surf, (min_x - pad, min_y - pad))
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    @classmethod
    def draw_hud_frame(
        cls,
        screen: pygame.Surface,
        rect: pygame.Rect | tuple,
        accent_color: tuple[int, int, int] = (56, 189, 248),
        bg_color: tuple[int, int, int] = (10, 15, 30),
        bg_alpha: int = 165,
        border_radius: int = 8,
        corner_size: int = 12,
        header_line_y: int | None = None,
        glow: bool = True,
    ) -> None:
        """Draws a translucent frosted-glass sci-fi HUD card with glowing L-bracket corners."""
        r = pygame.Rect(rect) if not isinstance(rect, pygame.Rect) else rect
        if r.width <= 0 or r.height <= 0:
            return
        acc = cls.normalize_color(accent_color)
        bg = cls.normalize_color(bg_color, (10, 15, 30))

        pad = 6
        surf = pygame.Surface((r.width + pad * 2, r.height + pad * 2), pygame.SRCALPHA)
        local = pygame.Rect(pad, pad, r.width, r.height)

        pygame.draw.rect(surf, (0, 0, 0, 130), local.move(3, 4), border_radius=border_radius)
        if glow:
            pygame.draw.rect(surf, (*acc, 36), local.inflate(4, 4), border_radius=border_radius + 2)

        pygame.draw.rect(surf, (*bg, bg_alpha), local, border_radius=border_radius)

        if local.height > 16:
            shine = pygame.Rect(local.x + 2, local.y + 2, max(1, local.width - 4), min(14, local.height // 4))
            pygame.draw.rect(
                surf,
                (255, 255, 255, 14),
                shine,
                border_top_left_radius=max(1, border_radius - 2),
                border_top_right_radius=max(1, border_radius - 2),
            )

        pygame.draw.rect(surf, (*acc, 85), local, 1, border_radius=border_radius)

        if header_line_y is not None and r.top < header_line_y < r.bottom:
            ly = header_line_y - r.top + pad
            pygame.draw.line(surf, (*acc, 110), (local.left + 8, ly), (local.right - 8, ly), 1)

        cl = min(corner_size, local.width // 3, local.height // 3)
        if cl >= 4:
            c_col = (*cls.brighten(acc, 40), 235)
            x0, y0, x1, y1 = local.left, local.top, local.right - 1, local.bottom - 1
            pygame.draw.lines(surf, c_col, False, [(x0, y0 + cl), (x0, y0), (x0 + cl, y0)], 2)
            pygame.draw.lines(surf, c_col, False, [(x1 - cl, y0), (x1, y0), (x1, y0 + cl)], 2)
            pygame.draw.lines(surf, c_col, False, [(x0, y1 - cl), (x0, y1), (x0 + cl, y1)], 2)
            pygame.draw.lines(surf, c_col, False, [(x1 - cl, y1), (x1, y1), (x1, y1 - cl)], 2)

        screen.blit(surf, (r.x - pad, r.y - pad))

    @classmethod
    def draw_neon_title(
        cls,
        screen: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        position: tuple[float, float],
        color=(255, 255, 255),
        glow_color=(56, 189, 248),
        accent_color=(168, 85, 247),
        underline: bool = True,
    ) -> pygame.Rect:
        """Draws a multi-layer glowing retro-modern title at the exact target position."""
        x, y = int(position[0]), int(position[1])
        c_rgb = cls.normalize_color(color)
        g_rgb = cls.normalize_color(glow_color)
        a_rgb = cls.normalize_color(accent_color)

        try:
            ticks = pygame.time.get_ticks()
        except Exception:
            ticks = 0
        pulse = 0.5 + 0.5 * math.sin(ticks * 0.004)

        surf, (px, py), (bw, bh), ink_rel = cls.render_text_styled(
            font,
            text,
            color=c_rgb,
            shadow=True,
            shadow_color=(6, 10, 24),
            shadow_offset=(3, 3),
            glow=True,
            glow_color=g_rgb,
            glow_radius=4,
        )

        aura_surf = font.render(text, True, a_rgb)
        aura_surf.set_alpha(int(55 + 45 * pulse))
        screen.blit(aura_surf, (x - 2, y + 2))
        screen.blit(surf, (x - px, y - py))

        if underline and ink_rel.width > 20:
            line_x = x + ink_rel.left
            line_w = ink_rel.width
            line_y = y + ink_rel.bottom + 6
            pygame.draw.line(screen, (*a_rgb, 140), (line_x, line_y + 1), (line_x + line_w, line_y + 1), 3)
            pygame.draw.line(screen, g_rgb, (line_x, line_y), (line_x + line_w, line_y), 2)
            spark_x = line_x + int(((ticks * 0.12) % max(1, line_w)))
            spark_w = min(32, line_w // 3)
            spark_end = min(line_x + line_w, spark_x + spark_w)
            pygame.draw.line(screen, (255, 255, 255), (spark_x, line_y), (spark_end, line_y), 2)

        return pygame.Rect(x, y, bw, bh)

    @classmethod
    def draw_status_badge(
        cls,
        screen: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        position: tuple[float, float],
        status_color=(56, 189, 248),
    ) -> None:
        """Draws a sleek bottom-bar HUD status pill with a glowing LED indicator and crisp text."""
        x, y = int(position[0]), int(position[1])
        s_col = cls.normalize_color(status_color)
        surf, (px, py), (bw, bh), ink_rel = cls.render_text_styled(
            font, text, color=s_col, shadow=True, glow=True, glow_color=s_col, glow_radius=2
        )
        pill_y = y + ink_rel.top - 4
        pill_h = max(18, ink_rel.height + 8)
        pill = pygame.Rect(x - 4, pill_y, bw + 24, pill_h)
        pill_surf = pygame.Surface((pill.width, pill.height), pygame.SRCALPHA)
        pygame.draw.rect(pill_surf, (10, 16, 32, 210), pill_surf.get_rect(), border_radius=5)
        pygame.draw.rect(pill_surf, (*s_col, 165), pill_surf.get_rect(), 1, border_radius=5)
        led_center = (9, pill.height // 2)
        pygame.draw.circle(pill_surf, (*s_col, 90), led_center, 5)
        pygame.draw.circle(pill_surf, s_col, led_center, 3)
        screen.blit(pill_surf, pill.topleft)
        screen.blit(surf, (x + 12 - px, y - py))

    @classmethod
    def draw_keycap(
        cls,
        screen: pygame.Surface,
        rect: pygame.Rect,
        is_rebinding: bool = False,
        is_hovered: bool = False,
        accent_color=(56, 189, 248),
        hover_color=(255, 199, 51),
    ) -> None:
        """Draws a 3D mechanical arcade keycap centered on the visible key glyph."""
        if rect.width <= 0 or rect.height <= 0:
            return
        size = max(rect.width + 24, rect.height + 24, 86)
        cap_rect = pygame.Rect(0, 0, size, size)
        cap_rect.center = rect.center

        acc = cls.normalize_color(accent_color)
        hov = cls.normalize_color(hover_color)
        rim = hov if is_hovered else (acc if is_rebinding else (95, 145, 205))

        pad = 8
        surf = pygame.Surface((cap_rect.width + pad * 2, cap_rect.height + pad * 2), pygame.SRCALPHA)
        outer = pygame.Rect(pad, pad, cap_rect.width, cap_rect.height)
        inner = outer.inflate(-10, -10)
        inner.y -= 2

        if is_rebinding or is_hovered:
            pygame.draw.rect(surf, (*rim, 85), outer.inflate(6, 6), border_radius=12)

        pygame.draw.rect(surf, (8, 12, 24, 235), outer, border_radius=10)
        pygame.draw.rect(surf, (*rim, 180), outer, 2, border_radius=10)

        top_fill = (24, 38, 68, 240) if is_rebinding else (16, 24, 46, 235)
        pygame.draw.rect(surf, top_fill, inner, border_radius=7)
        pygame.draw.rect(surf, (*cls.brighten(rim, 35), 210), inner, 1, border_radius=7)

        screen.blit(surf, (cap_rect.x - pad, cap_rect.y - pad))

    @classmethod
    def draw_synapse_network(
        cls,
        screen: pygame.Surface,
        connections: list[tuple[tuple[int, int], tuple[int, int]]],
        network_buttons: list[list],
        accent_color=(56, 189, 248),
        secondary_color=(168, 85, 247),
        pulse_color=(255, 199, 51),
    ) -> None:
        """Draws a glowing neural network graph with animated energy pulses along synapses and glowing neuron nodes."""
        acc = cls.normalize_color(accent_color)
        sec = cls.normalize_color(secondary_color)
        pul = cls.normalize_color(pulse_color)

        try:
            ticks = pygame.time.get_ticks()
        except Exception:
            ticks = 0

        for idx, (p1, p2) in enumerate(connections):
            t_col = cls.lerp_color(acc, sec, (idx % 7) / 6.0)
            pygame.draw.line(screen, t_col, p1, p2, 1)

            phase = ((ticks * 0.0012) + (idx * 0.17)) % 1.0
            px = int(p1[0] + (p2[0] - p1[0]) * phase)
            py = int(p1[1] + (p2[1] - p1[1]) * phase)
            pygame.draw.circle(screen, pul, (px, py), 2)

        num_layers = len(network_buttons)
        for l_idx, layer in enumerate(network_buttons):
            layer_ratio = l_idx / max(1, num_layers - 1)
            node_col = cls.lerp_color(acc, sec, layer_ratio)
            for btn in layer:
                bounds = btn.get_bounding_rect()
                cx, cy = bounds.centerx, bounds.centery
                halo_r = max(14, bounds.width // 2 + 6)
                halo_surf = pygame.Surface((halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA)
                center_local = (halo_r + 2, halo_r + 2)
                pygame.draw.circle(halo_surf, (*node_col, 55), center_local, halo_r)
                pygame.draw.circle(halo_surf, (*node_col, 130), center_local, halo_r - 3, 1)
                screen.blit(halo_surf, (cx - halo_r - 2, cy - halo_r - 2))
                btn.draw()

    @classmethod
    def draw_live_neural_network(
        cls,
        screen: pygame.Surface,
        rect: pygame.Rect | tuple[int, int, int, int],
        layers_sizes: list[int] | tuple[int, ...],
        layer_activations: list | None = None,
        accent_color=(56, 189, 248),
        secondary_color=(168, 85, 247),
        pulse_color=(255, 199, 51),
        opacity: int = 120,
        show_frame: bool = True,
        max_visible_neurons: int = 8,
    ) -> None:
        """
        Draws a translucent, adaptive live neural network topology with real-time per-neuron
        activations, glowing square scanlined nodes, circular neon halos, and active synapse pulses.
        Automatically pools layers larger than `max_visible_neurons` into representative neuron banks.
        """
        r = pygame.Rect(rect) if not isinstance(rect, pygame.Rect) else rect
        if r.width <= 20 or r.height <= 20 or not layers_sizes or len(layers_sizes) < 2:
            return

        acc = cls.normalize_color(accent_color)
        sec = cls.normalize_color(secondary_color)
        pul = cls.normalize_color(pulse_color)

        try:
            ticks = pygame.time.get_ticks()
        except Exception:
            ticks = 0

        panel = pygame.Surface((r.width, r.height), pygame.SRCALPHA)

        if show_frame:
            cls.draw_hud_frame(
                panel,
                (0, 0, r.width, r.height),
                accent_color=sec,
                bg_color=(8, 12, 26),
                bg_alpha=68,
                corner_size=12,
                glow=True,
            )

        num_layers = len(layers_sizes)
        pad_x = max(24, int(r.width * 0.06))
        pad_y = max(14, int(r.height * 0.06))
        left, right = pad_x, r.width - pad_x
        top, bottom = pad_y, r.height - pad_y

        x_positions = [
            int(left + i * (right - left) / max(1, num_layers - 1))
            for i in range(num_layers)
        ]

        layer_centers: list[list[tuple[int, int]]] = []
        layer_node_sizes: list[int] = []
        acts_per_layer: list[list[float]] = []

        for l_idx, raw_n in enumerate(layers_sizes):
            actual_n = max(1, int(raw_n))
            vis_n = min(actual_n, max(2, int(max_visible_neurons)))
            y_gap = (bottom - top) / (vis_n + 1)
            node_half = max(5, min(9, int(y_gap * 0.34)))
            layer_node_sizes.append(node_half)
            centers = [
                (x_positions[l_idx], int(top + (i + 1) * y_gap))
                for i in range(vis_n)
            ]
            layer_centers.append(centers)

            raw_acts = None
            if layer_activations is not None and l_idx < len(layer_activations):
                raw_acts = layer_activations[l_idx]

            layer_vals: list[float] = []
            if raw_acts is not None and len(raw_acts) > 0:
                n_raw = len(raw_acts)
                for i in range(vis_n):
                    if n_raw > vis_n:
                        s_idx = int(i * n_raw / vis_n)
                        e_idx = max(s_idx + 1, int((i + 1) * n_raw / vis_n))
                        chunk = [
                            0.0 if (math.isnan(float(x)) or math.isinf(float(x))) else float(x)
                            for x in raw_acts[s_idx:e_idx]
                        ]
                        val = (max(chunk) * 0.65 + (sum(chunk) / len(chunk)) * 0.35) if chunk else 0.0
                    elif i < n_raw:
                        val = float(raw_acts[i])
                        if math.isnan(val) or math.isinf(val):
                            val = 0.0
                    else:
                        val = 0.2
                    layer_vals.append(max(0.0, min(1.0, val)))
            else:
                for i in range(vis_n):
                    wave = 0.35 + 0.25 * math.sin(ticks * 0.003 + l_idx * 0.8 + i * 0.6)
                    layer_vals.append(max(0.0, min(1.0, wave)))
            acts_per_layer.append(layer_vals)

        # 1. Draw synapses and real-time signal energy pulses
        conn_idx = 0
        for li in range(num_layers - 1):
            c_left = layer_centers[li]
            c_right = layer_centers[li + 1]
            a_left = acts_per_layer[li]
            a_right = acts_per_layer[li + 1]

            for i, p1 in enumerate(c_left):
                a1 = a_left[i]
                for j, p2 in enumerate(c_right):
                    a2 = a_right[j]
                    signal = max(0.0, min(1.0, a1 * a2))
                    grad_t = (li + (conn_idx % 7) / 7.0) / max(1, num_layers - 1)
                    base_col = cls.lerp_color(acc, sec, grad_t)
                    active_tint = pul if signal > 0.65 else (130, 235, 255)
                    syn_col = cls.lerp_color(base_col, active_tint, signal * 0.55)
                    syn_alpha = int(38 + 182 * signal)
                    pygame.draw.line(panel, (*syn_col, syn_alpha), p1, p2, 2 if signal > 0.68 else 1)

                    if signal > 0.08:
                        speed = 0.0011 + 0.0007 * signal
                        phase = ((ticks * speed) + (conn_idx * 0.17)) % 1.0
                        px = int(p1[0] + (p2[0] - p1[0]) * phase)
                        py = int(p1[1] + (p2[1] - p1[1]) * phase)
                        p_alpha = int(90 + 165 * signal)
                        p_radius = 3 if signal > 0.65 else 2
                        pygame.draw.circle(panel, (*pul, p_alpha), (px, py), p_radius)

                    conn_idx += 1

        # 2. Draw neuron halos and scanlined square nodes reactive to activation level
        for l_idx, centers in enumerate(layer_centers):
            layer_ratio = l_idx / max(1, num_layers - 1)
            base_node_col = cls.lerp_color(acc, sec, layer_ratio)
            node_half = layer_node_sizes[l_idx]
            acts = acts_per_layer[l_idx]
            is_output_layer = l_idx == num_layers - 1

            for n_idx, (cx, cy) in enumerate(centers):
                act = acts[n_idx]
                peak_col = pul if (is_output_layer and act > 0.55) else (110, 238, 255)
                halo_col = cls.lerp_color(base_node_col, peak_col, act * 0.75)

                halo_r = int(node_half + 4 + round(3 * act))
                pygame.draw.circle(panel, (*halo_col, int(24 + 76 * act)), (cx, cy), halo_r)
                pygame.draw.circle(panel, (*halo_col, int(70 + 150 * act)), (cx, cy), max(1, halo_r - 2), 1)

                fill_col = cls.lerp_color((20, 32, 56), (245, 252, 255), act)
                rim_col = cls.lerp_color(base_node_col, pul if (is_output_layer and act > 0.65) else (255, 255, 255), act)

                sq_rect = pygame.Rect(cx - node_half, cy - node_half, node_half * 2, node_half * 2)
                pygame.draw.rect(panel, (*fill_col, int(185 + 70 * act)), sq_rect)

                scan_col = cls.lerp_color((12, 20, 38), (155, 215, 250), act)
                for sy in range(sq_rect.top + 2, sq_rect.bottom - 1, 3):
                    pygame.draw.line(
                        panel,
                        (*scan_col, int(145 + 85 * act)),
                        (sq_rect.left + 1, sy),
                        (sq_rect.right - 2, sy),
                        1,
                    )

                pygame.draw.rect(panel, (*rim_col, int(195 + 60 * act)), sq_rect, 2)

        panel.set_alpha(max(20, min(255, int(opacity))))
        screen.blit(panel, r.topleft)


class RetroBackdrop:
    """Reusable animated retro-modern backdrop with deep-space gradient, cyber grid, floating neon dust, and CRT vignette."""

    def __init__(
        self,
        width: int,
        height: int,
        accent_color: tuple[int, int, int] = (56, 189, 248),
        secondary_color: tuple[int, int, int] = (168, 85, 247),
        num_particles: int = 38,
    ) -> None:
        self.width = max(1, int(width))
        self.height = max(1, int(height))
        self.accent_color = RetroVisualFX.normalize_color(accent_color)
        self.secondary_color = RetroVisualFX.normalize_color(secondary_color)
        self.num_particles = num_particles
        self._bg_surface: pygame.Surface | None = None
        self._post_surface: pygame.Surface | None = None
        self._particles: list[list[float]] = []
        self._rebuild_surfaces()

    def resize(self, width: int, height: int) -> None:
        w, h = max(1, int(width)), max(1, int(height))
        if w != self.width or h != self.height:
            self.width = w
            self.height = h
            self._rebuild_surfaces()

    def _rebuild_surfaces(self) -> None:
        w, h = self.width, self.height
        bg = pygame.Surface((w, h))
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(5 + 9 * t)
            g = int(8 + 14 * (1.0 - abs(t - 0.5) * 1.5))
            b = int(18 + 26 * t)
            pygame.draw.line(bg, (r, g, b), (0, y), (w, y))

        nebula = pygame.Surface((w, h), pygame.SRCALPHA)
        for radius, alpha in ((180, 12), (130, 18), (85, 22)):
            pygame.draw.circle(nebula, (*self.accent_color, alpha), (int(w * 0.22), int(h * 0.28)), radius)
            pygame.draw.circle(nebula, (*self.secondary_color, alpha), (int(w * 0.78), int(h * 0.72)), radius)
        bg.blit(nebula, (0, 0))
        self._bg_surface = bg

        post = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(post, (0, 0, 0, 26), (0, y), (w, y))

        pygame.draw.rect(post, (0, 0, 0, 90), (0, 0, w, h), 4)
        pygame.draw.rect(post, (*self.accent_color, 55), (2, 2, w - 4, h - 4), 1)
        self._post_surface = post

        rng = random.Random(42)
        self._particles = [
            [
                rng.uniform(0, w),
                rng.uniform(0, h),
                rng.uniform(-12.0, 12.0),
                rng.uniform(-18.0, -5.0),
                rng.uniform(1.2, 2.6),
                rng.uniform(0.0, math.tau),
                float(rng.choice((0, 1))),
            ]
            for _ in range(self.num_particles)
        ]

    def draw_background(self, screen: pygame.Surface, show_grid: bool = True, show_particles: bool = True) -> None:
        w, h = screen.get_size()
        if w != self.width or h != self.height:
            self.resize(w, h)

        if self._bg_surface is not None:
            screen.blit(self._bg_surface, (0, 0))

        try:
            ticks = pygame.time.get_ticks()
        except Exception:
            ticks = 0

        if show_grid:
            grid_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            horizon_y = int(h * 0.62)
            step = 45
            offset_y = int((ticks * 0.015) % step)
            for gx in range(0, w, step):
                pygame.draw.line(grid_surf, (*self.accent_color, 14), (gx, 0), (gx, h), 1)
            for gy in range(offset_y, h, step):
                pygame.draw.line(grid_surf, (*self.accent_color, 14), (0, gy), (w, gy), 1)

            cx = w // 2
            for i in range(-6, 7):
                top_x = cx + i * 38
                bot_x = cx + i * 115
                pygame.draw.line(grid_surf, (*self.secondary_color, 26), (top_x, horizon_y), (bot_x, h), 1)
            screen.blit(grid_surf, (0, 0))

        if show_particles:
            dt = 1.0 / 60.0
            p_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            for p in self._particles:
                p[0] = (p[0] + p[2] * dt) % w
                p[1] = (p[1] + p[3] * dt) % h
                twinkle = 0.5 + 0.5 * math.sin(ticks * 0.004 + p[5])
                col = self.accent_color if p[6] < 0.5 else self.secondary_color
                alpha = int(45 + 115 * twinkle)
                radius = max(1, int(round(p[4])))
                pygame.draw.circle(p_surf, (*col, alpha), (int(p[0]), int(p[1])), radius)
            screen.blit(p_surf, (0, 0))

    def draw_post_overlay(self, screen: pygame.Surface) -> None:
        w, h = screen.get_size()
        if w != self.width or h != self.height:
            self.resize(w, h)
        if self._post_surface is not None:
            screen.blit(self._post_surface, (0, 0))

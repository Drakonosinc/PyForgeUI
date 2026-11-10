import pygame
from .Text_button import TextButton
from .Scroll_bar import ScrollBar


class ComboBox(TextButton):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        from ..Elements_Factory import ElementsFactory
        self.type_dropdown: str = self.get_icon()
        self.dropdown: list[int] = config.get("size", [self.font.size(self.text)[0] + self.font.size(self.type_dropdown)[0], 100])
        self.hover_dropdown: tuple[int, int, int] = config.get("hover_dropdown", (135, 206, 235))
        self.replace_text: bool = config.get("replace_text", False)
        self.adapt_dropdown: bool = config.get("adapt_dropdown", True)
        self.draw_scroll: bool = config.get("draw_scroll", True)
        self.command_dropdown = config.get("command_dropdown", None)
        self.anim_height_dropdown: int = 0
        self.is_dropdown_open: bool = False
        self.options: list[str] = []
        self.option_buttons: dict = {}
        self._last_layout_rect: pygame.Rect | None = None
        self.padding_x: int = config.get("padding_x", 6)
        self.padding_y: int = config.get("padding_y", 6)
        self.item_spacing: int = config.get("item_spacing", 6)

        self.factory = ElementsFactory({
            "screen": self.screen,
            "window": self.window,
            "font": self.font,
            "color": self.color,
            "hover_color": self.hover_color,
            "sound_hover": self.sound_hover,
            "sound_touch": self.sound_touch,
        })
        self.button_dropdown = self.factory.create_TextButton({
            "position": (self.position[0] + self.font.size(self.text)[0], int(self.position[1])),
            "text": self.type_dropdown,
            "command1": lambda: setattr(self, "is_dropdown_open", not self.is_dropdown_open),
            "command2": self.command_dropdown if callable(self.command_dropdown) else None,
        })
        self._combo_hover_surface = self.font.render(f"{self.text}{self.type_dropdown}", True, self.hover_color)
        self.rect: dict[str, object] = {
            "button": pygame.Rect(*self.position, *self.font.size(self.text)),
            "dropdown": self.button_dropdown,
        }

    def _update_surfaces(self) -> None:
        self._text_surface = self.font.render(self.text, True, self.color)
        self._hover_surface = self.font.render(self.text, True, self.hover_color)
        if hasattr(self, "type_dropdown"):
            self._combo_hover_surface = self.font.render(f"{self.text}{self.type_dropdown}", True, self.hover_color)
        if hasattr(self, "rect") and isinstance(self.rect, dict):
            self.rect["button"] = pygame.Rect(*self.position, *self._text_surface.get_size())
        else:
            self.rect = pygame.Rect(*self.position, *self._text_surface.get_size())

    def move(self, dx: int, dy: int) -> None:
        if dx == 0 and dy == 0:
            return
        self.position = (self.position[0] + dx, self.position[1] + dy)
        if isinstance(self.rect, dict) and "button" in self.rect:
            self.rect["button"].move_ip(dx, dy)
        self.button_dropdown.move(dx, dy)
        for btn in self.option_buttons.values():
            btn.move(dx, dy)
        if hasattr(self, "scroll"):
            self.scroll.move(dx, dy)
        if hasattr(self, "dropdown_rect") and isinstance(self.dropdown_rect, pygame.Rect):
            self.dropdown_rect.move_ip(dx, dy)

    def get_icon(self) -> str:
        raise NotImplementedError

    def is_vertical(self) -> bool:
        return False

    def _get_rect_dropdown(self) -> pygame.Rect:
        raise NotImplementedError

    def _adapt_size_dropdown(self) -> None:
        raise NotImplementedError

    def _check_buttons_position(self, i: int, text: str = "", first: bool = False) -> tuple[int, int]:
        raise NotImplementedError

    def _update_scroll_before_draw(self) -> None:
        pass

    def _post_repeat_charge(self, i: int, text: str, button: object) -> None:
        pass

    def _create_scroll(self) -> None:
        if self.is_vertical():
            self.scroll = self.factory.create_ScrollBar({
                "position": (self.position[0] + self.dropdown[0], self.position[1] + self.font.get_height(), 20, self.dropdown[1]),
                "type_of_orientation": "vertical",
                "thumb_height": 20,
                "color_bar": (135, 206, 235),
            })
        else:
            self.scroll = self.factory.create_ScrollBar({
                "position": (
                    self.position[0] + (self.font.size(self.text)[0] + self.font.size(self.type_dropdown)[0]),
                    int(self.position[1] + (self.font.get_height() / 2) + self.dropdown[1]),
                    self.dropdown[0],
                    20,
                ),
                "type_of_orientation": "horizontal",
                "thumb_width": 20,
                "color_bar": (135, 206, 235),
            })

    def draw(self) -> None:
        self.screen.blit(self._text_surface, self.position)
        self.button_dropdown.draw()
        if self.is_dropdown_open:
            self.draw_rect_dropdown()
        else:
            self.anim_height_dropdown = 0
            self.button_dropdown.change_item({"color": self.color})
        if self.detect_mouse:
            self.mouse_collision(self.rect["button"], self.get_mouse_pos(), self.draw_hover_effect)
        if self.pressed:
            self.pressed_button(self.rect["button"], pygame.mouse.get_pressed(), self.get_mouse_pos())

    def draw_hover_effect(self) -> pygame.Rect:
        return self.screen.blit(self._combo_hover_surface, self.position)

    def _visible_buttons(self) -> list:
        if self.replace_text:
            return [btn for btn in self.option_buttons.values() if btn.text != self.text]
        return list(self.option_buttons.values())

    def draw_rect_dropdown(self) -> None:
        self.button_dropdown.change_item({"color": self.hover_dropdown})
        if self.adapt_dropdown and self.option_buttons:
            self._adapt_size_dropdown()
        self.dropdown_rect = self._get_rect_dropdown()
        pygame.draw.rect(self.screen, self.hover_dropdown, self.dropdown_rect)
        pygame.draw.rect(self.screen, self.color, self.dropdown_rect, 2)
        if self.draw_scroll and self.option_buttons:
            self._rebuild_scroll()
        for button in self._visible_buttons():
            self._draw_option_buttons(button)
        if hasattr(self, "scroll"):
            self._draw_scroll()

    def _draw_option_buttons(self, button: object) -> None:
        if self._is_button_visible(button):
            button.draw()

    def _is_button_visible(self, button: object) -> bool:
        if self.is_vertical():
            return button.rect.bottom <= self.dropdown_rect.bottom and button.rect.top >= self.dropdown_rect.top
        else:
            return button.rect.right <= self.dropdown_rect.right and button.rect.left >= self.dropdown_rect.left

    def _draw_scroll(self) -> None:
        self._update_scroll_before_draw()
        self.scroll.draw()

    def _rebuild_scroll(self) -> None:
        self._create_scroll()
        if hasattr(self, "dropdown_rect") and isinstance(self.dropdown_rect, pygame.Rect):
            self.scroll.scroll_area = self.dropdown_rect
        self.rect["scroll"] = self.scroll.rect
        self.scroll.update_elements(self._visible_buttons())
        self.draw_scroll = False


    def charge_elements(self, options: dict) -> None:
        self._last_layout_rect = None
        for i, (option, action) in enumerate(options.items()):
            pos = self._check_buttons_position(i, option, first=(i == 0))
            button = self.factory.create_TextButton({
                "text": option,
                "position": pos,
                "command1": lambda idx=i: self._select_option(idx) if self.replace_text else None,
                "command2": action if callable(action) else None,
            })
            self._last_layout_rect = button.rect
            self._repeat_charge(f"elements_{i}", option, button, i)
        if self.replace_text and self.text in self.option_buttons:
            self.charge_buttons([btn for btn in self.option_buttons.values() if btn.text != self.text], True)

    def charge_buttons(self, buttons: list, first: bool = False) -> None:
        self._last_layout_rect = None
        for i, button in enumerate(buttons):
            is_first = first if i == 0 else False
            button.position = self._check_buttons_position(i, button.text, is_first)
            if hasattr(button, "rect"):
                if isinstance(button.rect, pygame.Rect):
                    button.rect.topleft = button.position
                    self._last_layout_rect = button.rect
                elif isinstance(button.rect, dict) and "button" in button.rect:
                    button.rect["button"].topleft = button.position
                    self._last_layout_rect = button.rect["button"]
            self._repeat_charge(f"buttons_{i}", button.text, button, i)

    def _repeat_charge(self, key, text, button, i) -> None:
        self.option_buttons[text] = button
        self.rect[key] = button
        if text not in self.options:
            self.options.append(text)
        self._post_repeat_charge(i, text, button)

    def _select_option(self, index: int) -> None:
        if 0 <= index < len(self.options):
            self.text = self.options[index]
            self._update_surfaces()
            self.option_buttons[self.options[index]].position = self.position
            self.option_buttons[self.options[index]].rect = pygame.Rect(*self.position, *self.font.size(self.text))
            self.button_dropdown.change_item({"position": (self.position[0] + self.font.size(self.text)[0], int(self.position[1]))})
            self.button_dropdown.rect = pygame.Rect(self.button_dropdown.position, self.font.size(self.button_dropdown.text))
            self.is_dropdown_open = False
        self.charge_buttons([button for button in self.option_buttons.values() if button.text != self.text], True)
        self.adapt_dropdown = True
        self._adapt_size_dropdown()
        self._rebuild_scroll()

    def events(self, event) -> bool:
        if not self.visible or not self.enabled:
            return False
        if self.is_dropdown_open and hasattr(self, "scroll"):
            if self.scroll.events(event):
                return True
        return False

    def return_buttons(self, button: str):
        return self.option_buttons[button]


class ComboBoxDown(ComboBox):
    def get_icon(self) -> str:
        return " V"

    def is_vertical(self) -> bool:
        return True

    def _get_rect_dropdown(self) -> pygame.Rect:
        if self.anim_height_dropdown < self.dropdown[1]:
            self.anim_height_dropdown = min(self.dropdown[1], self.anim_height_dropdown + max(1, self.dropdown[1] // 15))
        return pygame.Rect(self.position[0], self.position[1] + self.font.get_height(), self.dropdown[0], self.anim_height_dropdown)

    def _adapt_size_dropdown(self) -> None:
        vis = self._visible_buttons()
        count = max(1, len(vis))
        self.dropdown[1] = self.padding_y * 2 + count * self.font.get_height() + max(0, count - 1) * self.item_spacing
        if vis:
            max_w = max(self.font.size(b.text)[0] for b in vis)
            self.dropdown[0] = max(self.dropdown[0], max_w + self.padding_x * 2)
        self.adapt_dropdown = False

    def _check_buttons_position(self, i: int, text: str = "", first: bool = False) -> tuple[int, int]:
        x = int(self.position[0] + self.padding_x)
        if self._last_layout_rect is None or first:
            y = int(self.position[1] + self.font.get_height() + self.padding_y)
        else:
            y = int(self._last_layout_rect.bottom + self.item_spacing)
        return (x, y)

    def _update_scroll_before_draw(self) -> None:
        self.scroll.rect["rect"].height = self.dropdown_rect.height

    def _post_repeat_charge(self, i: int, text: str, button: object) -> None:
        self.dropdown[0] = max(self.dropdown[0], self.font.size(button.text)[0] + self.padding_x * 2)


class ComboBoxUp(ComboBox):
    def get_icon(self) -> str:
        return " ^"

    def is_vertical(self) -> bool:
        return True

    def _get_rect_dropdown(self) -> pygame.Rect:
        if self.anim_height_dropdown < self.dropdown[1]:
            self.anim_height_dropdown = min(self.dropdown[1], self.anim_height_dropdown + max(1, self.dropdown[1] // 15))
        return pygame.Rect(self.position[0], self.position[1] - self.anim_height_dropdown, self.dropdown[0], self.anim_height_dropdown)

    def _adapt_size_dropdown(self) -> None:
        vis = self._visible_buttons()
        count = max(1, len(vis))
        self.dropdown[1] = self.padding_y * 2 + count * self.font.get_height() + max(0, count - 1) * self.item_spacing
        if vis:
            max_w = max(self.font.size(b.text)[0] for b in vis)
            self.dropdown[0] = max(self.dropdown[0], max_w + self.padding_x * 2)
        self.adapt_dropdown = False

    def _check_buttons_position(self, i: int, text: str = "", first: bool = False) -> tuple[int, int]:
        x = int(self.position[0] + self.padding_x)
        if self._last_layout_rect is None or first:
            y = int(self.position[1] - self.font.get_height() - self.padding_y)
        else:
            y = int(self._last_layout_rect.top - self.font.get_height() - self.item_spacing)
        return (x, y)

    def _update_scroll_before_draw(self) -> None:
        if self.dropdown_rect.height != self.dropdown[1]:
            self.scroll.rect["rect"].y = self.scroll.rect["thumb"].y = self.dropdown_rect.y
        self.scroll.rect["rect"].height = self.dropdown_rect.height

    def _post_repeat_charge(self, i: int, text: str, button: object) -> None:
        self.dropdown[0] = max(self.dropdown[0], self.font.size(button.text)[0] + self.padding_x * 2)


class ComboBoxRight(ComboBox):
    def get_icon(self) -> str:
        return " >"

    def _dropdown_start_x(self) -> int:
        return int(self.position[0] + self.font.size(self.text)[0] + self.font.size(self.type_dropdown)[0] + 4)

    def _dropdown_top_y(self) -> int:
        return int(self.position[1] - self.padding_y // 2)

    def _get_rect_dropdown(self) -> pygame.Rect:
        if self.anim_height_dropdown < self.dropdown[0]:
            self.anim_height_dropdown = min(self.dropdown[0], self.anim_height_dropdown + max(1, self.dropdown[0] // 15))
        return pygame.Rect(self._dropdown_start_x(), self._dropdown_top_y(), self.anim_height_dropdown, self.dropdown[1])

    def _adapt_size_dropdown(self) -> None:
        vis = self._visible_buttons()
        if vis:
            left_bound = min(b.rect.left for b in vis)
            right_bound = max(b.rect.right for b in vis)
            self.dropdown[0] = (right_bound - left_bound) + self.padding_x * 2
        self.dropdown[1] = self.font.get_height() + self.padding_y * 2
        self.adapt_dropdown = False

    def _check_buttons_position(self, i: int, text: str = "", first: bool = False) -> tuple[int, int]:
        y = int(self._dropdown_top_y() + self.padding_y)
        if self._last_layout_rect is None or first:
            x = int(self._dropdown_start_x() + self.padding_x)
        else:
            x = int(self._last_layout_rect.right + self.item_spacing * 2)
        return (x, y)

    def _update_scroll_before_draw(self) -> None:
        self.scroll.rect["rect"].x = self.dropdown_rect.x
        self.scroll.rect["rect"].y = self.dropdown_rect.bottom
        self.scroll.rect["thumb"].y = self.dropdown_rect.bottom
        self.scroll.rect["rect"].width = self.dropdown_rect.width
        self.scroll.rect["thumb"].x = max(
            self.scroll.rect["rect"].left,
            min(self.scroll.rect["thumb"].x, self.scroll.rect["rect"].right - self.scroll.thumb_size),
        )


class ComboBoxLeft(ComboBox):
    def get_icon(self) -> str:
        return " <"

    def _dropdown_top_y(self) -> int:
        return int(self.position[1] - self.padding_y // 2)

    def _get_rect_dropdown(self) -> pygame.Rect:
        if self.anim_height_dropdown < self.dropdown[0]:
            self.anim_height_dropdown = min(self.dropdown[0], self.anim_height_dropdown + max(1, self.dropdown[0] // 15))
        return pygame.Rect(self.position[0] - self.anim_height_dropdown - 4, self._dropdown_top_y(), self.anim_height_dropdown, self.dropdown[1])

    def _adapt_size_dropdown(self) -> None:
        vis = self._visible_buttons()
        if vis:
            left_bound = min(b.rect.left for b in vis)
            right_bound = max(b.rect.right for b in vis)
            self.dropdown[0] = (right_bound - left_bound) + self.padding_x * 2
        self.dropdown[1] = self.font.get_height() + self.padding_y * 2
        self.adapt_dropdown = False

    def _check_buttons_position(self, i: int, text: str = "", first: bool = False) -> tuple[int, int]:
        y = int(self._dropdown_top_y() + self.padding_y)
        if self._last_layout_rect is None or first:
            x = int(self.position[0] - self.font.size(text)[0] - self.padding_x - 4)
        else:
            x = int(self._last_layout_rect.left - self.font.size(text)[0] - self.item_spacing * 2)
        return (x, y)

    def _update_scroll_before_draw(self) -> None:
        self.scroll.rect["rect"].y = self.dropdown_rect.bottom
        self.scroll.rect["thumb"].y = self.dropdown_rect.bottom
        if self.dropdown_rect.width != self.dropdown[0]:
            self.scroll.rect["rect"].x = self.scroll.rect["thumb"].x = self.dropdown_rect.x
        else:
            self.scroll.rect["rect"].x = self.dropdown_rect.x
        self.scroll.rect["rect"].width = self.dropdown_rect.width

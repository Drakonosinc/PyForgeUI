import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pygame
from pyforgeui import ElementsFactory, UIManager


class TestPyForgeUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        cls.screen = pygame.display.set_mode((1024, 768))
        cls.factory = ElementsFactory({"screen": cls.screen})

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_text_and_buttons(self) -> None:
        txt = self.factory.create_Text({"position": (10, 10), "text": "Hello"})
        btn = self.factory.create_TextButton({"position": (10, 40), "text": "Click"})
        poly = self.factory.create_PolygonButton({"position": [(10, 80), (50, 80), (30, 110)]})
        txt.draw()
        btn.draw()
        poly.draw()
        txt.change_item({"text": "Updated", "position": (20, 20)})
        self.assertEqual(txt.position, (20, 20))
        self.assertEqual(txt.rect.topleft, (20, 20))

    def test_checkbox_and_toggle(self) -> None:
        chk = self.factory.create_CheckBox({"position": (10, 10), "text": "VSync", "checked": False})
        tog = self.factory.create_ToggleSwitch({"position": (10, 50), "text": "Fullscreen", "value": False})
        self.assertTrue(chk.toggle())
        self.assertTrue(tog.toggle())
        chk.draw()
        tog.draw()

    def test_slider_and_progressbar(self) -> None:
        sld = self.factory.create_Slider({"position": (10, 10, 200, 12), "min_value": 0, "max_value": 100, "step": 5, "value": 25})
        sld.set_value(73)
        self.assertEqual(sld.get_value(), 75.0)
        prg = self.factory.create_ProgressBar({"position": (10, 40, 200, 24), "value": 50, "max_value": 100})
        prg.set_value(90)
        self.assertEqual(prg.get_value(), 90.0)
        sld.draw()
        prg.draw()

    def test_combobox_all_directions_and_spacing(self) -> None:
        for direction in ("down", "up", "right", "left"):
            cb = self.factory.create_ComboBox({
                "position": (400, 300),
                "text": "Ultra",
                "type_dropdown": direction,
                "replace_text": True,
            })
            cb.charge_elements({"Low": None, "Medium": None, "High": None, "Ultra": None})
            cb.is_dropdown_open = True
            for _ in range(15):
                cb.draw()
            cb._select_option(0)
            vis = cb._visible_buttons()
            self.assertEqual(len(vis), 3)
            # Ensure no two visible option buttons overlap
            for i in range(len(vis)):
                for j in range(i + 1, len(vis)):
                    self.assertFalse(
                        vis[i].rect.colliderect(vis[j].rect),
                        f"Overlap in ComboBox ({direction}): {vis[i].text} {vis[i].rect} vs {vis[j].text} {vis[j].rect}",
                    )

    def test_scrollbar_mousewheel(self) -> None:
        items = [self.factory.create_Text({"position": (100, 100 + i * 30), "text": f"Row {i}"}) for i in range(10)]
        sb = self.factory.create_ScrollBar({
            "position": (300, 100, 20, 120),
            "type_of_orientation": "vertical",
            "scroll_area": pygame.Rect(100, 100, 220, 120),
        })
        sb.update_elements(items)
        initial_y = items[0].position[1]
        wheel_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (150, 130), "button": 5})
        consumed = sb.events(wheel_down)
        self.assertTrue(consumed)
        self.assertLess(items[0].position[1], initial_y)
        # Item 0 scrolled above scroll_area.top (100) must be occluded from mouse clicks
        self.assertTrue(items[0]._is_occluded_by_popup(items[0].rect, (110, 95)))

    def test_containers_and_uimanager(self) -> None:
        ui = self.factory.create_UIManager()
        pnl = self.factory.create_Panel({"position": (50, 50, 300, 200), "title": "Panel", "draggable": True})
        spn = self.factory.create_NumberSpinner({"position": (70, 100, 120, 30), "value": 5})
        pnl.add_child(spn)
        mdl = self.factory.create_Modal({"title": "Alert", "message": "Confirm?"})
        ui.add(pnl, mdl)
        old_x = spn.rect.x
        pnl.move(25, 10)
        self.assertEqual(spn.rect.x, old_x + 25)
        mdl.open()
        click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (80, 110), "button": 1})
        self.assertTrue(ui.events(click))
        self.assertEqual(spn.get_value(), 5)  # Blocked by modal!

    def test_combobox_occlusion_and_mutual_exclusion(self) -> None:
        underneath_clicked = []
        option_clicked = []

        cb_top = self.factory.create_ComboBox({
            "position": (10, 100),
            "text": "Training",
            "type_dropdown": "down",
        })
        cb_top.charge_elements({
            "Genetic": lambda: option_clicked.append("Genetic"),
            "Q-learning": lambda: option_clicked.append("Q-learning"),
        })

        cb_bottom = self.factory.create_ComboBox({
            "position": (10, 130),
            "text": "Model",
            "type_dropdown": "down",
        })
        cb_bottom.charge_elements({"Pytorch": None, "Tensorflow": None})

        btn_under = self.factory.create_TextButton({
            "position": (10, 155),
            "text": "AI parameters",
            "command1": lambda: underneath_clicked.append(True),
        })

        # Open bottom first, then open top -> bottom must auto-close!
        cb_bottom.is_dropdown_open = True
        self.assertTrue(cb_bottom.is_dropdown_open)
        cb_top.is_dropdown_open = True
        self.assertTrue(cb_top.is_dropdown_open)
        self.assertFalse(cb_bottom.is_dropdown_open)

        # Draw enough frames to expand cb_top
        for _ in range(15):
            cb_top.draw()
            cb_bottom.draw()
            btn_under.draw()

        # Verify btn_under and cb_bottom are occluded by cb_top's open dropdown
        self.assertTrue(btn_under._is_visual_occluded_by_popup(btn_under.rect))
        self.assertTrue(cb_bottom._is_visual_occluded_by_popup(cb_bottom.get_header_rect()))

        # Attempting to click btn_under while cb_top is open must be blocked
        overlap_pos = (btn_under.rect.centerx, btn_under.rect.centery)
        btn_under.pressed_button(btn_under.rect, (True, False, False), overlap_pos, draw=lambda: None)
        btn_under.pressed_button(btn_under.rect, (False, False, False), overlap_pos, draw=lambda: None)
        self.assertEqual(len(underneath_clicked), 0)

        # Selecting an option in cb_top closes cb_top and blocks same-frame click-through
        q_btn = cb_top.return_buttons("Q-learning")
        q_pos = (q_btn.rect.centerx, q_btn.rect.centery)
        q_btn.pressed_button(q_btn.rect, (True, False, False), q_pos, draw=lambda: None)
        q_btn.pressed_button(q_btn.rect, (False, False, False), q_pos, draw=lambda: None)
        self.assertEqual(option_clicked, ["Q-learning"])
        self.assertFalse(cb_top.is_dropdown_open)

        # Immediate click check on btn_under on the same frame must also be blocked
        btn_under.pressed_button(btn_under.rect, (False, False, False), overlap_pos, draw=lambda: None)
        self.assertEqual(len(underneath_clicked), 0)


if __name__ == "__main__":
    unittest.main()

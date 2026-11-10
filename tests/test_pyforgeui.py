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


if __name__ == "__main__":
    unittest.main()

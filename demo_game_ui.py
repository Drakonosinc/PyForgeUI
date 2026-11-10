import os
import sys
import pygame

# Allow running demo directly from repo root or after pip install pyforgeui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pyforgeui import ElementsFactory



def make_icon_surface(size: tuple[int, int], bg_color: tuple, accent_color: tuple, shape: str = "sword") -> pygame.Surface:
    """Generates procedural game item icons so the demo runs standalone with zero external assets."""
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (*bg_color, 255), (0, 0, w, h), border_radius=8)
    pygame.draw.rect(surf, accent_color, (0, 0, w, h), 2, border_radius=8)

    cx, cy = w // 2, h // 2
    if shape == "sword":
        pygame.draw.line(surf, accent_color, (12, h - 12), (w - 12, 12), 4)
        pygame.draw.line(surf, (220, 220, 230), (14, h - 22), (22, h - 14), 3)
    elif shape == "shield":
        pts = [(cx, 10), (w - 12, 16), (w - 16, h - 18), (cx, h - 8), (16, h - 18), (12, 16)]
        pygame.draw.polygon(surf, accent_color, pts, 3)
    elif shape == "potion":
        pygame.draw.circle(surf, accent_color, (cx, cy + 5), 12)
        pygame.draw.rect(surf, (230, 235, 245), (cx - 4, 10, 8, 8))
    elif shape == "gem":
        pts = [(cx, 10), (w - 10, cy), (cx, h - 10), (10, cy)]
        pygame.draw.polygon(surf, accent_color, pts)
    elif shape == "crest":
        pygame.draw.circle(surf, accent_color, (cx, cy), min(w, h) // 3, 3)
        pygame.draw.polygon(surf, accent_color, [(cx, 10), (cx + 8, cy), (cx, h - 10), (cx - 8, cy)])
    else:
        pygame.draw.circle(surf, accent_color, (cx, cy), 10)
    return surf


class GameUIDemo:
    """
    Full multi-screen RPG Game Interface Showcase for PyForgeUI.
    Screens:
      1. MAIN MENU      (Title, Navigation StackLayout, Quit Confirmation Modal)
      2. CHARACTER & HUD (Draggable Stats Panel, ProgressBars, NumberSpinners, Inventory GridLayout + ScrollBar)
      3. SETTINGS       (TabContainer with Graphics, Audio, and Controls pages)
    """

    def __init__(self, max_frames: int | None = None) -> None:
        pygame.init()
        self.width, self.height = 1024, 680
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("PyForgeUI - Complete RPG Interface Showcase")
        self.clock = pygame.time.Clock()
        self.running = True
        self.max_frames = max_frames
        self.frame_count = 0

        self.font_title = pygame.font.Font(None, 52)
        self.font_header = pygame.font.Font(None, 32)
        self.font_body = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        self.factory = ElementsFactory({
            "screen": self.screen,
            "font": self.font_body,
            "color": (235, 240, 250),
            "hover_color": (255, 199, 51),
            "color_back": (38, 42, 52),
        })

        self.screens = {
            "menu": self.factory.create_UIManager({"font": self.font_small}),
            "game": self.factory.create_UIManager({"font": self.font_small}),
            "settings": self.factory.create_UIManager({"font": self.font_small}),
        }
        self.current_screen = "menu"
        self.selected_item_text = None

        self._build_main_menu()
        self._build_game_hud_screen()
        self._build_settings_screen()

    def switch_screen(self, name: str) -> None:
        if name in self.screens:
            self.current_screen = name

    # ------------------------------------------------------------------
    # SCREEN 1: MAIN MENU
    # ------------------------------------------------------------------
    def _build_main_menu(self) -> None:
        ui = self.screens["menu"]

        crest_surf = make_icon_surface((84, 84), (32, 38, 52), (255, 199, 51), "crest")
        crest_img = self.factory.create_Image({
            "position": (self.width // 2 - 42, 70),
            "surface": crest_surf,
            "tooltip": "PyForgeUI Engine Crest",
        })

        title = self.factory.create_Text({
            "position": (self.width // 2 - 195, 175),
            "font": self.font_title,
            "text": "CHRONICLES OF FORGE",
            "color": (255, 215, 90),
            "detect_mouse": False,
        })

        subtitle = self.factory.create_Text({
            "position": (self.width // 2 - 150, 225),
            "font": self.font_body,
            "text": "PyForgeUI Interactive Game Interface",
            "color": (170, 180, 200),
            "detect_mouse": False,
        })

        menu_panel = self.factory.create_Panel({
            "position": (self.width // 2 - 160, 270, 320, 250),
            "title": "MAIN NAVIGATION",
            "color_back": (28, 32, 42),
            "header_color": (44, 50, 66),
            "draggable": False,
        })

        btn_start = self.factory.create_TextButton({
            "position": (0, 0),
            "font": self.font_header,
            "text": ">> Enter Game HUD",
            "tooltip": "Open the live RPG Character, Inventory & HUD screen",
            "command1": lambda: self.switch_screen("game"),
        })
        btn_settings = self.factory.create_TextButton({
            "position": (0, 0),
            "font": self.font_header,
            "text": ">> Game Settings",
            "tooltip": "Configure Graphics, Audio & Keybinds",
            "command1": lambda: self.switch_screen("settings"),
        })
        btn_quit = self.factory.create_TextButton({
            "position": (0, 0),
            "font": self.font_header,
            "text": ">> Quit to Desktop",
            "color": (255, 120, 120),
            "tooltip": "Open confirmation modal dialog",
            "command1": lambda: self.quit_modal.open(),
        })

        menu_stack = self.factory.create_StackLayout({
            "position": (self.width // 2 - 115, 325),
            "orientation": "vertical",
            "spacing": 28,
            "children": [btn_start, btn_settings, btn_quit],
        })
        menu_panel.add_child(menu_stack)

        # Decorative PolygonButtons on the sides
        left_arrow = self.factory.create_PolygonButton({
            "position": [(self.width // 2 - 210, 390), (self.width // 2 - 180, 375), (self.width // 2 - 180, 405)],
            "color": (120, 170, 240),
            "tooltip": "Quick Jump: Settings Screen",
            "command1": lambda: self.switch_screen("settings"),
        })
        right_arrow = self.factory.create_PolygonButton({
            "position": [(self.width // 2 + 210, 390), (self.width // 2 + 180, 375), (self.width // 2 + 180, 405)],
            "color": (120, 170, 240),
            "tooltip": "Quick Jump: Game HUD Screen",
            "command1": lambda: self.switch_screen("game"),
        })

        self.quit_modal = self.factory.create_Modal({
            "title": "EXIT GAME",
            "message": "Are you sure you want to exit\nChronicles of Forge?",
            "confirm_text": "Yes, Exit",
            "cancel_text": "Stay",
            "on_confirm": self._stop_demo,
        })

        ui.add(crest_img, title, subtitle, menu_panel, left_arrow, right_arrow, self.quit_modal)

    def _stop_demo(self) -> None:
        self.running = False

    # ------------------------------------------------------------------
    # SCREEN 2: GAME HUD, DRAGGABLE CHARACTER PANEL & INVENTORY
    # ------------------------------------------------------------------
    def _build_game_hud_screen(self) -> None:
        ui = self.screens["game"]

        # Top Navigation Bar Panel
        top_bar = self.factory.create_Panel({
            "position": (20, 15, self.width - 40, 52),
            "color_back": (26, 30, 38),
            "border_color": (85, 95, 115),
        })
        btn_back_menu = self.factory.create_TextButton({
            "position": (35, 30),
            "text": "< Main Menu",
            "tooltip": "Return to Title Screen",
            "command1": lambda: self.switch_screen("menu"),
        })
        btn_to_settings = self.factory.create_TextButton({
            "position": (180, 30),
            "text": "Settings >",
            "tooltip": "Open Options & Controls",
            "command1": lambda: self.switch_screen("settings"),
        })
        hud_title = self.factory.create_Text({
            "position": (340, 28),
            "font": self.font_header,
            "text": "HERO LOADOUT & HUD",
            "color": (255, 205, 75),
            "detect_mouse": False,
        })
        btn_damage_test = self.factory.create_TextButton({
            "position": (680, 30),
            "text": "[-15 HP]",
            "color": (255, 110, 110),
            "tooltip": "Simulate taking damage on the HP ProgressBar",
            "command1": lambda: self.hp_bar.set_value(self.hp_bar.get_value() - 15),
        })
        btn_heal_test = self.factory.create_TextButton({
            "position": (780, 30),
            "text": "[+20 HP]",
            "color": (110, 240, 140),
            "tooltip": "Simulate healing on the HP ProgressBar",
            "command1": lambda: self.hp_bar.set_value(self.hp_bar.get_value() + 20),
        })
        btn_xp_test = self.factory.create_TextButton({
            "position": (885, 30),
            "text": "[+25 XP]",
            "color": (125, 195, 255),
            "tooltip": "Gain experience points",
            "command1": lambda: self.xp_bar.set_value((self.xp_bar.get_value() + 25) % 105),
        })
        top_bar.add_child(btn_back_menu)
        top_bar.add_child(btn_to_settings)
        top_bar.add_child(hud_title)
        top_bar.add_child(btn_damage_test)
        top_bar.add_child(btn_heal_test)
        top_bar.add_child(btn_xp_test)

        # HUD Status Panel (Left top)
        hud_panel = self.factory.create_Panel({
            "position": (20, 82, 460, 215),
            "title": "PLAYER STATUS (HUD)",
            "draggable": False,
        })
        lbl_name = self.factory.create_Text({
            "position": (35, 124),
            "text": "Hero Name:",
            "detect_mouse": False,
        })
        self.hero_input = self.factory.create_InputText({
            "position": (145, 118, 190, 28),
            "text": "Arthas",
            "color": (20, 20, 25),
            "color_back": (235, 240, 250),
            "tooltip": "Click to edit your Hero's name",
        })
        self.hp_bar = self.factory.create_ProgressBar({
            "position": (35, 160, 420, 24),
            "min_value": 0,
            "max_value": 100,
            "value": 85,
            "label": "Health",
            "fill_color": (220, 65, 65),
            "tooltip": "Current Hero Health Points",
        })
        self.mana_bar = self.factory.create_ProgressBar({
            "position": (35, 195, 420, 24),
            "min_value": 0,
            "max_value": 100,
            "value": 60,
            "label": "Mana",
            "fill_color": (70, 140, 235),
            "tooltip": "Current Arcane Mana Pool",
        })
        self.xp_bar = self.factory.create_ProgressBar({
            "position": (35, 230, 420, 20),
            "min_value": 0,
            "max_value": 100,
            "value": 40,
            "label": "Experience",
            "show_percentage": True,
            "fill_color": (185, 130, 255),
            "tooltip": "Experience progress toward next level",
        })
        hud_panel.add_child(lbl_name)
        hud_panel.add_child(self.hero_input)
        hud_panel.add_child(self.hp_bar)
        hud_panel.add_child(self.mana_bar)
        hud_panel.add_child(self.xp_bar)

        # Draggable Character Attributes Panel (Left bottom)
        stats_panel = self.factory.create_Panel({
            "position": (20, 312, 460, 345),
            "title": "ATTRIBUTES & CLASS (DRAG HEADER!)",
            "draggable": True,
            "tooltip": "Drag this window header to reposition it anywhere!",
        })

        lbl_str = self.factory.create_Text({"position": (40, 362), "text": "Strength (STR):", "detect_mouse": False})
        spn_str = self.factory.create_NumberSpinner({
            "position": (220, 355, 130, 30),
            "value": 14,
            "min_value": 1,
            "max_value": 99,
            "tooltip": "Increases melee physical damage",
        })

        lbl_agi = self.factory.create_Text({"position": (40, 405), "text": "Agility (AGI):", "detect_mouse": False})
        spn_agi = self.factory.create_NumberSpinner({
            "position": (220, 398, 130, 30),
            "value": 11,
            "min_value": 1,
            "max_value": 99,
            "tooltip": "Increases dodge and attack speed",
        })

        lbl_int = self.factory.create_Text({"position": (40, 448), "text": "Intelligence (INT):", "detect_mouse": False})
        spn_int = self.factory.create_NumberSpinner({
            "position": (220, 441, 130, 30),
            "value": 18,
            "min_value": 1,
            "max_value": 99,
            "tooltip": "Increases spell power and mana regeneration",
        })

        lbl_stance = self.factory.create_Text({"position": (40, 495), "text": "Combat Stance:", "color": (255, 205, 75), "detect_mouse": False})
        self.stance_group = self.factory.create_RadioGroup()
        r_aggressive = self.factory.create_RadioButton({
            "position": (40, 525),
            "text": "Berserker (+25% DMG)",
            "group": self.stance_group,
            "selected": True,
            "tooltip": "High offense, lower defense",
        })
        r_defensive = self.factory.create_RadioButton({
            "position": (40, 560),
            "text": "Guardian (+30% Armor)",
            "group": self.stance_group,
            "tooltip": " Reduces incoming physical damage",
        })
        r_balanced = self.factory.create_RadioButton({
            "position": (40, 595),
            "text": "Balanced (tactical)",
            "group": self.stance_group,
            "tooltip": "No penalties, steady stamina recovery",
        })

        for child in (lbl_str, spn_str, lbl_agi, spn_agi, lbl_int, spn_int, lbl_stance, r_aggressive, r_defensive, r_balanced):
            stats_panel.add_child(child)

        # Right side: Inventory GridLayout + Quest Log with ScrollBar
        inv_panel = self.factory.create_Panel({
            "position": (500, 82, 504, 310),
            "title": "BACKPACK INVENTORY (GRID LAYOUT)",
            "draggable": False,
        })

        self.selected_item_text = self.factory.create_Text({
            "position": (520, 355),
            "text": "Selected Item: Click an icon slot above",
            "color": (140, 220, 255),
            "detect_mouse": False,
        })

        item_Catalog = [
            ("Flameblade", "sword", (240, 95, 70), "Legendary Fire Sword (+45 ATK)"),
            ("Aegis Shield", "shield", (90, 175, 250), "Tower Shield (+30 DEF)"),
            ("Health Elixir", "potion", (235, 75, 115), "Restores 50 Health instantly"),
            ("Mana Vial", "potion", (75, 145, 250), "Restores 40 Mana instantly"),
            ("Soul Sapphire", "gem", (110, 225, 255), "Rare crafting catalyst"),
            ("Ruby Heart", "gem", (255, 85, 95), "Socketable +10% Max HP gem"),
            ("Shadow Dagger", "sword", (185, 120, 255), "Quick off-hand blade (+22 Crit)"),
            ("Oak Buckler", "shield", (215, 165, 95), "Lightweight parrying shield"),
            ("Emerald Shard", "gem", (85, 230, 135), "Poison enchantment stone"),
            ("Sun Crest", "crest", (255, 210, 75), "Key item: Opens the Sun Temple"),
            ("Frostbrand", "sword", (110, 215, 255), "Chills enemies on hit"),
            ("Stamina Brew", "potion", (115, 225, 115), "Boosts energy recovery"),
        ]

        slot_buttons = []
        for name, shape, accent, desc in item_Catalog:
            icon_surf = make_icon_surface((58, 58), (46, 52, 66), accent, shape)
            btn = self.factory.create_ImageButton({
                "position": (0, 0),
                "surface": icon_surf,
                "border": 2,
                "border_color": (90, 100, 120),
                "tooltip": f"{name}: {desc}",
                "command1": lambda n=name, d=desc: self.selected_item_text.change_item({"text": f"Equipped: {n} - {d}"}),
            })
            slot_buttons.append(btn)

        inv_grid = self.factory.create_GridLayout({
            "position": (525, 125),
            "columns": 6,
            "cell_size": (62, 62),
            "spacing_x": 14,
            "spacing_y": 14,
            "children": slot_buttons,
        })
        inv_panel.add_child(inv_grid)
        inv_panel.add_child(self.selected_item_text)

        # Quest Log with ScrollBar + ComboBox filter
        quest_panel = self.factory.create_Panel({
            "position": (500, 408, 504, 249),
            "title": "QUEST LOG & COMBOBOX FILTER",
            "clip_children": True,
        })

        quest_entries = [
            "[Main] Defeat the Obsidian Dragon in Peak",
            "[Guild] Deliver 5 Soul Sapphires to Blacksmith",
            "[Side] Explore the Sunken Catacombs",
            "[Bounty] Hunt the Rogue Necromancer",
            "[Lore] Decipher the Ancient Runestones",
            "[Craft] Forge the Mythril Chestplate",
            "[Event] Defend the Citadel Gates",
            "[Secret] Find the Lost Crown of Kings",
        ]
        quest_texts = []
        for idx, q_str in enumerate(quest_entries):
            qt = self.factory.create_Text({
                "position": (520, 455 + idx * 32),
                "text": q_str,
                "color": (215, 225, 240),
                "tooltip": f"Quest #{idx + 1} details",
            })
            quest_texts.append(qt)
            quest_panel.add_child(qt)

        quest_scroll = self.factory.create_ScrollBar({
            "position": (972, 448, 18, 195),
            "type_of_orientation": "vertical",
            "thumb_height": 42,
            "scroll_area": quest_panel.rect,
            "tooltip": "Drag or use Mouse Wheel to scroll through active quests",
        })

        quest_scroll.update_elements(quest_texts)
        quest_panel.add_child(quest_scroll)

        ui.add(top_bar, hud_panel, stats_panel, inv_panel, quest_panel)

    # ------------------------------------------------------------------
    # SCREEN 3: SETTINGS SCREEN (TAB CONTAINER: GRAPHICS, AUDIO, CONTROLS)
    # ------------------------------------------------------------------
    def _build_settings_screen(self) -> None:
        ui = self.screens["settings"]

        top_bar = self.factory.create_Panel({
            "position": (20, 15, self.width - 40, 52),
            "color_back": (26, 30, 38),
        })
        btn_back_menu = self.factory.create_TextButton({
            "position": (35, 30),
            "text": "< Main Menu",
            "command1": lambda: self.switch_screen("menu"),
        })
        btn_back_game = self.factory.create_TextButton({
            "position": (185, 30),
            "text": "< Back to Game HUD",
            "command1": lambda: self.switch_screen("game"),
        })
        settings_title = self.factory.create_Text({
            "position": (430, 28),
            "font": self.font_header,
            "text": "SYSTEM CONFIGURATION",
            "color": (255, 205, 75),
            "detect_mouse": False,
        })
        top_bar.add_child(btn_back_menu)
        top_bar.add_child(btn_back_game)
        top_bar.add_child(settings_title)

        tabs = self.factory.create_TabContainer({
            "position": (60, 95, self.width - 120, 540),
            "tabs": ["Graphics", "Audio", "Controls"],
        })

        # --- TAB 1: GRAPHICS ---
        chk_vsync = self.factory.create_CheckBox({
            "position": (0, 0),
            "text": "Enable Vertical Sync (V-Sync)",
            "checked": True,
            "tooltip": "Synchronizes frame rate with monitor refresh rate",
        })
        chk_shadows = self.factory.create_CheckBox({
            "position": (0, 0),
            "text": "Dynamic Soft Shadows",
            "checked": True,
            "tooltip": "Renders real-time shadows for units and terrain",
        })
        chk_bloom = self.factory.create_CheckBox({
            "position": (0, 0),
            "text": "Post-Processing Bloom & Glow",
            "checked": False,
            "tooltip": "Adds luminous glow around spells and torches",
        })
        tog_fullscreen = self.factory.create_ToggleSwitch({
            "position": (0, 0),
            "text": "Borderless Fullscreen Mode",
            "value": True,
            "tooltip": "Switch between windowed and borderless fullscreen",
        })
        tog_fps = self.factory.create_ToggleSwitch({
            "position": (0, 0),
            "text": "Show FPS Overlay Counter",
            "value": True,
            "tooltip": "Displays real-time performance metrics",
        })
        sld_fov = self.factory.create_Slider({
            "position": (0, 0, 260, 14),
            "min_value": 60,
            "max_value": 120,
            "step": 5,
            "value": 90,
            "label": "Camera Field of View (FOV)",
            "tooltip": "Adjust camera wide-angle perspective",
        })
        sld_gamma = self.factory.create_Slider({
            "position": (0, 0, 260, 14),
            "min_value": 50,
            "max_value": 150,
            "step": 1,
            "value": 100,
            "label": "Screen Brightness (%)",
            "tooltip": "Adjust display gamma brightness",
        })

        lbl_res = self.factory.create_Text({
            "position": (0, 0),
            "text": "Display Resolution Preset (ComboBox Down):",
            "color": (255, 205, 75),
            "detect_mouse": False,
        })
        combo_res = self.factory.create_ComboBox({
            "position": (520, 210),
            "text": "1920x1080",
            "type_dropdown": "down",
            "replace_text": True,
            "tooltip": "Click 'V' to open vertical resolution dropdown",
        })
        combo_res.charge_elements({
            "1280x720": None,
            "1600x900": None,
            "1920x1080": None,
            "2560x1440": None,
        })

        lbl_qual = self.factory.create_Text({
            "position": (0, 0),
            "text": "Texture Quality (ComboBox Right):",
            "color": (255, 205, 75),
            "detect_mouse": False,
        })
        combo_qual = self.factory.create_ComboBox({
            "position": (520, 380),
            "text": "Ultra",
            "type_dropdown": "right",
            "replace_text": True,
            "tooltip": "Click '>' to open horizontal quality dropdown",
        })
        combo_qual.charge_elements({
            "Low": None,
            "Medium": None,
            "High": None,
            "Ultra": None,
        })

        tabs.add_to_tab("Graphics", chk_vsync, (40, 45))
        tabs.add_to_tab("Graphics", chk_shadows, (40, 90))
        tabs.add_to_tab("Graphics", chk_bloom, (40, 135))
        tabs.add_to_tab("Graphics", tog_fullscreen, (40, 190))
        tabs.add_to_tab("Graphics", tog_fps, (40, 240))
        tabs.add_to_tab("Graphics", sld_fov, (40, 330))
        tabs.add_to_tab("Graphics", sld_gamma, (40, 405))
        tabs.add_to_tab("Graphics", lbl_res, (460, 45))
        tabs.add_to_tab("Graphics", combo_res)
        tabs.add_to_tab("Graphics", lbl_qual, (460, 215))
        tabs.add_to_tab("Graphics", combo_qual)

        # --- TAB 2: AUDIO ---
        sld_master = self.factory.create_Slider({
            "position": (0, 0, 340, 14),
            "min_value": 0,
            "max_value": 100,
            "step": 1,
            "value": 85,
            "label": "Master Volume",
            "tooltip": "Overall game sound output level",
        })
        sld_music = self.factory.create_Slider({
            "position": (0, 0, 340, 14),
            "min_value": 0,
            "max_value": 100,
            "step": 1,
            "value": 70,
            "label": "Orchestral Music Volume",
            "tooltip": "Background soundtrack volume",
        })
        sld_sfx = self.factory.create_Slider({
            "position": (0, 0, 340, 14),
            "min_value": 0,
            "max_value": 100,
            "step": 1,
            "value": 90,
            "label": "Combat & UI SFX Volume",
            "tooltip": "Sword clashes, spells, and button clicks",
        })
        sld_voice = self.factory.create_Slider({
            "position": (0, 0, 340, 14),
            "min_value": 0,
            "max_value": 100,
            "step": 1,
            "value": 95,
            "label": "NPC Voice Dialogue",
            "tooltip": "Character voice-over volume",
        })
        tog_mute_bg = self.factory.create_ToggleSwitch({
            "position": (0, 0),
            "text": "Mute Audio When Window Unfocused",
            "value": True,
        })
        chk_subtitles = self.factory.create_CheckBox({
            "position": (0, 0),
            "text": "Display Cinematic Subtitles",
            "checked": True,
        })

        tabs.add_to_tab("Audio", sld_master, (50, 70))
        tabs.add_to_tab("Audio", sld_music, (50, 145))
        tabs.add_to_tab("Audio", sld_sfx, (50, 220))
        tabs.add_to_tab("Audio", sld_voice, (50, 295))
        tabs.add_to_tab("Audio", tog_mute_bg, (50, 360))
        tabs.add_to_tab("Audio", chk_subtitles, (50, 415))

        # --- TAB 3: CONTROLS (KEYBINDS) ---
        lbl_kbd_help = self.factory.create_Text({
            "position": (0, 0),
            "text": "Click any KeybindButton below, then press a key on your keyboard (ESC to cancel):",
            "color": (180, 200, 230),
            "detect_mouse": False,
        })
        kb_jump = self.factory.create_KeybindButton({
            "position": (0, 0, 260, 36),
            "action_label": "Jump / Dodge",
            "key": pygame.K_SPACE,
            "tooltip": "Click and press any key to rebind Jump",
        })
        kb_attack = self.factory.create_KeybindButton({
            "position": (0, 0, 260, 36),
            "action_label": "Primary Attack",
            "key": pygame.K_q,
            "tooltip": "Click and press any key to rebind Primary Attack",
        })
        kb_skill = self.factory.create_KeybindButton({
            "position": (0, 0, 260, 36),
            "action_label": "Ultimate Skill",
            "key": pygame.K_r,
            "tooltip": "Click and press any key to rebind Ultimate Skill",
        })
        kb_inv = self.factory.create_KeybindButton({
            "position": (0, 0, 260, 36),
            "action_label": "Open Inventory",
            "key": pygame.K_i,
            "tooltip": "Click and press any key to rebind Inventory",
        })
        kb_interact = self.factory.create_KeybindButton({
            "position": (0, 0, 260, 36),
            "action_label": "Interact / Loot",
            "key": pygame.K_e,
            "tooltip": "Click and press any key to rebind Interact",
        })
        kb_map = self.factory.create_KeybindButton({
            "position": (0, 0, 260, 36),
            "action_label": "World Map",
            "key": pygame.K_m,
            "tooltip": "Click and press any key to rebind World Map",
        })

        tabs.add_to_tab("Controls", lbl_kbd_help, (45, 35))
        tabs.add_to_tab("Controls", kb_jump, (45, 85))
        tabs.add_to_tab("Controls", kb_attack, (45, 145))
        tabs.add_to_tab("Controls", kb_skill, (45, 205))
        tabs.add_to_tab("Controls", kb_inv, (360, 85))
        tabs.add_to_tab("Controls", kb_interact, (360, 145))
        tabs.add_to_tab("Controls", kb_map, (360, 205))

        ui.add(top_bar, tabs)

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------
    def run(self) -> None:
        while self.running:
            active_ui = self.screens[self.current_screen]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    active_ui.events(event)

            self.screen.fill((18, 21, 28))
            active_ui.draw()
            pygame.display.flip()
            self.clock.tick(60)

            self.frame_count += 1
            if self.max_frames is not None and self.frame_count >= self.max_frames:
                self.running = False

        pygame.quit()


if __name__ == "__main__":
    # Pass --test on CLI to run 30 frames across all screens automatically and exit cleanly
    if "--test" in sys.argv:
        demo = GameUIDemo(max_frames=15)
        for scr in ("menu", "game", "settings"):
            demo.switch_screen(scr)
            demo.screens[scr].draw()
        demo.run()
        print("DEMO MULTI-SCREEN VERIFICATION PASSED!")
    else:
        demo = GameUIDemo()
        demo.run()

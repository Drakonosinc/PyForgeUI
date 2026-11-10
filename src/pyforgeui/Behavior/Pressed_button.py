import pygame


class PressedButton:
    """Mixin providing click, release, hold-repeat, and command callback execution."""

    def __init__(self, config: dict) -> None:
        self.sound_touch = config.get("sound_touch", None)
        self.pressed: bool = config.get("pressed", True)
        if not hasattr(self, "states") or not isinstance(self.states, dict):
            self.states = {}
        self.states.update({
            "presses_touch": True,
            "click_time": None,
            "active": False,
            **config.get("states", {}),
        })
        self.repeat: bool = config.get("repeat_button", False)
        self.repeat_interval: int = config.get("repeat_interval", 200)
        num_cmds = config.get("number_commands", 4)
        self.commands: list = [config.get(f"command{i}") for i in range(1, num_cmds)]
        if callable(config.get("command")):
            self.commands.insert(0, config.get("command"))

    def pressed_button(self, rect: pygame.Rect, pressed_mouse: tuple, mouse_pos: tuple[int, int], draw=None, repeat: bool | None = None) -> bool:
        if not getattr(self, "visible", True) or not getattr(self, "enabled", True):
            return False

        fired = False

        def execute(sound=False, active=False, presses=True, time=None, command=True):
            nonlocal fired
            if sound and self.sound_touch:
                self.sound_touch.play(loops=0)
            self.states["active"] = active
            self.states["presses_touch"] = presses
            self.states["click_time"] = None if time is None else time
            if command:
                fired = True
                self.execute_commands()

        repeat = self.repeat if repeat is None else repeat
        current_time = pygame.time.get_ticks()

        if pressed_mouse[0] and rect.collidepoint(mouse_pos) and self.states["presses_touch"]:
            execute(False, True, False, current_time, False)

        if not repeat and not pressed_mouse[0] and self.states["active"]:
            if rect.collidepoint(mouse_pos):
                execute(True)
            else:
                self.states["active"] = False
                self.states["presses_touch"] = True
        elif self.states["click_time"] is not None and repeat:
            if pressed_mouse[0] and rect.collidepoint(mouse_pos):
                if current_time - self.states["click_time"] >= self.repeat_interval:
                    execute(True, active=True, presses=False, time=current_time, command=True)
            else:
                self.states["active"] = False
                self.states["presses_touch"] = True
                self.states["click_time"] = None

        if pressed_mouse[0] and not rect.collidepoint(mouse_pos) and self.states["active"]:
            self.states["active"], self.states["presses_touch"] = False, True

        if self.states["active"]:
            self.draw_pressed_effect() if draw is None else draw()

        return fired

    def draw_pressed_effect(self):
        return NotImplementedError

    def execute_commands(self, *args) -> None:
        if callable(self.commands):
            try:
                self.commands(*args)
            except TypeError:
                self.commands()
            return
        for command in self.commands:
            if callable(command):
                try:
                    command(*args)
                except TypeError:
                    command()

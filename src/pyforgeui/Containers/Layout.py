import pygame
from ..Behavior.Mouse_collision import MouseCollision


class StackLayout(MouseCollision):
    """Automatic vertical or horizontal box layout manager."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.orientation: str = config.get("orientation", "vertical").lower()
        self.spacing: int = config.get("spacing", 10)
        self.padding: int = config.get("padding", 8)
        self.children: list = []
        self.rect = pygame.Rect(int(self.position[0]), int(self.position[1]), 0, 0)
        for child in config.get("children", []):
            self.add_child(child)

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            self.reflow()
        return child

    def remove_child(self, child) -> None:
        if child in self.children:
            self.children.remove(child)
            self.reflow()

    def reflow(self) -> None:
        x_start = int(self.position[0]) + self.padding
        y_start = int(self.position[1]) + self.padding
        cx, cy = x_start, y_start
        max_w, max_h = 0, 0

        for child in self.children:
            if not getattr(child, "visible", True):
                continue
            if hasattr(child, "set_position"):
                child.set_position(cx, cy)
            bounds = child.get_bounding_rect() if hasattr(child, "get_bounding_rect") else getattr(child, "rect", pygame.Rect(cx, cy, 0, 0))
            if self.orientation == "vertical":
                cy += bounds.height + self.spacing
                max_w = max(max_w, bounds.width)
                max_h = cy - y_start - self.spacing
            else:
                cx += bounds.width + self.spacing
                max_h = max(max_h, bounds.height)
                max_w = cx - x_start - self.spacing

        self.rect = pygame.Rect(
            int(self.position[0]),
            int(self.position[1]),
            max(0, max_w + self.padding * 2),
            max(0, max_h + self.padding * 2),
        )

    def move(self, dx: int, dy: int) -> None:
        if dx == 0 and dy == 0:
            return
        super().move(dx, dy)
        for child in self.children:
            if hasattr(child, "move"):
                child.move(dx, dy)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        for child in self.children:
            if hasattr(child, "events") and child.events(event):
                return True
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        for child in self.children:
            if hasattr(child, "draw"):
                child.draw()


class GridLayout(MouseCollision):
    """Automatic 2D grid layout manager for inventory slots, skill trees, and button matrices."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.columns: int = max(1, int(config.get("columns", 3)))
        self.cell_size: tuple[int, int] | None = config.get("cell_size", None)
        self.spacing_x: int = config.get("spacing_x", config.get("spacing", 10))
        self.spacing_y: int = config.get("spacing_y", config.get("spacing", 10))
        self.padding: int = config.get("padding", 8)
        self.children: list = []
        self.rect = pygame.Rect(int(self.position[0]), int(self.position[1]), 0, 0)
        for child in config.get("children", []):
            self.add_child(child)

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            self.reflow()
        return child

    def remove_child(self, child) -> None:
        if child in self.children:
            self.children.remove(child)
            self.reflow()

    def reflow(self) -> None:
        x0 = int(self.position[0]) + self.padding
        y0 = int(self.position[1]) + self.padding
        if self.cell_size:
            cw, ch = self.cell_size
        else:
            cw, ch = 64, 32
            for child in self.children:
                b = child.get_bounding_rect() if hasattr(child, "get_bounding_rect") else getattr(child, "rect", None)
                if isinstance(b, pygame.Rect):
                    cw = max(cw, b.width)
                    ch = max(ch, b.height)

        visible_children = [c for c in self.children if getattr(c, "visible", True)]
        for idx, child in enumerate(visible_children):
            row = idx // self.columns
            col = idx % self.columns
            cx = x0 + col * (cw + self.spacing_x)
            cy = y0 + row * (ch + self.spacing_y)
            if hasattr(child, "set_position"):
                child.set_position(cx, cy)

        rows = (len(visible_children) + self.columns - 1) // self.columns if visible_children else 0
        cols = min(len(visible_children), self.columns) if visible_children else 0
        total_w = cols * cw + max(0, cols - 1) * self.spacing_x + self.padding * 2
        total_h = rows * ch + max(0, rows - 1) * self.spacing_y + self.padding * 2
        self.rect = pygame.Rect(int(self.position[0]), int(self.position[1]), total_w, total_h)

    def move(self, dx: int, dy: int) -> None:
        if dx == 0 and dy == 0:
            return
        super().move(dx, dy)
        for child in self.children:
            if hasattr(child, "move"):
                child.move(dx, dy)

    def events(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        for child in self.children:
            if hasattr(child, "events") and child.events(event):
                return True
        return False

    def draw(self) -> None:
        if not self.visible:
            return
        for child in self.children:
            if hasattr(child, "draw"):
                child.draw()

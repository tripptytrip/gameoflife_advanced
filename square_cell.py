# square_cell.py

import pygame
from settings import DEAD_CELL_COLOR, GRID_LINE_COLOR

class SquareCell:
    """
    Represents a single square cell in the grid.
    """

    def __init__(self, x, y, size, alive=False, lifeform_id=None):
        """
        Initialize a square cell.

        Args:
            x (int): Grid coordinate x.
            y (int): Grid coordinate y.
            size (int): Size of the square cell.
            alive (bool): State of the cell, alive or dead.
            lifeform_id (int or None): Identifier of the lifeform the cell belongs to.
        """
        self.x = x
        self.y = y
        self.size = size
        self.alive = alive
        self.neighbors = []
        self.alive_duration = 0  # Number of consecutive generations the cell has been alive
        self.lifeform_id = lifeform_id  # Lifeform identifier

    def get_position(self, offset_x, offset_y):
        """
        Calculate the pixel position of the square cell.
        """
        x = self.x * self.size
        y = self.y * self.size
        return (x + offset_x, y + offset_y)

    def draw(self, surface, offset_x, offset_y, lifeform=None):
        """
        Draw the square cell on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            offset_x (int): Horizontal offset for rendering.
            offset_y (int): Vertical offset for rendering.
            lifeform (Lifeform or None): The lifeform object associated with this cell.
        """
        # Determine the color based on lifeform and alive_duration
        if self.alive:
            if self.alive_duration > 10 and lifeform:
                color = lifeform.color_static
            elif lifeform:
                color = lifeform.color_alive
            else:
                color = DEAD_CELL_COLOR
        else:
            color = DEAD_CELL_COLOR

        rect = pygame.Rect(
            self.get_position(offset_x, offset_y),
            (self.size, self.size)
        )
        pygame.draw.rect(surface, color, rect)
        # Optional: Draw grid lines for better visibility
        pygame.draw.rect(surface, GRID_LINE_COLOR, rect, 1)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, SquareCell) and self.x == other.x and self.y == other.y

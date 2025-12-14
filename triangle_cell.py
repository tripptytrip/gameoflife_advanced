# triangle_cell.py

import pygame
import math
from settings import DEAD_CELL_COLOR, GRID_LINE_COLOR

class TriangleCell:
    """
    Represents a single triangular cell in the grid.
    """

    def __init__(self, x, y, size, upward=True, alive=False, lifeform_id=None):
        """
        Initialize a triangle cell.

        Args:
            x (int): Grid coordinate x.
            y (int): Grid coordinate y.
            size (int): Size of the triangle cell.
            upward (bool): Direction of the triangle (upward or downward).
            alive (bool): State of the cell, alive or dead.
            lifeform_id (int or None): Identifier of the lifeform the cell belongs to.
        """
        self.x = x
        self.y = y
        self.size = size
        self.upward = upward
        self.alive = alive
        self.neighbors = []
        self.alive_duration = 0  # Number of consecutive generations the cell has been alive
        self.lifeform_id = lifeform_id  # Lifeform identifier

    def get_position(self, offset_x, offset_y):
        """
        Calculate the pixel position of the triangle cell.
        """
        x = self.x * (self.size / 2)
        y = self.y * (self.size * math.sqrt(3) / 2)
        return (x + offset_x, y + offset_y)

    def draw(self, surface, offset_x, offset_y, lifeform=None):
        """
        Draw the triangle cell on the given surface.

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

        pygame.draw.polygon(surface, color, self.get_corners(offset_x, offset_y))
        # Optional: Draw grid lines for better visibility
        pygame.draw.polygon(surface, GRID_LINE_COLOR, self.get_corners(offset_x, offset_y), 1)

    @staticmethod
    def draw_static(surface, x, y, size, upward, offset_x, offset_y, lifeform=None, alive_duration=0):
        """
        Static method to draw a triangle cell on the given surface.
        """
        # Determine the color based on lifeform and alive_duration
        if lifeform:
            if alive_duration > 10:
                color = lifeform.color_static
            else:
                color = lifeform.color_alive
        else:
            color = DEAD_CELL_COLOR
        
        x0 = x * (size / 2) + offset_x
        y0 = y * (size * math.sqrt(3) / 2) + offset_y
        half_size = size / 2
        height = size * math.sqrt(3) / 2

        if upward:
            corners = [
                (x0, y0 - height / 2),
                (x0 - half_size, y0 + height / 2),
                (x0 + half_size, y0 + height / 2)
            ]
        else:
            corners = [
                (x0, y0 + height / 2),
                (x0 - half_size, y0 - height / 2),
                (x0 + half_size, y0 - height / 2)
            ]
        
        pygame.draw.polygon(surface, color, corners)
        # Optional: Draw grid lines for better visibility
        pygame.draw.polygon(surface, GRID_LINE_COLOR, corners, 1)

    def get_corners(self, offset_x, offset_y):
        """
        Calculate the corner positions of the triangle cell.
        """
        x0, y0 = self.get_position(offset_x, offset_y)
        half_size = self.size / 2
        height = self.size * math.sqrt(3) / 2

        if self.upward:
            corners = [
                (x0, y0 - height / 2),
                (x0 - half_size, y0 + height / 2),
                (x0 + half_size, y0 + height / 2)
            ]
        else:
            corners = [
                (x0, y0 + height / 2),
                (x0 - half_size, y0 - height / 2),
                (x0 + half_size, y0 - height / 2)
            ]
        return corners

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, TriangleCell) and self.x == other.x and self.y == other.y

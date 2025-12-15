# hexagon_cell.py

import pygame
import math
from settings import DEAD_CELL_COLOR, GRID_LINE_COLOR

class HexagonCell:
    """
    Represents a single hexagonal cell in the grid.
    """

    def __init__(self, q, r, size, alive=False, lifeform_id=None):
        """
        Initialize a hexagon cell.

        Args:
            q (int): Axial coordinate q.
            r (int): Axial coordinate r.
            size (int): Size (radius) of the hexagon.
            alive (bool): State of the cell, alive or dead.
            lifeform_id (int or None): Identifier of the lifeform the cell belongs to.
        """
        self.q = q
        self.r = r
        self.size = size
        self.alive = alive
        self.neighbors = []
        self.alive_duration = 0  # Number of consecutive generations the cell has been alive
        self.lifeform_id = lifeform_id  # Lifeform identifier

    def get_position(self, offset_x, offset_y):
        """
        Calculate the pixel position of the hexagon cell for flat-topped hexagons.
        """
        x = self.size * (3/2) * self.q
        y = self.size * math.sqrt(3) * (self.r + self.q / 2)
        return (x + offset_x, y + offset_y)

    def draw(self, surface, offset_x, offset_y, lifeform=None):
        """
        Draw the hexagon cell on the given surface.

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

        corners = self.get_corners(offset_x, offset_y)
        pygame.draw.polygon(surface, color, corners)
        # Optional: Draw grid lines for better visibility
        pygame.draw.polygon(surface, GRID_LINE_COLOR, corners, 1)

    @staticmethod
    def draw_static(surface, q, r, size, offset_x, offset_y, lifeform=None, alive_duration=0):
        """
        Static method to draw a hexagon cell on the given surface.
        """
        # Determine the color based on lifeform and alive_duration
        if lifeform:
            if alive_duration > 10:
                color = lifeform.color_static
            else:
                color = lifeform.color_alive
        else:
            color = DEAD_CELL_COLOR

        # odd-q offset coordinates so rows stay aligned into a rectangle
        center_x = size * 1.5 * q + offset_x
        center_y = size * math.sqrt(3) * (r + 0.5 * (q & 1)) + offset_y
        
        angles = [math.radians(60 * i) for i in range(6)]
        corners = [
            (center_x + size * math.cos(angle),
             center_y + size * math.sin(angle))
            for angle in angles
        ]
        
        pygame.draw.polygon(surface, color, corners)
        # Optional: Draw grid lines for better visibility
        pygame.draw.polygon(surface, GRID_LINE_COLOR, corners, 1)

    def get_corners(self, offset_x, offset_y):
        """
        Calculate the corner positions of the hexagon cell for flat-topped hexagons.
        """
        center_x, center_y = self.get_position(offset_x, offset_y)
        angles = [math.radians(60 * i) for i in range(6)]  # Correct angles for flat-topped hexagons
        corners = [
            (center_x + self.size * math.cos(angle),
            center_y + self.size * math.sin(angle))
            for angle in angles
        ]
        return corners

    def __hash__(self):
        return hash((self.q, self.r))

    def __eq__(self, other):
        return isinstance(other, HexagonCell) and self.q == other.q and self.r == other.r

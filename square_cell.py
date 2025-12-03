# square_cell.py

import pygame
from settings import DEAD_CELL_COLOR, GRID_LINE_COLOR

class SquareCell:
    """
    A stateless utility for drawing square cells.
    """

    @staticmethod
    def draw(surface, x, y, size, offset_x, offset_y, lifeform=None, alive_duration=0):
        """
        Draw a square cell on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            x (int): Grid coordinate x.
            y (int): Grid coordinate y.
            size (int): Size of the square cell.
            offset_x (int): Horizontal offset for rendering.
            offset_y (int): Vertical offset for rendering.
            lifeform (Lifeform or None): The lifeform object associated with this cell.
            alive_duration (int): Number of generations the cell has been alive.
        """
        # Determine the color based on lifeform and alive_duration
        if lifeform:
            if alive_duration > 10:
                color = lifeform.color_static
            else:
                color = lifeform.color_alive
        else:
            color = DEAD_CELL_COLOR

        # Calculate pixel position
        px = x * size + offset_x
        py = y * size + offset_y
        
        rect = pygame.Rect(px, py, size, size)
        pygame.draw.rect(surface, color, rect)
        # Optional: Draw grid lines for better visibility
        pygame.draw.rect(surface, GRID_LINE_COLOR, rect, 1)

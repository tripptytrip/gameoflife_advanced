import pygame
import math
from view.renderer import Renderer
from square_grid import SquareGrid
from hexagon_grid_numpy import HexagonGridNumpy
from triangle_grid_numpy import TriangleGridNumpy
from square_cell import SquareCell
from hexagon_cell import HexagonCell
from triangle_cell import TriangleCell

class PygameRenderer(Renderer):
    def render(self, grid, surface):
        if isinstance(grid, SquareGrid) and not isinstance(grid, (HexagonGridNumpy, TriangleGridNumpy)):
            self._draw_square_grid(grid, surface)
        elif isinstance(grid, HexagonGridNumpy):
            self._draw_hexagon_grid(grid, surface)
        elif isinstance(grid, TriangleGridNumpy):
            self._draw_triangle_grid(grid, surface)

    def _draw_square_grid(self, grid, surface):
        for y in range(grid.grid_height):
            for x in range(grid.grid_width):
                lifeform_id = grid.grid[y, x]
                lifeform = grid.get_lifeform_by_id(lifeform_id)
                alive_duration = grid.grid_lifespans[y, x]
                SquareCell.draw(surface, x, y, grid.cell_size, grid.offset_x, grid.offset_y, lifeform, alive_duration)

    def _draw_hexagon_grid(self, grid, surface):
        for r in range(grid.grid_height):
            for c in range(grid.grid_width):
                lifeform_id = grid.grid[r, c]
                lifeform = grid.get_lifeform_by_id(lifeform_id)
                alive_duration = grid.grid_lifespans[r, c]
                HexagonCell.draw_static(
                    surface, c, r, grid.cell_size, grid.offset_x, grid.offset_y, lifeform, alive_duration
                )

    def _draw_triangle_grid(self, grid, surface):
        for r in range(grid.grid_height):
            for c in range(grid.grid_width):
                lifeform_id = grid.grid[r, c]
                lifeform = grid.get_lifeform_by_id(lifeform_id)
                alive_duration = grid.grid_lifespans[r, c]
                upward = (c + r) % 2 == 0
                TriangleCell.draw_static(surface, c, r, grid.cell_size, upward, grid.offset_x, grid.offset_y, lifeform, alive_duration)

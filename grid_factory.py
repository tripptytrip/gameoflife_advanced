# grid_factory.py

from triangle_grid import TriangleGrid
from square_grid import SquareGrid
from hexagon_grid import HexagonGrid

def create_grid(lifeforms=None, initial_alive_percentage=0.5, shape='triangle',
                grid_width=50, grid_height=50, available_width=None, available_height=None):
    if shape == 'triangle':
        return TriangleGrid(
            lifeforms=lifeforms,
            initial_alive_percentage=initial_alive_percentage,
            grid_width=grid_width,
            grid_height=grid_height,
            available_width=available_width,
            available_height=available_height
        )
    elif shape == 'square':
        return SquareGrid(
            lifeforms=lifeforms,
            initial_alive_percentage=initial_alive_percentage,
            grid_width=grid_width,
            grid_height=grid_height,
            available_width=available_width,
            available_height=available_height
        )
    elif shape == 'hexagon':
        return HexagonGrid(
            lifeforms=lifeforms,
            initial_alive_percentage=initial_alive_percentage,
            grid_width=grid_width,
            grid_height=grid_height,
            available_width=available_width,
            available_height=available_height
        )
    else:
        raise ValueError(f"Unsupported grid shape: {shape}")

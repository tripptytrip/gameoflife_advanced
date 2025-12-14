# grid_factory.py

from triangle_grid_numpy import TriangleGridNumpy
from square_grid import SquareGrid
from hexagon_grid_numpy import HexagonGridNumpy

def create_grid(lifeforms=None, initial_alive_percentage=0.5, shape='triangle',
                grid_width=50, grid_height=50, available_width=None, available_height=None, wrap=True,
                triangle_neighborhood_mode="edge+vertex"):
    if shape == 'triangle':
        return TriangleGridNumpy(
            lifeforms=lifeforms,
            initial_alive_percentage=initial_alive_percentage,
            grid_width=grid_width,
            grid_height=grid_height,
            available_width=available_width,
            available_height=available_height,
            wrap=wrap,
            neighborhood_mode=triangle_neighborhood_mode
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
        return HexagonGridNumpy(
            lifeforms=lifeforms,
            initial_alive_percentage=initial_alive_percentage,
            grid_width=grid_width,
            grid_height=grid_height,
            available_width=available_width,
            available_height=available_height,
            wrap=wrap
        )
    else:
        raise ValueError(f"Unsupported grid shape: {shape}")

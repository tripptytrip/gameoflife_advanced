# neighbor_utils.py
#
# Centralised neighbour-count helpers per lattice.

def get_max_neighbors(grid_shape: str, triangle_mode: str = "edge+vertex") -> int:
    shape = grid_shape.lower()
    if shape == "square":
        return 8
    if shape == "hexagon":
        return 6
    if shape == "triangle":
        return 12 if triangle_mode == "edge+vertex" else 3
    raise ValueError(f"Unsupported grid shape: {grid_shape}")

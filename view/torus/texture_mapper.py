import numpy as np
from typing import List
from lifeform import Lifeform

class GridTextureMapper:
    """
    Converts grid state to an RGB texture for the torus surface.
    """
    
    def __init__(self, grid_width: int, grid_height: int, lifeforms: List[Lifeform]):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.lifeforms = lifeforms
        
        # Color lookup table
        self.color_lut = self._build_color_lut()
        
        # Pre-allocate texture buffer
        self.texture_data = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)
    
    def _build_color_lut(self) -> np.ndarray:
        """Build lookup table: lifeform_id → RGB color."""
        if not self.lifeforms:
            max_id = 1
        else:
            max_id = max(lf.id for lf in self.lifeforms) + 1
        lut = np.zeros((max_id, 3), dtype=np.uint8)
        lut[0] = [30, 30, 35]  # Dead cell color
        
        for lf in self.lifeforms:
            lut[lf.id] = lf.color_alive
        
        return lut
    
    def update(self, grid: np.ndarray, lifespans: np.ndarray) -> np.ndarray:
        """
        Convert grid state to RGB texture.
        
        Uses vectorized operations for performance.
        """
        # Base colors from lifeform IDs
        self.texture_data[:] = self.color_lut[grid]
        
        # Modify brightness based on lifespan (older = brighter/whiter)
        if lifespans is not None:
            static_mask = lifespans > 10
            # Ensure texture_data and the other array are compatible for the operation.
            # The operation is done in float64 and then cast back to uint8.
            self.texture_data[static_mask] = (
                self.texture_data[static_mask].astype(np.float64) * 0.7 + 
                np.array([255, 255, 255], dtype=np.uint8).astype(np.float64) * 0.3
            ).astype(np.uint8)
        
        return self.texture_data

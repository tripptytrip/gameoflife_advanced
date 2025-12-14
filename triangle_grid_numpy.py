# triangle_grid_numpy.py

import pygame
import numpy as np
from scipy.signal import convolve2d
from square_grid import SquareGrid
from triangle_cell import TriangleCell
import random
import math

class TriangleGridNumpy(SquareGrid):
    """
    Manages the triangular grid and cell states for multiple lifeforms using NumPy for performance.
    """

    def __init__(self, lifeforms=None, initial_alive_percentage=0.5,
                 grid_width=50, grid_height=50, available_width=None, available_height=None):
        """
        Initialize the triangle grid based on the specified grid size and lifeforms.
        """
        super().__init__(lifeforms, initial_alive_percentage, grid_width, grid_height, available_width, available_height)
        self._create_neighbor_map()

    def _create_neighbor_map(self):
        self.neighbor_map = {}
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                neighbors = []
                # Upward pointing triangle
                if (c + r) % 2 == 0:
                    offsets = [(0, -1), (0, 1), (-1, 0)]
                # Downward pointing triangle
                else:
                    offsets = [(0, -1), (0, 1), (1, 0)]
                
                for dr, dc in offsets:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.grid_height and 0 <= nc < self.grid_width:
                        neighbors.append(nr * self.grid_width + nc)
                self.neighbor_map[r * self.grid_width + c] = neighbors

    def create_grid(self):
        """
        Create the triangular grid of cells and distribute initial live cells among lifeforms.
        """
        # Calculate cell size based on available space and grid dimensions
        if self.available_width and self.available_height:
            cell_width = self.available_width / ((self.grid_width + 1) / 2)
            cell_height = self.available_height / (self.grid_height * (math.sqrt(3) / 2))
            self.cell_size = int(min(cell_width, cell_height))
        else:
            self.cell_size = 10  # Default cell size

        # Initialize grid state
        self.grid = np.zeros((self.grid_height, self.grid_width), dtype=np.int8)
        self.grid_lifespans = np.zeros_like(self.grid)
        
        num_alive_cells = int(self.grid_width * self.grid_height * self.initial_alive_percentage)
        if num_alive_cells > 0 and self.lifeforms:
            # Generate random indices for alive cells
            alive_indices = np.random.choice(self.grid_width * self.grid_height, num_alive_cells, replace=False)
            alive_rows, alive_cols = np.unravel_index(alive_indices, self.grid.shape)

            # Assign lifeforms to alive cells
            lifeform_ids = np.random.choice([lf.id for lf in self.lifeforms], size=num_alive_cells)
            self.grid[alive_rows, alive_cols] = lifeform_ids
            self.grid_lifespans[alive_rows, alive_cols] = 1
        elif num_alive_cells > 0: # single lifeform case
            alive_indices = np.random.choice(self.grid_width * self.grid_height, num_alive_cells, replace=False)
            alive_rows, alive_cols = np.unravel_index(alive_indices, self.grid.shape)
            self.grid[alive_rows, alive_cols] = 1
            self.grid_lifespans[alive_rows, alive_cols] = 1

    def update(self):
        is_alive = self.grid > 0
        flat_grid = self.grid.ravel()
        
        neighbor_counts = {}
        for lifeform in self.lifeforms:
            lifeform_mask = flat_grid == lifeform.id
            neighbor_counts[lifeform.id] = np.zeros_like(flat_grid, dtype=np.int8)
            for i in range(len(flat_grid)):
                neighbors = self.neighbor_map[i]
                neighbor_counts[lifeform.id][i] = np.sum(lifeform_mask[neighbors])

        neighbor_counts_grid = {lf: counts.reshape(self.grid.shape) for lf, counts in neighbor_counts.items()}
        
        new_grid = self.grid.copy()
        new_lifespans = self.grid_lifespans.copy()

        births = 0
        deaths = 0

        lifeform_birth_counts = {lf.id: 0 for lf in self.lifeforms}

        # --- Birth Logic ---
        dead_cells = ~is_alive
        possible_births = np.zeros_like(self.grid)

        for lifeform in self.lifeforms:
            neighbor_count = neighbor_counts_grid[lifeform.id]
            birth_mask = np.isin(neighbor_count, lifeform.birth_rules) & dead_cells
            possible_births[birth_mask] = lifeform.id

        birth_locations = np.argwhere(possible_births > 0)
        
        if birth_locations.size > 0:
            for y, x in birth_locations:
                potential_parents = []
                for lifeform in self.lifeforms:
                    if np.isin(neighbor_counts_grid[lifeform.id][y, x], lifeform.birth_rules):
                        potential_parents.append(lifeform.id)

                if potential_parents:
                    chosen_parent = random.choice(potential_parents)
                    new_grid[y, x] = chosen_parent
                    new_lifespans[y, x] = 1
                    births += 1
                    lifeform_birth_counts[chosen_parent] += 1

        # --- Survival and Death Logic ---
        for lifeform in self.lifeforms:
            lifeform_mask = (self.grid == lifeform.id)
            neighbor_count = neighbor_counts_grid[lifeform.id]
            
            # Survival
            survival_mask = np.isin(neighbor_count, lifeform.survival_rules) & lifeform_mask
            new_lifespans[survival_mask] += 1

            # Death
            death_mask = ~np.isin(neighbor_count, lifeform.survival_rules) & lifeform_mask
            new_grid[death_mask] = 0
            new_lifespans[death_mask] = 0
            deaths += np.sum(death_mask)

        self.grid = new_grid
        self.grid_lifespans = new_lifespans
        
        # --- Metrics ---
        static_cells = np.sum(self.grid_lifespans > 10)
        lifeform_alive_counts = {lf.id: np.sum(self.grid == lf.id) for lf in self.lifeforms}
        lifeform_static_counts = {lf.id: np.sum((self.grid == lf.id) & (self.grid_lifespans > 10)) for lf in self.lifeforms}
        lifeform_metrics = {lf.id: {} for lf in self.lifeforms}
        
        self.generation += 1

        return births, deaths, static_cells, lifeform_alive_counts, lifeform_static_counts, lifeform_metrics

    def draw(self, surface):
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                lifeform_id = self.grid[r, c]
                lifeform = self.get_lifeform_by_id(lifeform_id)
                alive_duration = self.grid_lifespans[r, c]
                upward = (c + r) % 2 == 0
                TriangleCell.draw_static(surface, c, r, self.cell_size, upward, self.offset_x, self.offset_y, lifeform, alive_duration)

    def handle_click(self, pos):
        mouse_x, mouse_y = pos
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                x = c * (self.cell_size / 2) + self.offset_x
                y = r * (self.cell_size * math.sqrt(3) / 2) + self.offset_y
                
                if math.dist((mouse_x, mouse_y), (x, y)) < self.cell_size / 2:
                    if self.grid[r, c] > 0:
                        self.grid[r, c] = 0
                        self.grid_lifespans[r, c] = 0
                    else:
                        if self.lifeforms:
                            lifeform_id = random.choice(self.lifeforms).id
                            self.grid[r, c] = lifeform_id
                            self.grid_lifespans[r, c] = 1
                        else: # single lifeform
                            self.grid[r, c] = 1
                            self.grid_lifespans[r, c] = 1
                    return


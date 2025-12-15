# hexagon_grid_numpy.py

import pygame
import numpy as np
from scipy.signal import convolve2d
from square_grid import SquareGrid
from hexagon_cell import HexagonCell
import random
import math

class HexagonGridNumpy(SquareGrid):
    """
    Manages the hexagonal grid and cell states for multiple lifeforms using NumPy for performance.
    """

    def __init__(self, lifeforms=None, initial_alive_percentage=0.5,
                 grid_width=50, grid_height=50, available_width=None, available_height=None, wrap=True):
        """
        Initialize the hexagonal grid based on the specified grid size and lifeforms.
        """
        self.wrap = wrap
        super().__init__(lifeforms, initial_alive_percentage, grid_width, grid_height, available_width, available_height)
        self._create_neighbor_map()

    def _create_neighbor_map(self):
        self.neighbor_map = {}
        neighbor_lists = []
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                neighbors = []
                # Odd-q layout
                if c % 2 == 1:
                    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (1, 1)]
                else:
                    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)]
                self.neighbor_count = len(offsets)
                
                for dr, dc in offsets:
                    nr, nc = r + dr, c + dc
                    if self.wrap:
                        nr %= self.grid_height
                        nc %= self.grid_width
                        neighbors.append(nr * self.grid_width + nc)
                    else:
                        if 0 <= nr < self.grid_height and 0 <= nc < self.grid_width:
                            neighbors.append(nr * self.grid_width + nc)
                cell_index = r * self.grid_width + c
                self.neighbor_map[cell_index] = neighbors
                neighbor_lists.append(neighbors)

        # Dense neighbor array for vectorized counting
        self.max_degree = max((len(n) for n in neighbor_lists), default=0)
        num_cells = self.grid_width * self.grid_height
        self.neighbor_indices = -np.ones((num_cells, self.max_degree), dtype=np.int32)
        for idx, lst in enumerate(neighbor_lists):
            self.neighbor_indices[idx, : len(lst)] = lst

    def create_grid(self):
        """
        Create the hexagonal grid of cells and distribute initial live cells among lifeforms.
        """
        self.resize(self.available_width, self.available_height)

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

    def draw(self, surface):
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                lifeform_id = self.grid[r, c]
                lifeform = self.get_lifeform_by_id(lifeform_id)
                alive_duration = self.grid_lifespans[r, c]

                # Pass axial coordinates into the renderer so it can calculate the center itself
                HexagonCell.draw_static(
                    surface,
                    c,
                    r,
                    self.cell_size,
                    self.offset_x,
                    self.offset_y,
                    lifeform,
                    alive_duration,
                )

    def update(self):
        is_alive = self.grid > 0
        flat_grid = self.grid.ravel()

        # Vectorized neighbor counts
        padded = np.pad(flat_grid, (0, 1))  # last index used for padding (-1 entries)
        neighbor_idx = np.where(self.neighbor_indices >= 0, self.neighbor_indices, flat_grid.size)
        neighbor_vals = padded[neighbor_idx]
        
        neighbor_counts = {}
        for lifeform in self.lifeforms:
            life_mask = (neighbor_vals == lifeform.id).astype(np.int8)
            counts = life_mask.sum(axis=1)
            neighbor_counts[lifeform.id] = counts

        neighbor_counts_grid = {lf: counts.reshape(self.grid.shape) for lf, counts in neighbor_counts.items()}
        
        new_grid = self.grid.copy()
        new_lifespans = self.grid_lifespans.copy()

        births = 0
        deaths = 0

        lifeform_birth_counts = {lf.id: 0 for lf in self.lifeforms}
        lifeform_kill_counts = {lf.id: 0 for lf in self.lifeforms}

        if self.lifeforms:
            stacked_counts = np.stack([neighbor_counts[lf.id] for lf in self.lifeforms])
            total_neighbors_all = stacked_counts.sum(axis=0).reshape(self.grid.shape)

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

            # Kill attribution for overcrowding
            if lifeform.survival_rules:
                max_survive = max(lifeform.survival_rules)
            else:
                max_survive = -1
            death_overcrowd = (neighbor_count > max_survive) & death_mask
            if self.lifeforms and np.any(death_overcrowd):
                lf_idx = self.lifeforms.index(lifeform)
                counts_at = stacked_counts[:, death_overcrowd.ravel()]
                counts_at[lf_idx, :] = -1
                killer_idx = np.argmax(counts_at, axis=0)
                killer_vals = np.take_along_axis(counts_at, killer_idx[None, :], axis=0).flatten()
                total_n = total_neighbors_all[death_overcrowd]
                majority = killer_vals > (total_n / 2)
                for k_idx, is_majority in zip(killer_idx, majority):
                    if not is_majority:
                        continue
                    killer_lf = self.lifeforms[k_idx]
                    if killer_lf.id != lifeform.id:
                        lifeform_kill_counts[killer_lf.id] += 1

        changed_cells = np.sum(self.grid != new_grid)
        self.grid = new_grid
        self.grid_lifespans = new_lifespans
        
        # --- Metrics ---
        static_cells = np.sum(self.grid_lifespans > 10)
        lifeform_alive_counts = {lf.id: np.sum(self.grid == lf.id) for lf in self.lifeforms}
        lifeform_static_counts = {lf.id: np.sum((self.grid == lf.id) & (self.grid_lifespans > 10)) for lf in self.lifeforms}
        lifeform_metrics = {lf.id: {} for lf in self.lifeforms}
        
        self.generation += 1

        return births, deaths, static_cells, lifeform_alive_counts, lifeform_static_counts, lifeform_metrics, lifeform_kill_counts, changed_cells

    def handle_click(self, pos):
        mouse_x, mouse_y = pos
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                x = self.cell_size * 3/2 * c + self.offset_x
                y = self.cell_size * math.sqrt(3) * (r + 0.5 * (c&1)) + self.offset_y
                
                # Using a simple distance check for now
                if math.dist((mouse_x, mouse_y), (x, y)) < self.cell_size:
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

    def resize(self, available_width=None, available_height=None):
        """
        Recompute cell size on window resize without resetting state.
        """
        self.available_width = available_width
        self.available_height = available_height
        if self.available_width and self.available_height:
            cell_width_approx = self.available_width / (self.grid_width * 1.5)
            cell_height_approx = self.available_height / (self.grid_height * math.sqrt(3))
            self.cell_size = int(min(cell_width_approx, cell_height_approx))
        else:
            self.cell_size = 10  # Default cell size

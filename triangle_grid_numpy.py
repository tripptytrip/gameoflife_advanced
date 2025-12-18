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
                 grid_width=50, grid_height=50, available_width=None, available_height=None, wrap=True, neighborhood_mode="edge+vertex"):
        """
        Initialize the triangle grid based on the specified grid size and lifeforms.
        """
        self.wrap = wrap
        self.neighborhood_mode = neighborhood_mode.lower()  # "edge" or "edge+vertex"
        if self.neighborhood_mode not in ("edge", "edge+vertex"):
            raise ValueError(f"Unsupported triangle neighborhood mode: {neighborhood_mode}")
        super().__init__(lifeforms, initial_alive_percentage, grid_width, grid_height, available_width, available_height)
        self._build_neighbor_offsets()
        self._create_neighbor_map()

    def _triangle_corners(self, r, c, upward, size=2.0):
        """
        Compute triangle corners for a notional triangle at (r, c).
        Used only for adjacency discovery.
        """
        x0 = c * (size / 2)
        y0 = r * (size * math.sqrt(3) / 2)
        half_size = size / 2
        height = size * math.sqrt(3) / 2
        if upward:
            corners = [
                (x0, y0 - height / 2),
                (x0 - half_size, y0 + height / 2),
                (x0 + half_size, y0 + height / 2),
            ]
        else:
            corners = [
                (x0, y0 + height / 2),
                (x0 - half_size, y0 - height / 2),
                (x0 + half_size, y0 - height / 2),
            ]
        return [(round(cx, 6), round(cy, 6)) for cx, cy in corners]

    def _build_neighbor_offsets(self):
        """
        Precompute relative neighbor offsets for upward/downward triangles based on the mode.
        """
        def add_offsets(origin_corners, base_r, base_c):
            offsets = set()
            for dr in range(-3, 4):
                for dc in range(-3, 4):
                    if dr == 0 and dc == 0:
                        continue
                    nr = base_r + dr
                    nc = base_c + dc
                    neighbor_upward = (nr + nc) % 2 == 0
                    corners = self._triangle_corners(nr, nc, neighbor_upward)
                    shared_vertices = set(origin_corners) & set(corners)
                    if self.neighborhood_mode == "edge":
                        if len(shared_vertices) >= 2:
                            offsets.add((dr, dc))
                    else:  # edge+vertex
                        if len(shared_vertices) >= 1:
                            offsets.add((dr, dc))
            return offsets

        # Use coordinate origins that match orientation parity
        base_up_r, base_up_c = 0, 0  # even parity
        base_down_r, base_down_c = 0, 1  # odd parity
        origin_up = self._triangle_corners(base_up_r, base_up_c, True)
        origin_down = self._triangle_corners(base_down_r, base_down_c, False)

        self.offsets_up = add_offsets(origin_up, base_up_r, base_up_c)
        self.offsets_down = add_offsets(origin_down, base_down_r, base_down_c)
        if len(self.offsets_up) != len(self.offsets_down):
            raise ValueError("Triangle neighbor offsets differ between orientations")
        # Consistency metadata
        self.neighbor_count = len(self.offsets_up)

    def _create_neighbor_map(self):
        self.neighbor_map = {}
        neighbor_lists = []
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                neighbors = []
                upward = (c + r) % 2 == 0
                offsets = self.offsets_up if upward else self.offsets_down

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
        Create the triangular grid of cells and distribute initial live cells among lifeforms.
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

    def draw(self, surface):
        pass

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

    def resize(self, available_width=None, available_height=None):
        """
        Recompute cell size on window resize without resetting state.
        """
        self.available_width = available_width
        self.available_height = available_height
        if self.available_width and self.available_height:
            cell_width = self.available_width / ((self.grid_width + 1) / 2)
            cell_height = self.available_height / (self.grid_height * (math.sqrt(3) / 2))
            self.cell_size = int(min(cell_width, cell_height))
        else:
            self.cell_size = 10  # Default cell size

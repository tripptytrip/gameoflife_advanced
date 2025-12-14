# square_grid.py

import pygame
import numpy as np
from scipy.signal import convolve2d
from square_cell import SquareCell
from lifeform import Lifeform
import random

class SquareGrid:
    """
    Manages the square grid and cell states for multiple lifeforms using NumPy for performance.
    """

    def __init__(self, lifeforms=None, initial_alive_percentage=0.5,
                 grid_width=50, grid_height=50, available_width=None, available_height=None):
        """
        Initialize the square grid based on the specified grid size and lifeforms.
        """
        self.lifeforms = lifeforms if lifeforms else []
        self.initial_alive_percentage = initial_alive_percentage
        self.generation = 0
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.available_width = available_width
        self.available_height = available_height
        self.neighbor_count = 8  # Moore neighborhood

        self.grid = np.zeros((self.grid_height, self.grid_width), dtype=np.int8)
        self.grid_lifespans = np.zeros_like(self.grid)

        self.offset_x = 0
        self.offset_y = 0
        self.cell_size = None  # Will be calculated
        
        self.create_grid()

    def resize(self, available_width=None, available_height=None):
        """
        Recompute cell size when the window is resized without resetting state.
        """
        self.available_width = available_width
        self.available_height = available_height
        if self.available_width and self.available_height:
            cell_width = self.available_width / self.grid_width
            cell_height = self.available_height / self.grid_height
            self.cell_size = int(min(cell_width, cell_height))
        else:
            self.cell_size = 10

    def calculate_offsets(self, start_x=0, start_y=0):
        self.offset_x = start_x
        self.offset_y = start_y

    def create_grid(self):
        # Calculate cell size
        if self.available_width and self.available_height:
            cell_width = self.available_width / self.grid_width
            cell_height = self.available_height / self.grid_height
            self.cell_size = int(min(cell_width, cell_height))
        else:
            self.cell_size = 10

        # Initialize grid state
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
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                lifeform_id = self.grid[y, x]
                lifeform = self.get_lifeform_by_id(lifeform_id)
                alive_duration = self.grid_lifespans[y, x]
                SquareCell.draw(surface, x, y, self.cell_size, self.offset_x, self.offset_y, lifeform, alive_duration)


    def get_lifeform_by_id(self, lifeform_id):
        if lifeform_id is None or lifeform_id == 0:
            return None
        for lifeform in self.lifeforms:
            if lifeform.id == lifeform_id:
                return lifeform
        return None

    def update(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        
        is_alive = self.grid > 0
        
        new_grid = self.grid.copy()
        new_lifespans = self.grid_lifespans.copy()

        births = 0
        deaths = 0

        lifeform_birth_counts = {lf.id: 0 for lf in self.lifeforms}

        # Pre-calculate neighbor counts for all lifeforms
        neighbor_counts = {}
        for lifeform in self.lifeforms:
            lifeform_grid = (self.grid == lifeform.id)
            neighbor_counts[lifeform.id] = convolve2d(lifeform_grid, kernel, mode='same', boundary='wrap')

        # --- Birth Logic ---
        dead_cells = ~is_alive
        possible_births = np.zeros_like(self.grid)

        for lifeform in self.lifeforms:
            neighbor_count = neighbor_counts[lifeform.id]
            birth_mask = np.isin(neighbor_count, lifeform.birth_rules) & dead_cells
            possible_births[birth_mask] = lifeform.id

        birth_locations = np.argwhere(possible_births > 0)
        
        if birth_locations.size > 0:
            for y, x in birth_locations:
                potential_parents = []
                for lifeform in self.lifeforms:
                    if np.isin(neighbor_counts[lifeform.id][y, x], lifeform.birth_rules):
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
            neighbor_count = neighbor_counts[lifeform.id]
            
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

        # The rest of the metrics are complex and might require more thought on how to vectorize them efficiently.
        # For now, we'll return placeholder values.
        lifeform_metrics = {lf.id: {} for lf in self.lifeforms}
        
        self.generation += 1

        return births, deaths, static_cells, lifeform_alive_counts, lifeform_static_counts, lifeform_metrics


    def handle_click(self, pos):
        x, y = pos
        grid_x = int((x - self.offset_x) / self.cell_size)
        grid_y = int((y - self.offset_y) / self.cell_size)

        if 0 <= grid_y < self.grid_height and 0 <= grid_x < self.grid_width:
            if self.grid[grid_y, grid_x] > 0:
                self.grid[grid_y, grid_x] = 0
                self.grid_lifespans[grid_y, grid_x] = 0
            else:
                if self.lifeforms:
                    lifeform_id = random.choice(self.lifeforms).id
                    self.grid[grid_y, grid_x] = lifeform_id
                    self.grid_lifespans[grid_y, grid_x] = 1
                else: # single lifeform
                    self.grid[grid_y, grid_x] = 1
                    self.grid_lifespans[grid_y, grid_x] = 1

    # Metrics calculation methods need to be refactored to work with NumPy arrays
    def calculate_average_cluster_size(self, lifeform_id):
        # Placeholder
        return 0

    def calculate_max_cluster_size(self, lifeform_id):
        # Placeholder
        return 0

    def identify_clusters(self, lifeform_id):
        # Placeholder
        return []

    def calculate_entropy(self, lifeform_id):
        # Placeholder
        return 0

    def calculate_pattern_diversity(self, lifeform_id):
        # Placeholder
        return 0


# triangle_grid.py

import pygame
from triangle_cell import TriangleCell
from lifeform import Lifeform
import random
import math

class TriangleGrid:
    """
    Manages the triangular grid and cell states for multiple lifeforms.
    """
    def __init__(self, lifeforms=None, initial_alive_percentage=0.5,
                 grid_width=50, grid_height=50, available_width=None, available_height=None):
        """
        Initialize the triangle grid based on the specified grid size and lifeforms.

        Args:
            lifeforms (list of Lifeform): List of lifeforms operating on the grid.
            initial_alive_percentage (float): The percentage of cells to be alive initially (between 0 and 1).
            grid_width (int): Number of cells in the horizontal direction.
            grid_height (int): Number of cells in the vertical direction.
            available_width (int or float): Available screen width for the grid.
            available_height (int or float): Available screen height for the grid.
        """
        self.cells = {}
        self.offset_x = 0
        self.offset_y = 0
        self.cell_size = None  # Will be calculated
        self.lifeforms = lifeforms if lifeforms else []
        self.initial_alive_percentage = initial_alive_percentage
        self.generation = 0
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.available_width = available_width
        self.available_height = available_height
        self.create_grid()

    def calculate_offsets(self, start_x=0, start_y=0):
        """
        Calculate offsets to position the grid so that its top-left corner is at (start_x, start_y).

        Args:
            start_x (float): The x-coordinate where the grid's top-left corner should be positioned.
            start_y (float): The y-coordinate where the grid's top-left corner should be positioned.
        """
        self.offset_x = start_x
        self.offset_y = start_y

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

        # Create cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                upward = (x + y) % 2 == 0
                cell = TriangleCell(x, y, self.cell_size, upward=upward, alive=False, lifeform_id=None)
                self.cells[(x, y)] = cell

        total_cells = len(self.cells)
        alive_cells_total = int(total_cells * self.initial_alive_percentage)
        num_lifeforms = len(self.lifeforms) if self.lifeforms else 1
        alive_cells_per_lifeform = max(alive_cells_total // num_lifeforms, 1)

        # Assign alive cells to lifeforms
        if self.lifeforms:
            for lifeform in self.lifeforms:
                assigned = 0
                while assigned < alive_cells_per_lifeform:
                    cell = random.choice(list(self.cells.values()))
                    if not cell.alive:
                        cell.alive = True
                        cell.lifeform_id = lifeform.id
                        cell.alive_duration = 1
                        assigned += 1
        else:
            # Single lifeform scenario
            for cell in self.cells.values():
                if random.random() < self.initial_alive_percentage:
                    cell.alive = True
                    cell.lifeform_id = 1  # Default lifeform ID
                    cell.alive_duration = 1

        self.calculate_neighbors()

    def calculate_neighbors(self):
        """
        Calculate and assign neighbors for each cell.
        """
        # Define neighbor offsets for triangles
        neighbor_offsets = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, 1), (-1, 1), (1, -1)
        ]
        for cell in self.cells.values():
            neighbors = []
            for dx, dy in neighbor_offsets:
                neighbor_coord = (cell.x + dx, cell.y + dy)
                neighbor = self.cells.get(neighbor_coord)
                if neighbor:
                    neighbors.append(neighbor)
            cell.neighbors = neighbors

    def draw(self, surface):
        """
        Draw all cells in the grid with appropriate colors based on lifeforms.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        for cell in self.cells.values():
            lifeform = self.get_lifeform_by_id(cell.lifeform_id)
            cell.draw(surface, self.offset_x, self.offset_y, lifeform=lifeform)

    def get_lifeform_by_id(self, lifeform_id):
        """
        Retrieve a Lifeform object by its ID.

        Args:
            lifeform_id (int or None): The ID of the lifeform.

        Returns:
            Lifeform or None: The corresponding Lifeform object or None if not found.
        """
        if lifeform_id is None:
            return None
        for lifeform in self.lifeforms:
            if lifeform.id == lifeform_id:
                return lifeform
        return None

    def update(self):
        """
        Update the grid to the next generation based on each lifeform's rules.

        Returns:
            tuple: A tuple containing the number of births, deaths, static cells,
                   lifeform_alive_counts, lifeform_static_counts, lifeform_metrics.
        """
        new_states = {}
        births = 0
        deaths = 0
        static_cells = 0

        lifeform_static_counts = {lifeform.id: 0 for lifeform in self.lifeforms}
        lifeform_alive_counts = {lifeform.id: 0 for lifeform in self.lifeforms}
        lifeform_death_counts = {lifeform.id: 0 for lifeform in self.lifeforms}
        lifeform_birth_counts = {lifeform.id: 0 for lifeform in self.lifeforms}
        lifeform_lifespans = {lifeform.id: [] for lifeform in self.lifeforms}
        previous_alive_counts = self.previous_alive_counts if hasattr(self, 'previous_alive_counts') else {lifeform.id: 0 for lifeform in self.lifeforms}
        lifeform_previous_positions = self.lifeform_previous_positions if hasattr(self, 'lifeform_previous_positions') else {lifeform.id: set() for lifeform in self.lifeforms}
        lifeform_current_positions = {lifeform.id: set() for lifeform in self.lifeforms}

        # Record previous positions
        for cell in self.cells.values():
            if cell.alive:
                lifeform_previous_positions[cell.lifeform_id].add((cell.x, cell.y))

        for cell in self.cells.values():
            if cell.lifeform_id is None:
                # Dead cell: Check for possible births from any lifeform
                possible_births = {}
                for lifeform in self.lifeforms:
                    live_neighbors = sum(1 for neighbor in cell.neighbors if neighbor.alive and neighbor.lifeform_id == lifeform.id)
                    if live_neighbors in lifeform.birth_rules:
                        possible_births[lifeform.id] = live_neighbors
                if possible_births:
                    # Randomly select one lifeform to birth the cell
                    selected_lifeform_id = random.choice(list(possible_births.keys()))
                    new_states[cell] = selected_lifeform_id  # Cell becomes alive with selected lifeform
                    births += 1
                    lifeform_birth_counts[selected_lifeform_id] += 1
                else:
                    new_states[cell] = None  # Remains dead
            else:
                # Live cell: Apply survival rules of its own lifeform
                lifeform = self.get_lifeform_by_id(cell.lifeform_id)
                if lifeform:
                    live_neighbors = sum(1 for neighbor in cell.neighbors if neighbor.alive and neighbor.lifeform_id == lifeform.id)
                    if live_neighbors in lifeform.survival_rules:
                        new_states[cell] = lifeform.id  # Survives
                    else:
                        new_states[cell] = None  # Dies
                        deaths += 1
                        lifeform_death_counts[cell.lifeform_id] += 1
                        # Record lifespan
                        lifeform_lifespans[cell.lifeform_id].append(cell.alive_duration)
                else:
                    new_states[cell] = None  # Shouldn't happen

        # Update cell states and alive_duration
        for cell, new_lifeform_id in new_states.items():
            if new_lifeform_id is not None:
                if cell.alive:
                    if cell.lifeform_id == new_lifeform_id:
                        cell.alive_duration += 1
                    else:
                        # Record lifespan before changing lifeform
                        lifeform_lifespans[cell.lifeform_id].append(cell.alive_duration)
                        cell.lifeform_id = new_lifeform_id
                        cell.alive_duration = 1
                else:
                    cell.alive = True
                    cell.lifeform_id = new_lifeform_id
                    cell.alive_duration = 1
            else:
                if cell.alive:
                    # Record lifespan
                    lifeform_lifespans[cell.lifeform_id].append(cell.alive_duration)
                    cell.alive = False
                    cell.lifeform_id = None
                    cell.alive_duration = 0

            # Count static cells and alive cells per lifeform
            if cell.alive:
                lifeform_alive_counts[cell.lifeform_id] += 1
                lifeform_current_positions[cell.lifeform_id].add((cell.x, cell.y))
                if cell.alive_duration > 10:
                    static_cells += 1
                    lifeform_static_counts[cell.lifeform_id] += 1

        # Compute metrics for each lifeform
        lifeform_metrics = {}
        total_cells = len(self.cells)
        total_alive_cells = sum(lifeform_alive_counts.values())
        for lifeform in self.lifeforms:
            lifeform_id = lifeform.id
            metrics = {}

            # Average Cluster Size for Static Lifeforms
            metrics['average_cluster_size'] = self.calculate_average_cluster_size(lifeform_id)

            # Growth Rate
            previous_alive = previous_alive_counts.get(lifeform_id, 0)
            current_alive = lifeform_alive_counts.get(lifeform_id, 0)
            metrics['growth_rate'] = (current_alive - previous_alive) if self.generation > 0 else 0

            # Death Rate
            metrics['death_rate'] = lifeform_death_counts.get(lifeform_id, 0)

            # Average Lifespan of Cells
            lifespans = lifeform_lifespans.get(lifeform_id, [])
            if lifespans:
                metrics['average_lifespan'] = sum(lifespans) / len(lifespans)
            else:
                metrics['average_lifespan'] = 0

            # Maximum Cluster Size
            metrics['max_cluster_size'] = self.calculate_max_cluster_size(lifeform_id)

            # Dominance Ratio
            if total_alive_cells > 0:
                metrics['dominance_ratio'] = current_alive / total_alive_cells
            else:
                metrics['dominance_ratio'] = 0

            # Entropy (Spatial Distribution)
            metrics['entropy'] = self.calculate_entropy(lifeform_id)

            # Mobility
            previous_positions = lifeform_previous_positions.get(lifeform_id, set())
            current_positions = lifeform_current_positions.get(lifeform_id, set())
            if previous_positions:
                moved_cells = len(current_positions - previous_positions)
                total_previous_cells = len(previous_positions)
                metrics['mobility'] = moved_cells / total_previous_cells
            else:
                metrics['mobility'] = 0

            # Diversity of Patterns
            metrics['diversity'] = self.calculate_pattern_diversity(lifeform_id)

            lifeform_metrics[lifeform_id] = metrics

        # Save current alive counts and positions for the next generation
        self.previous_alive_counts = lifeform_alive_counts.copy()
        self.lifeform_previous_positions = lifeform_current_positions

        return births, deaths, static_cells, lifeform_alive_counts, lifeform_static_counts, lifeform_metrics

    def calculate_average_cluster_size(self, lifeform_id):
        """
        Calculate the average cluster size for static lifeforms.

        Args:
            lifeform_id (int): The ID of the lifeform.

        Returns:
            float: The average cluster size.
        """
        clusters = self.identify_clusters(lifeform_id)
        if clusters:
            cluster_sizes = [len(cluster) for cluster in clusters]
            return sum(cluster_sizes) / len(cluster_sizes)
        else:
            return 0

    def calculate_max_cluster_size(self, lifeform_id):
        """
        Calculate the maximum cluster size for the lifeform.

        Args:
            lifeform_id (int): The ID of the lifeform.

        Returns:
            int: The size of the largest cluster.
        """
        clusters = self.identify_clusters(lifeform_id)
        if clusters:
            return max(len(cluster) for cluster in clusters)
        else:
            return 0

    def identify_clusters(self, lifeform_id):
        """
        Identify clusters of connected cells for the lifeform.

        Args:
            lifeform_id (int): The ID of the lifeform.

        Returns:
            list of set: A list where each element is a set of connected cells forming a cluster.
        """
        visited = set()
        clusters = []

        for cell in self.cells.values():
            if cell.alive and cell.lifeform_id == lifeform_id and cell not in visited:
                cluster = set()
                self.dfs_iterative(cell, lifeform_id, visited, cluster)
                clusters.append(cluster)
        return clusters

    def dfs_iterative(self, start_cell, lifeform_id, visited, cluster):
        """
        Iterative depth-first search to identify connected cells.

        Args:
            start_cell (TriangleCell): The starting cell for DFS.
            lifeform_id (int): The ID of the lifeform.
            visited (set): Set of already visited cells.
            cluster (set): Set to accumulate connected cells.
        """
        stack = [start_cell]
        while stack:
            cell = stack.pop()
            if cell not in visited:
                visited.add(cell)
                cluster.add(cell)
                for neighbor in cell.neighbors:
                    if neighbor.alive and neighbor.lifeform_id == lifeform_id and neighbor not in visited:
                        stack.append(neighbor)

    def calculate_entropy(self, lifeform_id):
        """
        Calculate the entropy of the spatial distribution of the lifeform's cells.

        Args:
            lifeform_id (int): The ID of the lifeform.

        Returns:
            float: The entropy value.
        """
        positions = [(cell.x, cell.y) for cell in self.cells.values() if cell.alive and cell.lifeform_id == lifeform_id]
        if not positions:
            return 0
        xs, ys = zip(*positions)
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        variance_x = sum((x - mean_x) ** 2 for x in xs) / len(xs)
        variance_y = sum((y - mean_y) ** 2 for y in ys) / len(ys)
        entropy = (variance_x + variance_y) ** 0.5
        return entropy

    def calculate_pattern_diversity(self, lifeform_id):
        """
        Calculate the diversity of patterns for the lifeform.

        Args:
            lifeform_id (int): The ID of the lifeform.

        Returns:
            int: The number of distinct patterns.
        """
        clusters = self.identify_clusters(lifeform_id)
        pattern_set = set()
        for cluster in clusters:
            pattern = frozenset((cell.x, cell.y) for cell in cluster)
            pattern_set.add(pattern)
        return len(pattern_set)

    def handle_click(self, pos):
        """
        Handle a mouse click event to toggle a cell's state.

        Args:
            pos (tuple): (x, y) pixel coordinates of the click.
        """
        x, y = pos
        for cell in self.cells.values():
            x_cell, y_cell = cell.get_position(self.offset_x, self.offset_y)
            rect = pygame.Rect(x_cell, y_cell, cell.size, cell.size)
            if rect.collidepoint(x, y):
                if cell.alive:
                    # Toggle to dead
                    cell.alive = False
                    cell.lifeform_id = None
                    cell.alive_duration = 0
                else:
                    # Toggle to alive with a random lifeform
                    if self.lifeforms:
                        cell.lifeform_id = random.choice(self.lifeforms).id
                    else:
                        cell.lifeform_id = 1  # Default lifeform ID
                    cell.alive = True
                    cell.alive_duration = 1
                break

    @staticmethod
    def point_in_polygon(x, y, polygon):
        """
        Determine if a point is inside a polygon using the ray casting algorithm.

        Args:
            x (float): X-coordinate of the point.
            y (float): Y-coordinate of the point.
            polygon (list): List of (x, y) tuples representing the polygon corners.

        Returns:
            bool: True if the point is inside the polygon, False otherwise.
        """
        num = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(num + 1):
            p2x, p2y = polygon[i % num]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y + 1e-6) + p1x  # Prevent division by zero
                        else:
                            xints = p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

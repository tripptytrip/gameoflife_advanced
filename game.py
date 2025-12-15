# game.py

import pygame
import uuid
import numpy as np
from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    PANEL_BACKGROUND_COLOR,
    FONT_NAME,
    FONT_SIZE,
    TEXT_COLOR,
    LEFT_PANEL_WIDTH,
    DEFAULT_TRIANGLE_MODE,
)
from settings_panel import SettingsPanel
from grid_factory import create_grid
from tooltip import Tooltip
from data_recorder import DataRecorder  # Ensure DataRecorder is imported
from lifeform import Lifeform  # Ensure Lifeform is imported
import random
from neighbor_utils import get_max_neighbors

class GameOfLife:
    """
    Manages the main game loop and user interactions.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Conway's Game of Life Simulator")
        self.clock = pygame.time.Clock()
        
        # Initialize settings
        self.fps = 30  # Ensure this is set before SettingsPanel
        self.number_of_lifeforms = 1  # Default to 1 lifeform
        self.lifeforms = []
        self.shape = 'square'  # Initialize grid shape
        self.triangle_mode = DEFAULT_TRIANGLE_MODE
        self.left_panel_width = LEFT_PANEL_WIDTH
        self._resizing_panel = False
        self._panel_min_width = 220
        self._skip_step_once = False
        self._clicked_this_frame = False
        self._skip_frames = 0

        # **Added grid_width and grid_height attributes**
        self.grid_width = 50      # Default grid width
        self.grid_height = 50     # Default grid height

        self.randomise_lifeforms()  # Initialize lifeforms
        self.initial_alive_percentage = 50 / 100.0  # Convert to 0-1 range
        self.session_id = str(uuid.uuid4())  # Generate a unique session ID
        self.data_recorder = DataRecorder(self.session_id)  # Initialize DataRecorder

        # Updated to include grid_width and grid_height
        self.grid = create_grid(
            lifeforms=self.lifeforms[:self.number_of_lifeforms],
            initial_alive_percentage=self.initial_alive_percentage,
            shape=self.shape,
            grid_width=self.grid_width,      # Pass grid_width
            grid_height=self.grid_height,     # Pass grid_height
            triangle_neighborhood_mode=self.triangle_mode
        )
        self.is_running = False
        self.is_paused = True
        self.generation = 0
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        # Limit how much history we plot/keep to avoid slow charts
        self.history_limit = 300
        
        # Auto-run settings
        self.auto_run_mode = False
        self.auto_run_sessions = 1
        self.auto_run_generations = 100  # Default value
        self.auto_run_session_count = 0
        print(f"auto_run_generations set to {self.auto_run_generations}")

        # Initialize SettingsPanel after grid_width and grid_height are set
        self.settings_panel = SettingsPanel(self)
        print("SettingsPanel initialized")

        # Initialize counters and history
        self.total_births = 0
        self.total_deaths = 0
        if hasattr(self.grid, 'grid'): #Numpy grid
            self.current_alive = np.sum(self.grid.grid > 0)
            self.current_dead = self.grid.grid.size - self.current_alive
            self.current_static = np.sum(self.grid.grid_lifespans > 10)
        else: #legacy grid
            self.current_alive = sum(cell.alive for cell in self.grid.cells.values())
            self.current_dead = len(self.grid.cells) - self.current_alive
            self.current_static = sum(1 for cell in self.grid.cells.values() if cell.alive_duration > 10)
        self.history_generations = [self.generation]
        self.history_alive = [self.current_alive]
        self.history_dead = [self.current_dead]
        self.history_static = [self.current_static]
        self.history_births = [0]
        self.history_deaths = [0]
        self.total_kills = {lifeform.id: 0 for lifeform in self.lifeforms[:self.number_of_lifeforms]}
        self.history_kills = {lifeform.id: [0] for lifeform in self.lifeforms[:self.number_of_lifeforms]}
        self.history_volatility = [0.0]
        self.crash_alert_message = None
        self.history_volatility = [0.0]
        self.crash_alert_message = None

        # Initialize lifeform alive counts
        self.lifeform_alive_counts = {lifeform.id: [] for lifeform in self.lifeforms[:self.number_of_lifeforms]}
        self.update_lifeform_alive_counts(initial=True)

        # Initialize chart_rect
        self.chart_rect = None
        # Calculate grid offsets based on initial chart position
        self.calculate_grid_offsets()

        # Initialize Tooltip
        self.tooltip = Tooltip()

    def randomise_lifeforms(self):
        """
        Randomly generate lifeforms with unique birth and survival rules.
        """
        self.lifeforms = []
        max_n = get_max_neighbors(self.shape, self.triangle_mode)
        for i in range(1, 11):  # Up to 10 lifeforms
            # Randomly select birth and survival rules
            birth_rules = sorted(random.sample(range(0, max_n + 1), random.randint(1, min(4, max_n + 1))))
            survival_rules = sorted(random.sample(range(0, max_n + 1), random.randint(1, min(4, max_n + 1))))
            lifeform = Lifeform(lifeform_id=i, birth_rules=birth_rules, survival_rules=survival_rules)
            self.lifeforms.append(lifeform)

    def create_grid(self):
        # Compute available screen space
        available_width, available_height = self.get_available_screen_space()

        self.grid = create_grid(
            lifeforms=self.lifeforms[:self.number_of_lifeforms],
            initial_alive_percentage=self.initial_alive_percentage,
            shape=self.shape,
            grid_width=self.grid_width,      # Pass grid_width
            grid_height=self.grid_height,    # Pass grid_height
            available_width=available_width,
            available_height=available_height,
            triangle_neighborhood_mode=self.triangle_mode
        )
        # Calculate grid offsets
        self.calculate_grid_offsets()

        # Reset counters and histories
        self.total_births = 0
        self.total_deaths = 0
        self.generation = 0
        if hasattr(self.grid, 'grid'): #Numpy grid
            self.current_alive = np.sum(self.grid.grid > 0)
            self.current_dead = self.grid.grid.size - self.current_alive
            self.current_static = np.sum(self.grid.grid_lifespans > 10)
        else: #legacy grid
            self.current_alive = sum(cell.alive for cell in self.grid.cells.values())
            self.current_dead = len(self.grid.cells) - self.current_alive
            self.current_static = sum(1 for cell in self.grid.cells.values() if cell.alive_duration > 10)
        self.history_generations = [self.generation]
        self.history_alive = [self.current_alive]
        self.history_dead = [self.current_dead]
        self.history_static = [self.current_static]
        self.history_births = [0]
        self.history_deaths = [0]
        self.total_kills = {lifeform.id: 0 for lifeform in self.lifeforms[:self.number_of_lifeforms]}
        self.history_kills = {lifeform.id: [0] for lifeform in self.lifeforms[:self.number_of_lifeforms]}

        # Initialize lifeform alive counts
        self.lifeform_alive_counts = {lifeform.id: [] for lifeform in self.lifeforms[:self.number_of_lifeforms]}
        self.update_lifeform_alive_counts(initial=True)

        # Initialize chart_rect
        self.chart_rect = None
        # Calculate grid offsets based on initial chart position
        self.calculate_grid_offsets()

    def calculate_grid_offsets(self):
        padding = 10  # Padding in pixels

        chart_rect = self.get_chart_rect()
        grid_start_y = chart_rect.bottom + padding

        grid_start_x = self.left_panel_width + padding  # Start to the right of the left panel for all shapes

        self.grid.calculate_offsets(start_x=grid_start_x, start_y=grid_start_y)

    def get_chart_rect(self):
        """
        Calculate and return the chart rectangle.
        """
        left_padding = 60  # Increased padding to accommodate left y-axis labels
        right_padding = 60  # Increased padding to accommodate right y-axis labels
        top_padding = 10
        chart_height = 180

        chart_rect = pygame.Rect(
            self.left_panel_width + left_padding,  # Start to the right of the left panel and left padding
            top_padding,
            self.screen.get_width() - self.left_panel_width - left_padding - right_padding,
            chart_height
        )
        return chart_rect

    def get_available_screen_space(self):
        """
        Calculate the available screen space for the grid based on UI elements.

        Returns:
            tuple: (available_width, available_height)
        """
        padding = 10  # Padding in pixels
        available_width = self.screen.get_width() - self.left_panel_width - padding * 2
        chart_rect = self.get_chart_rect()
        available_height = self.screen.get_height() - chart_rect.bottom - padding * 2
        return available_width, available_height

    def run(self):
        """
        Runs the main game loop.
        """
        while True:
            self.handle_events()
            if self._skip_step_once or self._clicked_this_frame or self._skip_frames > 0:
                self._skip_step_once = False
                self._clicked_this_frame = False
                if self._skip_frames > 0:
                    self._skip_frames -= 1
            elif not self.is_paused and self.is_running:
                self.update_simulation()
            elif self.auto_run_mode:
                self.auto_run_simulations()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def update_simulation(self):
        """
        Update the simulation by one generation.
        """
        births, deaths, static_cells, lifeform_alive_counts, lifeform_static_counts, lifeform_metrics, lifeform_kill_counts, changed_cells = self.grid.update()
        self.generation += 1
        self.total_births += births
        self.total_deaths += deaths
        self.current_alive = sum(lifeform_alive_counts.values())
        if hasattr(self.grid, 'grid'): #Numpy grid
            self.current_dead = self.grid.grid.size - self.current_alive
        else: #legacy grid
            self.current_dead = len(self.grid.cells) - self.current_alive
        self.current_static = static_cells

        # Update history
        self.history_generations.append(self.generation)
        self.history_alive.append(self.current_alive)
        self.history_dead.append(self.current_dead)
        self.history_static.append(self.current_static)
        self.history_births.append(self.total_births)
        self.history_deaths.append(self.total_deaths)
        total_cells = self.grid.grid.size if hasattr(self.grid, 'grid') else len(self.grid.cells)
        alive_norm = max(self.current_alive, 1)
        volatility_pct = (changed_cells / alive_norm) * 100 if alive_norm else 0
        self.history_volatility.append(volatility_pct)
        for lf_id in self.total_kills.keys():
            self.total_kills[lf_id] += lifeform_kill_counts.get(lf_id, 0)
            self.history_kills.setdefault(lf_id, []).append(self.total_kills[lf_id])
        # Keep kill history aligned even if new lifeforms appear
        for lf in self.lifeforms[:self.number_of_lifeforms]:
            if lf.id not in self.history_kills:
                self.history_kills[lf.id] = [0] * len(self.history_generations)
        # Sudden death detection: >80% drop within last 10 generations
        if len(self.history_alive) >= 10:
            prev_alive = self.history_alive[-10]
            if prev_alive > 0:
                drop = prev_alive - self.current_alive
                if drop > 0.8 * prev_alive:
                    self.is_paused = True
                    self.is_running = False
                    self.crash_alert_message = f"Sudden death: gen {self.generation} drop {prev_alive}->{self.current_alive}"
                    self.tooltip.update(self.crash_alert_message)
        # Stasis alert: high occupancy, low volatility
        occupancy = (self.current_alive / total_cells * 100) if total_cells else 0
        if occupancy > 80 and volatility_pct < 5:
            self.crash_alert_message = "CRITICAL STASIS DETECTED"
        else:
            self.crash_alert_message = None

        # Update lifeform alive counts
        self.update_lifeform_alive_counts(lifeform_alive_counts)
        self.trim_history()

        # Insert data into the database
        for lifeform in self.lifeforms[:self.number_of_lifeforms]:
            lifeform_id = lifeform.id
            birth_rules_array = sorted(lifeform.birth_rules)
            survival_rules_array = sorted(lifeform.survival_rules)
            alive_count = int(lifeform_alive_counts.get(lifeform_id, 0))
            static_count = int(lifeform_static_counts.get(lifeform_id, 0))
            metrics = lifeform_metrics.get(lifeform_id, {})
            self.data_recorder.insert_record(
                generation=self.generation,
                lifeform_id=lifeform_id,
                birth_rules=birth_rules_array,
                survival_rules=survival_rules_array,
                alive_count=alive_count,
                static_count=static_count,
                shape=self.shape,
                metrics=metrics
            )

    def auto_run_simulations(self):
        """
        Run simulations automatically for data collection.
        """
        if self.auto_run_session_count < self.auto_run_sessions:
            # Set random parameters
            self.initial_alive_percentage = random.uniform(0.01, 0.9)
            self.number_of_lifeforms = random.randint(1, 10)
            self.shape = random.choice(['triangle', 'square', 'hexagon'])
            self.randomise_lifeforms()

            # Create new grid with random settings
            self.create_grid()

            # Run the simulation for the specified number of generations
            num_generations = self.auto_run_generations  # Use the user-defined value
            for _ in range(num_generations):
                self.update_simulation()

            self.auto_run_session_count += 1
        else:
            # Auto-run complete
            self.auto_run_mode = False
            print(f"Auto-run completed: {self.auto_run_sessions} sessions executed.")
            self.data_recorder.close()
            pygame.quit()
            quit()

    def start_auto_run(self, num_sessions):
        """
        Initialize auto-run mode with the specified number of sessions.

        Args:
            num_sessions (int): The number of sessions to run automatically.
        """
        self.auto_run_mode = True
        self.auto_run_sessions = num_sessions
        self.auto_run_session_count = 0
        self.is_running = False
        self.is_paused = True  # Ensure normal simulation is paused

    def handle_events(self):
        """
        Handle user input and events.
        """
        mouse_pos = pygame.mouse.get_pos()
        self.tooltip.update('')  # Reset tooltip

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Close data recorder
                if hasattr(self, 'data_recorder') and self.data_recorder:
                    self.data_recorder.close()
                pygame.quit()
                quit()
            # Always handle settings panel events
            self.settings_panel.handle_event(event)
            if event.type in (pygame.VIDEORESIZE, pygame.WINDOWRESIZED):
                # Some backends send resize events without .size; fall back to current window size.
                new_size = getattr(event, "size", self.screen.get_size())
                self.handle_resize(new_size)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Start panel resize drag if near divider
                    if abs(event.pos[0] - self.left_panel_width) <= 6:
                        self._resizing_panel = True
                        continue
                    self.grid.handle_click(event.pos)
                    self._clicked_this_frame = True
                    # Ensure no simulation step is triggered in this frame
                    self._skip_step_once = True
                    self._skip_frames = max(self._skip_frames, 2)
                    # Update current alive and dead counts
                    if hasattr(self.grid, 'grid'): #Numpy grid
                        self.current_alive = np.sum(self.grid.grid > 0)
                        self.current_dead = self.grid.grid.size - self.current_alive
                        self.current_static = np.sum(self.grid.grid_lifespans > 10)
                    else: #legacy grid
                        self.current_alive = sum(cell.alive for cell in self.grid.cells.values())
                        self.current_dead = len(self.grid.cells) - self.current_alive
                        self.current_static = sum(1 for cell in self.grid.cells.values() if cell.alive_duration > 10)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self._resizing_panel:
                    self._resizing_panel = False
            elif event.type == pygame.MOUSEMOTION:
                if self._resizing_panel:
                    new_width = max(self._panel_min_width, min(event.pos[0], self.screen.get_width() - 200))
                    if new_width != self.left_panel_width:
                        self.left_panel_width = new_width
                        self.handle_resize(self.screen.get_size())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused
                    self.is_running = True
                elif event.key == pygame.K_r:
                    self.create_grid()
                    self.is_paused = True
                elif event.key == pygame.K_n:
                    self.settings_panel.randomise_lifeforms()
                    self.create_grid()
                    self.is_paused = True
                elif event.key == pygame.K_s:
                    if self.is_paused:
                        self.update_simulation()

    def handle_resize(self, size):
        """
        Respond to window resize without fighting the window manager.
        """
        if self.screen.get_size() != size:
            self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)

        # Recompute available space and cell sizes without resetting state
        available_width, available_height = self.get_available_screen_space()
        if hasattr(self.grid, 'resize'):
            self.grid.resize(available_width, available_height)
        self.calculate_grid_offsets()  # Recalculate offsets on window resize
        # Refresh tooltip state after layout change
        self.update_tooltip(pygame.mouse.get_pos())

    def update_tooltip(self, mouse_pos):
        """
        Update the tooltip text based on the current hovered element.
        """
        tooltip_text = ''
        # Check if hovering over buttons in settings panel
        if self.settings_panel.hovered_button:
            tooltip_text = f'Click to {self.settings_panel.hovered_button}'
        # Check if hovering over grid cells
        else:
            # You can add more tooltip conditions here if needed
            pass
        self.tooltip.update(tooltip_text)

    def update_settings(self):
        """
        Apply updated settings from the settings panel.
        """
        # Update number_of_lifeforms and other settings is handled via callbacks
        # Recreate the grid with updated settings and lifeforms
        self.create_grid()

    def apply_ruleset_to_lifeform(self, lifeform_index, birth_rules_str, survival_rules_str, name=None):
        """
        Applies a new ruleset to a specific lifeform and refreshes the game.

        Args:
            lifeform_index (int): The 0-based index of the lifeform to modify.
            birth_rules_str (str): A comma-separated string of birth rules.
            survival_rules_str (str): A comma-separated string of survival rules.
            name (str, optional): An optional name for the lifeform.
        """
        if not (0 <= lifeform_index < len(self.lifeforms)):
            print(f"Error: Invalid lifeform_index {lifeform_index}")
            return

        try:
            # Parse rule strings into lists of integers
            birth_rules = [int(r.strip()) for r in birth_rules_str.split(',') if r.strip()]
            survival_rules = [int(r.strip()) for r in survival_rules_str.split(',') if r.strip()]
        except ValueError as e:
            print(f"Error parsing rules: {e}")
            return
            
        # Apply the new rules
        lifeform = self.lifeforms[lifeform_index]
        lifeform.birth_rules = sorted(birth_rules)
        lifeform.survival_rules = sorted(survival_rules)
        if name:
            lifeform.name = name

        # Update the settings panel UI to reflect the new rules
        self.settings_panel.update_lifeform_rules()
        
        # Reset the grid to apply the changes immediately
        self.create_grid()
        print(f"Applied new rules to Lifeform {lifeform.id} and reset grid.")

    def update_lifeform_alive_counts(self, lifeform_alive_counts=None, initial=False):
        """
        Update the counts of alive cells per lifeform.

        Args:
            lifeform_alive_counts (dict, optional): Dictionary mapping lifeform IDs to alive counts.
            initial (bool): If True, initializes the counts based on the current grid.
        """
        if initial:
            if hasattr(self.grid, 'grid'): #Numpy grid
                for lifeform in self.lifeforms[:self.number_of_lifeforms]:
                    count = np.sum(self.grid.grid == lifeform.id)
                    self.lifeform_alive_counts[lifeform.id].append(count)
            else: #legacy grid
                # Initialize with current counts from the grid
                for lifeform in self.lifeforms[:self.number_of_lifeforms]:
                    count = sum(
                        cell.alive and cell.lifeform_id == lifeform.id
                        for cell in self.grid.cells.values()
                    )
                    self.lifeform_alive_counts[lifeform.id].append(count)
        elif lifeform_alive_counts is not None:
            # Append counts to existing history
            for lifeform_id, count in lifeform_alive_counts.items():
                if lifeform_id in self.lifeform_alive_counts:
                    self.lifeform_alive_counts[lifeform_id].append(count)
                else:
                    self.lifeform_alive_counts[lifeform_id] = [count]

    def trim_history(self):
        """
        Keep history arrays capped so chart drawing stays fast.
        """
        def trim(lst):
            excess = len(lst) - self.history_limit
            if excess > 0:
                del lst[:excess]

        for lst in [
            self.history_generations,
            self.history_alive,
            self.history_dead,
            self.history_static,
            self.history_births,
            self.history_deaths,
            self.history_volatility,
        ]:
            trim(lst)

        for counts in self.lifeform_alive_counts.values():
            trim(counts)
        for counts in self.history_kills.values():
            trim(counts)

    def draw(self):
        """
        Draw the game elements on the screen with improved visuals.
        """
        self.screen.fill(BACKGROUND_COLOR)
        # Draw line chart
        self.draw_line_chart()
        # Draw grid
        self.grid.draw(self.screen)

        # Draw left panel background with rounded corners
        panel_rect = pygame.Rect(0, 0, LEFT_PANEL_WIDTH, self.screen.get_height())
        panel_rect = pygame.Rect(0, 0, self.left_panel_width, self.screen.get_height())
        pygame.draw.rect(self.screen, PANEL_BACKGROUND_COLOR, panel_rect, border_radius=10)

        # Display text within the left panel using improved font
        text_x = 20  # Increased padding
        y_offset = 20

        # Use a larger font for headings
        heading_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE + 4, bold=True)
        gen_text = heading_font.render(f'Generation: {self.generation}', True, TEXT_COLOR)
        self.screen.blit(gen_text, (text_x, y_offset))
        y_offset += 40

        # Display instructions with better spacing
        instructions = [
            "Controls:",
            "Space: Start/Pause",
            "R: Reset Grid",
            "N: New Random Grid",
            "S: Step Forward (paused)",
            "Click: Toggle Cell",
        ]
        for text in instructions:
            instr_text = self.font.render(text, True, TEXT_COLOR)
            self.screen.blit(instr_text, (text_x, y_offset))
            y_offset += 25

        y_offset += 10  # Add some spacing

        # Display counts with better spacing
        counts = [
            f"Total Births: {self.total_births}",
            f"Total Deaths: {self.total_deaths}",
            f"Current Alive: {self.current_alive}",
            f"Current Dead: {self.current_dead}",
            f"Static Cells: {self.current_static}",
        ]
        if self.crash_alert_message:
            counts.append(self.crash_alert_message)
        for text in counts:
            counts_text = self.font.render(text, True, TEXT_COLOR)
            self.screen.blit(counts_text, (text_x, y_offset))
            y_offset += 25

        y_offset += 10  # Add some spacing

        # Draw settings panel within the left panel
        self.settings_panel.draw(self.screen, x=10, y=y_offset, width=self.left_panel_width - 20)

        # Draw tooltip
        self.tooltip.draw(self.screen, pygame.mouse.get_pos())

    def draw_line_chart(self):
        """
        Draws the line chart of counts over generations with lifeform alive counts and static cells.
        """
        # Get chart area
        chart_rect = self.get_chart_rect()
        self.chart_rect = chart_rect  # Store for use in positioning the grid
        pygame.draw.rect(self.screen, (50, 50, 50), chart_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, chart_rect, 2)

        # Determine max generations
        max_generations = min(self.history_limit, len(self.history_generations))

        # Determine max count for y-axis (population/static)
        max_count = max(
            [1] +
            [max(counts[-max_generations:]) if counts[-max_generations:] else 1 for counts in self.lifeform_alive_counts.values()] +
            ([max(self.history_static[-max_generations:]) if self.history_static[-max_generations:] else 1])
        )

        # Determine max for kill axis (separate scale)
        kill_max = max(
            [1] +
            [max(counts[-max_generations:]) if counts[-max_generations:] else 0 for counts in self.history_kills.values()] +
            [max(self.history_volatility[-max_generations:]) if self.history_volatility[-max_generations:] else 0]
        )

        if len(self.history_generations) > 1:
            # Scaling factors
            x_scale = chart_rect.width / (len(self.history_generations) - 1)
            y_scale = chart_rect.height / max_count
            kill_y_scale = chart_rect.height / kill_max if kill_max > 0 else chart_rect.height

            # Plot lines for each lifeform
            for lifeform in self.lifeforms[:self.number_of_lifeforms]:
                lifeform_id = lifeform.id
                counts = self.lifeform_alive_counts[lifeform_id][-max_generations:]
                points = [
                    (chart_rect.x + i * x_scale,
                     chart_rect.bottom - counts[i] * y_scale)
                    for i in range(len(counts))
                ]
                pygame.draw.lines(self.screen, lifeform.color_alive, False, points, 2)

            # Plot static cells line
            data_static = self.history_static[-max_generations:]
            points_static = [
                (chart_rect.x + i * x_scale,
                 chart_rect.bottom - data_static[i] * y_scale)
            for i in range(len(data_static))
            ]
            # Define color for static cells line
            color_static_line = (255, 255, 255)  # White color
            pygame.draw.lines(self.screen, color_static_line, False, points_static, 2)

            # Plot kill lines
            for lifeform in self.lifeforms[:self.number_of_lifeforms]:
                lf_id = lifeform.id
                kills = self.history_kills.get(lf_id, [])[-max_generations:]
                if not kills:
                    continue
                points = [
                    (chart_rect.x + i * x_scale,
                     chart_rect.bottom - kills[i] * kill_y_scale)
                    for i in range(len(kills))
                ]
                pygame.draw.lines(self.screen, lifeform.color_static, False, points, 1)

            # Plot volatility line (right axis)
            vol_color = (255, 215, 0)  # Gold
            vol_data = self.history_volatility[-max_generations:]
            vol_points = [
                (chart_rect.x + i * x_scale,
                 chart_rect.bottom - vol_data[i] * kill_y_scale)
                for i in range(len(vol_data))
            ]
            pygame.draw.lines(self.screen, vol_color, False, vol_points, 2)

            # Draw y-axis labels
            y_axis_ticks = 5  # Number of ticks on y-axis
            for i in range(y_axis_ticks + 1):
                y_value = int(i * max_count / y_axis_ticks)
                y_pos = chart_rect.bottom - i * chart_rect.height / y_axis_ticks
                label = self.font.render(str(y_value), True, TEXT_COLOR)
                label_rect = label.get_rect()
                label_x = chart_rect.x - label_rect.width - 10  # Adjusted spacing
                self.screen.blit(label, (label_x, y_pos - label_rect.height / 2))
                # Draw tick marks
                pygame.draw.line(self.screen, TEXT_COLOR, (chart_rect.x - 5, y_pos), (chart_rect.x, y_pos))

            # Right y-axis for kills
            for i in range(y_axis_ticks + 1):
                y_value = int(i * kill_max / y_axis_ticks)
                y_pos = chart_rect.bottom - i * chart_rect.height / y_axis_ticks
                label = self.font.render(str(y_value), True, TEXT_COLOR)
                label_rect = label.get_rect()
                label_x = chart_rect.right + 5
                self.screen.blit(label, (label_x, y_pos - label_rect.height / 2))
                pygame.draw.line(self.screen, TEXT_COLOR, (chart_rect.right, y_pos), (chart_rect.right + 5, y_pos))

            # Add legend
            legend_texts = []
            for lifeform in self.lifeforms[:self.number_of_lifeforms]:
                legend_texts.append((f"Lifeform {lifeform.id}", lifeform.color_alive))
                legend_texts.append((f"LF {lifeform.id} Kills", lifeform.color_static))
            legend_texts.append(("Static Cells", color_static_line))
            legend_texts.append(("Volatility %", vol_color))

            for i, (text, color) in enumerate(legend_texts):
                legend = self.font.render(text, True, color)
                self.screen.blit(legend, (chart_rect.x + 10, chart_rect.y + 10 + i * 20))

if __name__ == '__main__':
    game = GameOfLife()
    game.run()

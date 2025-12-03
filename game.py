# game.py

import pygame
import uuid
from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    PANEL_BACKGROUND_COLOR,
    FONT_NAME,
    FONT_SIZE,
    TEXT_COLOR,
    LEFT_PANEL_WIDTH
)
from settings_panel import SettingsPanel
from grid_factory import create_grid
from tooltip import Tooltip
from data_recorder import DataRecorder  # Ensure DataRecorder is imported
from lifeform import Lifeform  # Ensure Lifeform is imported
import random

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
        self.shape = 'triangle'  # Initialize grid shape

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
            grid_height=self.grid_height     # Pass grid_height
        )
        self.is_running = False
        self.is_paused = True
        self.generation = 0
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        
        # Auto-run settings
        self.auto_run_mode = False
        self.auto_run_sessions = 0
        self.auto_run_generations = 100  # Default value
        self.auto_run_session_count = 0
        print(f"auto_run_generations set to {self.auto_run_generations}")

        # Initialize SettingsPanel after grid_width and grid_height are set
        self.settings_panel = SettingsPanel(self)
        print("SettingsPanel initialized")

        # Initialize counters and history
        self.total_births = 0
        self.total_deaths = 0
        self.current_alive = sum(cell.alive for cell in self.grid.cells.values())
        self.current_dead = len(self.grid.cells) - self.current_alive
        self.current_static = sum(1 for cell in self.grid.cells.values() if cell.alive_duration > 10)
        self.history_generations = [self.generation]
        self.history_alive = [self.current_alive]
        self.history_dead = [self.current_dead]
        self.history_static = [self.current_static]
        self.history_births = [0]
        self.history_deaths = [0]

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
        for i in range(1, 11):  # Up to 10 lifeforms
            # Randomly select birth and survival rules
            birth_rules = sorted(random.sample(range(0, 9), random.randint(1, 4)))
            survival_rules = sorted(random.sample(range(0, 9), random.randint(1, 4)))
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
            available_height=available_height
        )
        # Calculate grid offsets
        self.calculate_grid_offsets()

        # Reset counters and histories
        self.total_births = 0
        self.total_deaths = 0
        self.generation = 0
        self.current_alive = sum(cell.alive for cell in self.grid.cells.values())
        self.current_dead = len(self.grid.cells) - self.current_alive
        self.current_static = sum(1 for cell in self.grid.cells.values() if cell.alive_duration > 10)
        self.history_generations = [self.generation]
        self.history_alive = [self.current_alive]
        self.history_dead = [self.current_dead]
        self.history_static = [self.current_static]
        self.history_births = [0]
        self.history_deaths = [0]

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

        grid_start_x = LEFT_PANEL_WIDTH + padding  # Start to the right of the left panel for all shapes

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
            LEFT_PANEL_WIDTH + left_padding,  # Start to the right of the left panel and left padding
            top_padding,
            self.screen.get_width() - LEFT_PANEL_WIDTH - left_padding - right_padding,
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
        available_width = self.screen.get_width() - LEFT_PANEL_WIDTH - padding * 2
        chart_rect = self.get_chart_rect()
        available_height = self.screen.get_height() - chart_rect.bottom - padding * 2
        return available_width, available_height

    def run(self):
        """
        Runs the main game loop.
        """
        while True:
            self.handle_events()
            if not self.is_paused and self.is_running:
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
        # Update the grid and get per-lifeform counts and metrics
        births, deaths, static_cells, lifeform_alive_counts, lifeform_static_counts, lifeform_metrics = self.grid.update()
        self.generation += 1
        self.total_births += births
        self.total_deaths += deaths
        self.current_alive = sum(cell.alive for cell in self.grid.cells.values())
        self.current_dead = len(self.grid.cells) - self.current_alive
        self.current_static = static_cells

        # Update history
        self.history_generations.append(self.generation)
        self.history_alive.append(self.current_alive)
        self.history_dead.append(self.current_dead)
        self.history_static.append(self.current_static)
        self.history_births.append(self.total_births)
        self.history_deaths.append(self.total_deaths)

        # Update lifeform alive counts
        self.update_lifeform_alive_counts(lifeform_alive_counts)

        # Insert data into the database
        for lifeform in self.lifeforms[:self.number_of_lifeforms]:
            lifeform_id = lifeform.id
            birth_rules_array = [1 if i in lifeform.birth_rules else 0 for i in range(9)]  # Adjusted to 9 for consistency
            survival_rules_array = [1 if i in lifeform.survival_rules else 0 for i in range(9)]
            alive_count = lifeform_alive_counts.get(lifeform_id, 0)
            static_count = lifeform_static_counts.get(lifeform_id, 0)
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
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.calculate_grid_offsets()  # Recalculate offsets on window resize
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.grid.handle_click(event.pos)
                    # Update current alive and dead counts
                    self.current_alive = sum(cell.alive for cell in self.grid.cells.values())
                    self.current_dead = len(self.grid.cells) - self.current_alive
                    self.current_static = sum(1 for cell in self.grid.cells.values() if cell.alive_duration > 10)
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

        # Update tooltip based on hovered element
        self.update_tooltip(mouse_pos)

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

    def update_lifeform_alive_counts(self, lifeform_alive_counts=None, initial=False):
        """
        Update the counts of alive cells per lifeform.

        Args:
            lifeform_alive_counts (dict, optional): Dictionary mapping lifeform IDs to alive counts.
            initial (bool): If True, initializes the counts based on the current grid.
        """
        if initial:
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
        for text in counts:
            counts_text = self.font.render(text, True, TEXT_COLOR)
            self.screen.blit(counts_text, (text_x, y_offset))
            y_offset += 25

        y_offset += 10  # Add some spacing

        # Draw settings panel within the left panel
        self.settings_panel.draw(self.screen, x=10, y=y_offset, width=LEFT_PANEL_WIDTH - 20)

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
        max_generations = min(1000, len(self.history_generations))

        # Determine max count for y-axis
        max_count = max(
            [1] +
            [max(counts[-max_generations:]) if counts[-max_generations:] else 1 for counts in self.lifeform_alive_counts.values()] +
            ([max(self.history_static[-max_generations:]) if self.history_static[-max_generations:] else 1])
        )

        if len(self.history_generations) > 1:
            # Scaling factors
            x_scale = chart_rect.width / (len(self.history_generations) - 1)
            y_scale = chart_rect.height / max_count

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

            # Add legend
            legend_texts = []
            for lifeform in self.lifeforms[:self.number_of_lifeforms]:
                legend_texts.append((f"Lifeform {lifeform.id}", lifeform.color_alive))
            legend_texts.append(("Static Cells", color_static_line))

            for i, (text, color) in enumerate(legend_texts):
                legend = self.font.render(text, True, color)
                self.screen.blit(legend, (chart_rect.x + 10, chart_rect.y + 10 + i * 20))

if __name__ == '__main__':
    game = GameOfLife()
    game.run()

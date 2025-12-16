# game.py

import pygame
import uuid
import numpy as np
from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    PANEL_BACKGROUND_COLOR,
    TEXT_COLOR,
    LEFT_PANEL_WIDTH,
    DEFAULT_TRIANGLE_MODE,
    FONT_NAME,
    FONT_SIZE_XS,
    FONT_SIZE_SM,
    FONT_SIZE_BASE,
    FONT_SIZE_LG,
    FONT_SIZE_XL,
    FONT_SIZE_2XL,
    ACCENT_PRIMARY,
    ACCENT_SECONDARY,
    ACCENT_SUCCESS,
    ACCENT_WARNING,
    ACCENT_DANGER,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    BUTTON_TEXT_COLOR,
    CHART_BACKGROUND,
    CHART_GRID_LINES,
    CHART_AXIS_COLOR,
)
from settings_panel import SettingsPanel
from grid_factory import create_grid
from tooltip import TooltipManager
from data_recorder import DataRecorder  # Ensure DataRecorder is imported
from lifeform import Lifeform  # Ensure Lifeform is imported
import random
from neighbor_utils import get_max_neighbors

class FontManager:
    def __init__(self):
        self.fonts = {
            'xs': pygame.font.SysFont(FONT_NAME, FONT_SIZE_XS),
            'sm': pygame.font.SysFont(FONT_NAME, FONT_SIZE_SM),
            'base': pygame.font.SysFont(FONT_NAME, FONT_SIZE_BASE),
            'lg': pygame.font.SysFont(FONT_NAME, FONT_SIZE_LG),
            'xl': pygame.font.SysFont(FONT_NAME, FONT_SIZE_XL, bold=True),
            '2xl': pygame.font.SysFont(FONT_NAME, FONT_SIZE_2XL, bold=True),
            'mono': pygame.font.SysFont('Consolas', FONT_SIZE_SM),  # For numbers
        }
    
    def get(self, size='base'):
        return self.fonts.get(size, self.fonts['base'])

class ActionButton:
    """A styled action button with icon and tooltip."""
    
    def __init__(self, icon, label, shortcut, action, font, 
                 primary=False, danger=False):
        self.icon = icon
        self.label = label
        self.shortcut = shortcut
        self.action = action
        self.font = font
        self.primary = primary
        self.danger = danger
        self.rect = None
        self.hovered = False
        
    def draw(self, surface, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        
        # Determine colors
        if self.primary:
            bg = ACCENT_PRIMARY if not self.hovered else (119, 122, 255)
        elif self.danger:
            bg = ACCENT_DANGER if not self.hovered else (255, 140, 140)
        else:
            bg = BUTTON_COLOR if not self.hovered else BUTTON_HOVER_COLOR
            
        # Draw button
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        
        # Draw icon and label
        content = f"{self.icon} {self.label}"
        text_surf = self.font.render(content, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Show shortcut on hover
        if self.hovered:
            shortcut_surf = self.font.render(f"[{self.shortcut}]", True, (180, 180, 190))
            shortcut_rect = shortcut_surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 4))
            surface.blit(shortcut_surf, shortcut_rect)


class ActionBar:
    """Horizontal bar of action buttons."""
    
    def __init__(self, game, font_manager):
        self.game = game
        self.font_manager = font_manager
        self.font = font_manager.get('base')
        self.buttons = [
            ActionButton("▶", "Play", "Space", self.toggle_play, self.font, primary=True),
            ActionButton("↺", "Reset", "R", self.reset, self.font),
            ActionButton("⏭", "Step", "S", self.step, self.font),
            ActionButton("🎲", "New", "N", self.new_random, self.font),
        ]
        
    def toggle_play(self):
        self.game.is_paused = not self.game.is_paused
        self.game.is_running = True
        # Update button icon
        self.buttons[0].icon = "⏸" if not self.game.is_paused else "▶"
        self.buttons[0].label = "Pause" if not self.game.is_paused else "Play"
        
    def reset(self):
        self.game.create_grid()
        
    def step(self):
        if self.game.is_paused:
            self.game.update_simulation()
            
    def new_random(self):
        self.game.randomise_lifeforms()
        self.game.create_grid()
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.rect and btn.rect.collidepoint(event.pos):
                    btn.action()
                    return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle_play()
                return True
            elif event.key == pygame.K_r:
                self.reset()
                return True
            elif event.key == pygame.K_s:
                self.step()
                return True
            elif event.key == pygame.K_n:
                self.new_random()
                return True
        return False
    
    def draw(self, surface, x, y, width):
        button_gap = 8
        button_width = (width - (len(self.buttons) - 1) * button_gap) // len(self.buttons)
        button_height = 36
        
        for i, btn in enumerate(self.buttons):
            btn_x = x + i * (button_width + button_gap)
            btn.draw(surface, btn_x, y, button_width, button_height)
        
        return button_height + 12  # Return total height including padding

class StatCard:
    """A styled statistic display card."""
    
    def __init__(self, label, icon, color, font_manager):
        self.label = label
        self.icon = icon
        self.color = color
        self.font_manager = font_manager
        self.value = 0
        self.previous_value = 0
        self.trend = 0  # -1, 0, 1
        self.animated_value = AnimatedValue(initial=self.value)
        
    def update(self, new_value):
        self.previous_value = self.value
        self.value = new_value
        self.animated_value.set(new_value)
        if new_value > self.previous_value:
            self.trend = 1
        elif new_value < self.previous_value:
            self.trend = -1
        else:
            self.trend = 0
            
    def draw(self, surface, x, y, width, height):
        # Card background
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (35, 38, 48), card_rect, border_radius=8)
        
        # Accent bar on left
        accent_rect = pygame.Rect(x, y, 4, height)
        pygame.draw.rect(surface, self.color, accent_rect, 
                        border_top_left_radius=8, border_bottom_left_radius=8)
        
        # Icon
        icon_surf = self.font_manager.get('lg').render(self.icon, True, self.color)
        surface.blit(icon_surf, (x + 12, y + 8))
        
        # Value (large, monospace)
        self.animated_value.update()
        value_text = f"{self.animated_value.get_display_value():,}"
        value_surf = self.font_manager.get('mono').render(value_text, True, TEXT_COLOR)
        surface.blit(value_surf, (x + 12, y + 28))
        
        # Label
        label_surf = self.font_manager.get('xs').render(self.label, True, (160, 163, 175))
        surface.blit(label_surf, (x + 12, y + 48))
        
        # Trend indicator
        if self.trend != 0:
            trend_icon = "↑" if self.trend > 0 else "↓"
            trend_color = ACCENT_SUCCESS if self.trend > 0 else ACCENT_DANGER
            trend_surf = self.font_manager.get('sm').render(trend_icon, True, trend_color)
            surface.blit(trend_surf, (x + width - 20, y + 8))


class StatisticsPanel:
    """Panel displaying simulation statistics."""
    
    def __init__(self, game, font_manager):
        self.game = game
        self.font_manager = font_manager
        self.cards = {
            'generation': StatCard("Generation", "⏱", ACCENT_PRIMARY, font_manager),
            'population': StatCard("Population", "👥", ACCENT_SUCCESS, font_manager),
            'births': StatCard("Births", "✚", ACCENT_SECONDARY, font_manager),
            'deaths': StatCard("Deaths", "✖", ACCENT_DANGER, font_manager),
        }
        
    def update(self):
        self.cards['generation'].update(self.game.generation)
        self.cards['population'].update(self.game.current_alive)
        self.cards['births'].update(self.game.total_births)
        self.cards['deaths'].update(self.game.total_deaths)
        
    def draw(self, surface, x, y, width):
        card_height = 68
        card_gap = 8
        cards_per_row = 2
        card_width = (width - card_gap) // cards_per_row
        
        card_items = list(self.cards.items())

        for i, (key, card) in enumerate(card_items):
            col = i % cards_per_row
            row = i // cards_per_row
            card_x = x + col * (card_width + card_gap)
            card_y = y + row * (card_height + card_gap)
            card.draw(surface, card_x, card_y, card_width, card_height)
        
        total_height = ((len(self.cards) + cards_per_row - 1) // cards_per_row) * (card_height + card_gap)
        return total_height

class KeyboardHints:
    """Displays keyboard shortcuts on demand."""
    
    SHORTCUTS = [
        ("Space", "Play/Pause simulation"),
        ("R", "Reset grid"),
        ("N", "New random grid"),
        ("S", "Step forward (when paused)"),
        ("Click", "Toggle cell state"),
        ("Scroll", "Adjust panel scroll"),
        ("?", "Show/hide this help"),
    ]
    
    def __init__(self, font_manager):
        self.font_manager = font_manager
        self.visible = False
        
    def toggle(self):
        self.visible = not self.visible
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                # ? key pressed
                self.toggle()
                return True
            elif event.key == pygame.K_ESCAPE and self.visible:
                self.visible = False
                return True
        return False
    
    def draw(self, surface):
        if not self.visible:
            # Draw small hint in corner
            hint_text = "Press ? for shortcuts"
            hint_surf = self.font_manager.get('xs').render(hint_text, True, (120, 123, 140))
            surface.blit(hint_surf, (surface.get_width() - hint_surf.get_width() - 16, 
                                     surface.get_height() - 24))
            return
            
        # Draw overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Draw shortcuts panel
        panel_width = 320
        panel_height = len(self.SHORTCUTS) * 36 + 60
        panel_x = (surface.get_width() - panel_width) // 2
        panel_y = (surface.get_height() - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, PANEL_BACKGROUND_COLOR, panel_rect, border_radius=12)
        pygame.draw.rect(surface, ACCENT_PRIMARY, panel_rect, 2, border_radius=12)
        
        # Title
        title = self.font_manager.get('lg').render("Keyboard Shortcuts", True, TEXT_COLOR)
        surface.blit(title, (panel_x + 20, panel_y + 16))
        
        # Shortcuts list
        y = panel_y + 52
        for key, description in self.SHORTCUTS:
            # Key badge
            key_surf = self.font_manager.get('mono').render(key, True, ACCENT_PRIMARY)
            key_rect = key_surf.get_rect()
            badge_rect = pygame.Rect(panel_x + 20, y, max(key_rect.width + 16, 48), 28)
            pygame.draw.rect(surface, (45, 48, 62), badge_rect, border_radius=4)
            surface.blit(key_surf, (badge_rect.x + (badge_rect.width - key_rect.width) // 2, 
                                   badge_rect.y + 6))
            
            # Description
            desc_surf = self.font_manager.get('sm').render(description, True, TEXT_COLOR)
            surface.blit(desc_surf, (panel_x + 80, y + 6))
            
            y += 36

class LayoutManager:
    """Manages responsive layout calculations."""
    
    MIN_PANEL_WIDTH = 240
    MAX_PANEL_WIDTH = 400
    PANEL_WIDTH_RATIO = 0.25  # 25% of window width
    
    def __init__(self, window_width, window_height):
        self.update(window_width, window_height)
        
    def update(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        
        # Calculate panel width
        self.panel_width = int(window_width * self.PANEL_WIDTH_RATIO)
        self.panel_width = max(self.MIN_PANEL_WIDTH, 
                               min(self.MAX_PANEL_WIDTH, self.panel_width))
        
        # Calculate chart dimensions
        self.chart_margin = 16
        self.chart_x = self.panel_width + self.chart_margin + 50  # Account for y-axis
        self.chart_width = window_width - self.chart_x - 60  # Right margin
        self.chart_height = min(180, int(window_height * 0.25))
        self.chart_y = self.chart_margin
        
        # Calculate grid area
        self.grid_x = self.panel_width + self.chart_margin
        self.grid_y = self.chart_y + self.chart_height + self.chart_margin + 20
        self.grid_width = window_width - self.grid_x - self.chart_margin
        self.grid_height = window_height - self.grid_y - self.chart_margin
        
    def get_panel_rect(self):
        return pygame.Rect(0, 0, self.panel_width, self.window_height)
    
    def get_chart_rect(self):
        return pygame.Rect(self.chart_x, self.chart_y, self.chart_width, self.chart_height)
    
    def get_grid_rect(self):
        return pygame.Rect(self.grid_x, self.grid_y, self.grid_width, self.grid_height)

class AnimatedValue:
    """Smoothly interpolates numeric values for display."""
    
    def __init__(self, initial=0, speed=0.15):
        self.target = initial
        self.current = float(initial)
        self.speed = speed
        
    def set(self, new_value):
        self.target = new_value
        
    def update(self):
        diff = self.target - self.current
        self.current += diff * self.speed
        
    def get_display_value(self):
        return int(round(self.current))

class GameOfLife:
    """
    Manages the main game loop and user interactions.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Conway's Game of Life Simulator")
        self.clock = self.clock = pygame.time.Clock()
        self.font_manager = FontManager()
        
        # Initialize settings
        self.fps = 30  # Ensure this is set before SettingsPanel
        self.number_of_lifeforms = 1  # Default to 1 lifeform
        self.lifeforms = []
        self.shape = 'square'  # Initialize grid shape
        self.triangle_mode = DEFAULT_TRIANGLE_MODE
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
        
        # Initialize Tooltip
        self.tooltip = TooltipManager(self.font_manager.get('sm'))

        # Initialize Action Bar
        self.action_bar = ActionBar(self, self.font_manager)

        # Initialize Statistics Panel
        self.statistics_panel = StatisticsPanel(self, self.font_manager)

        # Initialize Keyboard Hints
        self.keyboard_hints = KeyboardHints(self.font_manager)

        # Initialize Layout Manager
        self.layout = LayoutManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.left_panel_width = self.layout.panel_width

        # Calculate grid offsets based on initial chart position
        self.calculate_grid_offsets()

        # Capture initial session metadata
        self.record_session_metadata()

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
        grid_rect = self.layout.get_grid_rect()

        self.grid = create_grid(
            lifeforms=self.lifeforms[:self.number_of_lifeforms],
            initial_alive_percentage=self.initial_alive_percentage,
            shape=self.shape,
            grid_width=self.grid_width,      # Pass grid_width
            grid_height=self.grid_height,    # Pass grid_height
            available_width=grid_rect.width,
            available_height=grid_rect.height,
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

        # Update session metadata after grid (re)creation
        self.record_session_metadata()

    def calculate_grid_offsets(self):
        grid_rect = self.layout.get_grid_rect()
        self.grid.calculate_offsets(start_x=grid_rect.x, start_y=grid_rect.y)

    def record_session_metadata(self):
        """
        Store environment parameters for this session so DB rows can be filtered by setup.
        """
        neighborhood = self.triangle_mode if self.shape == "triangle" else "N/A"
        total_gens = getattr(self, "auto_run_generations", None)
        self.data_recorder.record_session_meta(
            grid_width=self.grid_width,
            grid_height=self.grid_height,
            grid_shape=self.shape,
            neighborhood_mode=neighborhood,
            initial_alive_percentage=self.initial_alive_percentage,
            total_generations=total_gens
        )

    def get_chart_rect(self):
        return self.layout.get_chart_rect()

    def get_available_screen_space(self):
        grid_rect = self.layout.get_grid_rect()
        return grid_rect.width, grid_rect.height

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
        self.animated_generation.set(self.generation)
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

        # Update statistics panel
        self.statistics_panel.update()

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
        self.tooltip.clear()  # Reset tooltip

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Close data recorder
                if hasattr(self, 'data_recorder') and self.data_recorder:
                    self.data_recorder.close()
                pygame.quit()
                quit()
            
            # Handle collapsible section events
            for section in self.settings_panel.sections.values():
                if section.handle_event(event):
                    break  # Event was handled

            # Always handle settings panel events
            self.settings_panel.handle_event(event)

            # Handle keyboard hints events
            if self.keyboard_hints.handle_event(event):
                continue

            # Handle action bar events
            if self.action_bar.handle_event(event):
                continue

            if event.type in (pygame.VIDEORESIZE, pygame.WINDOWRESIZED):
                # Some backends send resize events without .size; fall back to current window size.
                new_size = getattr(event, "size", self.screen.get_size())
                self.handle_resize(new_size[0], new_size[1])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
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

    def handle_resize(self, new_width, new_height):
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        self.layout.update(new_width, new_height)
        
        # Update grid with new available space
        grid_rect = self.layout.get_grid_rect()
        if hasattr(self.grid, 'resize'):
            self.grid.resize(available_width=grid_rect.width, available_height=grid_rect.height)
        self.grid.calculate_offsets(start_x=grid_rect.x, start_y=grid_rect.y)
        self.left_panel_width = self.layout.panel_width

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
        self.tooltip.set(tooltip_text, mouse_pos)

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
        Draw the game elements on the screen with the redesigned UI.
        """
        self.screen.fill(BACKGROUND_COLOR)
        # Draw line chart
        self.draw_line_chart()
        # Draw grid
        self.grid.draw(self.screen)

        # --- Left Panel Redesign ---
        panel_rect = pygame.Rect(0, 0, self.left_panel_width, self.screen.get_height())
        pygame.draw.rect(self.screen, PANEL_BACKGROUND_COLOR, panel_rect)

        y_offset = 20
        x_padding = 15
        panel_content_width = self.left_panel_width - (x_padding * 2)

        # Title
        title_text = self.font_manager.get('2xl').render("GAME OF LIFE", True, TEXT_COLOR)
        self.screen.blit(title_text, (x_padding, y_offset))
        y_offset += title_text.get_height() + 10
        pygame.draw.line(self.screen, (45, 48, 58), (x_padding, y_offset), (self.left_panel_width - x_padding, y_offset), 1)
        y_offset += 20

        # Action Buttons
        y_offset += self.action_bar.draw(self.screen, x_padding, y_offset, panel_content_width)

        # --- Collapsible Sections ---
        
        # Statistics Section
        stats_section = self.settings_panel.sections['statistics']
        header_h = stats_section.draw_header(self.screen, x_padding, y_offset, panel_content_width)
        y_offset += header_h + 5
        
        if stats_section.expanded:
            y_offset += self.statistics_panel.draw(self.screen, x_padding, y_offset, panel_content_width)
            y_offset += 10

        # Settings Section
        settings_section = self.settings_panel.sections['settings']
        header_h = settings_section.draw_header(self.screen, x_padding, y_offset, panel_content_width)
        y_offset += header_h + 5

        if settings_section.expanded:
            settings_height = self.settings_panel.draw(self.screen, x=x_padding, y=y_offset, width=panel_content_width)
            y_offset += settings_height
        
        y_offset += 15

        # Lifeform Status Section
        lifeform_section = self.settings_panel.sections['lifeforms']
        header_h = lifeform_section.draw_header(self.screen, x_padding, y_offset, panel_content_width)
        y_offset += header_h + 5

        if lifeform_section.expanded:
            for i, lifeform in enumerate(self.lifeforms[:self.number_of_lifeforms]):
                color = lifeform.color_alive
                rule_str = f"B{'/'.join(map(str, lifeform.birth_rules))}/S{'/'.join(map(str, lifeform.survival_rules))}"
                alive_count = self.lifeform_alive_counts[lifeform.id][-1] if self.lifeform_alive_counts[lifeform.id] else 0

                pygame.draw.rect(self.screen, color, (x_padding + 10, y_offset + 4, 12, 12), border_radius=3)
                
                lf_text = self.font_manager.get('base').render(f"LF{lifeform.id}:", True, TEXT_COLOR)
                self.screen.blit(lf_text, (x_padding + 30, y_offset))
                
                count_text = self.font_manager.get('mono').render(f"{alive_count:,}", True, TEXT_COLOR)
                self.screen.blit(count_text, (x_padding + 80, y_offset))
                
                rule_text_surf = self.font_manager.get('sm').render(rule_str, True, (160, 163, 175))
                self.screen.blit(rule_text_surf, (x_padding + 150, y_offset + 2))
                
                y_offset += 28
            y_offset += 10

        # Draw tooltip
        self.tooltip.draw(self.screen)
        
        # Draw keyboard hints
        self.keyboard_hints.draw(self.screen)

    def draw_line_chart(self):
        """Draws an improved line chart with better visual hierarchy."""
        chart_rect = self.get_chart_rect()
        self.chart_rect = chart_rect
        
        # Draw background with subtle gradient effect
        pygame.draw.rect(self.screen, CHART_BACKGROUND, chart_rect, border_radius=8)
        
        # Draw subtle grid lines
        num_grid_lines = 5
        for i in range(1, num_grid_lines):
            y = chart_rect.y + (i * chart_rect.height // num_grid_lines)
            pygame.draw.line(self.screen, CHART_GRID_LINES, 
                            (chart_rect.x, y), (chart_rect.right, y), 1)
        
        # Draw border
        pygame.draw.rect(self.screen, CHART_AXIS_COLOR, chart_rect, 2, border_radius=8)
        
        # ... (existing plotting logic with updated colors)
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
                label = self.font_manager.get('sm').render(str(y_value), True, TEXT_COLOR)
                label_rect = label.get_rect()
                label_x = chart_rect.x - label_rect.width - 10  # Adjusted spacing
                self.screen.blit(label, (label_x, y_pos - label_rect.height / 2))
                # Draw tick marks
                pygame.draw.line(self.screen, TEXT_COLOR, (chart_rect.x - 5, y_pos), (chart_rect.x, y_pos))

            # Right y-axis for kills
            for i in range(y_axis_ticks + 1):
                y_value = int(i * kill_max / y_axis_ticks)
                y_pos = chart_rect.bottom - i * chart_rect.height / y_axis_ticks
                label = self.font_manager.get('sm').render(str(y_value), True, TEXT_COLOR)
                label_rect = label.get_rect()
                label_x = chart_rect.right + 5
                self.screen.blit(label, (label_x, y_pos - label_rect.height / 2))
                pygame.draw.line(self.screen, TEXT_COLOR, (chart_rect.right, y_pos), (chart_rect.right + 5, y_pos))
        
        # Move legend outside chart (below or to the side)
        self._draw_chart_legend(chart_rect)

    def _draw_chart_legend(self, chart_rect):
        """Draw legend below the chart instead of inside it."""
        legend_y = chart_rect.bottom + 8
        legend_x = chart_rect.x
        item_width = 100
        
        for i, lifeform in enumerate(self.lifeforms[:self.number_of_lifeforms]):
            x = legend_x + (i % 5) * item_width
            y = legend_y + (i // 5) * 20
            
            # Color swatch
            pygame.draw.rect(self.screen, lifeform.color_alive, 
                            pygame.Rect(x, y + 2, 12, 12), border_radius=2)
            
            # Label
            label = self.font_manager.get('xs').render(f"LF{lifeform.id}", True, TEXT_COLOR)
            self.screen.blit(label, (x + 16, y))

if __name__ == '__main__':
    game = GameOfLife()
    game.run()

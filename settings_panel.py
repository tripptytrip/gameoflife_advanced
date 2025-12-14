# settings_panel.py

import pygame
from settings import (
    TEXT_COLOR,
    PANEL_BACKGROUND_COLOR,
    FONT_NAME,
    FONT_SIZE,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    SCROLLBAR_COLOR,
    SCROLLBAR_HANDLE_COLOR,
)
from lifeform import Lifeform

class Slider:
    """
    Represents a slider UI element.
    """
    def __init__(self, label, min_val, max_val, current_val, x, y, width, height, font,
                 live_callback=None, release_callback=None):
        self.label = label
        self.min = min_val
        self.max = max_val
        self.value = current_val
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_radius = height // 2
        self.handle_x = self.get_handle_position()
        self.handle_y = y + height // 2
        self.dragging = False
        self.font = font
        # Callback to fire while dragging (live updates)
        self.live_callback = live_callback
        # Callback to fire when the user releases the handle (for heavy work)
        self.release_callback = release_callback

    def get_handle_position(self):
        """
        Calculate the x-position of the slider handle based on current value.
        """
        proportion = (self.value - self.min) / (self.max - self.min)
        return self.rect.x + int(proportion * self.rect.width)

    def handle_event(self, event):
        """
        Handle events related to the slider.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                distance = ((mouse_x - self.handle_x) ** 2 + (mouse_y - self.handle_y) ** 2) ** 0.5
                if distance <= self.handle_radius:
                    self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                if self.release_callback:
                    self.release_callback(self.value)
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = event.pos
                # Clamp handle position within the slider track
                self.handle_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
                # Update value based on handle position
                proportion = (self.handle_x - self.rect.x) / self.rect.width
                self.value = int(self.min + proportion * (self.max - self.min))
                if self.live_callback:
                    self.live_callback(self.value)

    def draw(self, surface):
        """
        Draw the slider on the given surface.
        """
        # Draw label above the slider
        label_surf = self.font.render(f"{self.label}", True, TEXT_COLOR)
        label_rect = label_surf.get_rect(midtop=(self.rect.centerx, self.rect.y - 20))
        surface.blit(label_surf, label_rect)

        # Draw current value below the slider
        value_surf = self.font.render(f"{self.value}", True, TEXT_COLOR)
        value_rect = value_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + self.rect.height + 5))
        surface.blit(value_surf, value_rect)

        # Draw slider track
        pygame.draw.rect(surface, SCROLLBAR_COLOR, self.rect)

        # Draw slider handle
        pygame.draw.circle(surface, BUTTON_COLOR, (self.handle_x, self.handle_y), self.handle_radius)
        pygame.draw.circle(surface, TEXT_COLOR, (self.handle_x, self.handle_y), self.handle_radius, 2)


class SettingsPanel:
    """
    Manages the settings panel for adjusting game variables with improved UI elements.
    """

    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.active_box = None
        self.setup_panel()

        # Scrollbar attributes
        self.scroll_y = 0
        self.scroll_speed = 20  # Pixels per scroll event
        self.is_dragging = False
        self.drag_start_y = 0
        self.scrollbar_rect = None
        self.handle_rect = None
        self.handle_height = 0

        # Initialize content and visible heights
        self.content_height = 0
        self.visible_height = 0

        # Track hovered button for tooltips
        self.hovered_button = None

    def setup_panel(self):
        """
        Initialize input values and labels for the settings panel.
        """
        self.sliders = {
            'Initial Alive Percentage': {
                'min': 0,
                'max': 100,
                'value': int(self.game.initial_alive_percentage * 100),
                'live_callback': self.update_initial_alive_percentage
            },
            'Simulation Speed (FPS)': {
                'min': 1,
                'max': 60,
                'value': self.game.fps,
                'live_callback': self.update_simulation_speed
            },
            'Number of Lifeforms': {
                'min': 1,
                'max': 10,
                'value': self.game.number_of_lifeforms,
                'release_callback': self.update_number_of_lifeforms
            },
            'Grid Width': {  # New slider for grid width
                'min': 10,
                'max': 400,
                'value': self.game.grid_width,
                'release_callback': self.update_grid_width
            },
            'Grid Height': {  # New slider for grid height
                'min': 10,
                'max': 200,
                'value': self.game.grid_height,
                'release_callback': self.update_grid_height
            },
            'Number of Generations': {  # For auto-run
                'min': 1,
                'max': 1000,
                'value': self.game.auto_run_generations,
                'release_callback': self.update_number_of_generations
            },
            'Number of Sessions': {  # For auto-run
                'min': 1,
                'max': 100,
                'value': 1,
                'release_callback': self.update_number_of_sessions
            }
        }

        self.selections = {
            'Grid Shape': {
                'options': ['triangle', 'square', 'hexagon'],
                'selected': self.game.shape,
                'rect': None
            }
        }

        self.buttons = {
            'Apply': None,                # Rect will be set during drawing
            'Randomise Lifeforms': None,  # Rect will be set during drawing
            'Auto Run': None              # Rect for Auto Run button
        }

        # Add inputs for lifeform rules
        self.lifeform_rules = {}
        for idx in range(1, 11):  # For up to 10 lifeforms
            self.lifeform_rules[idx] = {
                'birth_rules': ','.join(map(str, self.game.lifeforms[idx-1].birth_rules)) if idx <= len(self.game.lifeforms) else '',
                'survival_rules': ','.join(map(str, self.game.lifeforms[idx-1].survival_rules)) if idx <= len(self.game.lifeforms) else '',
                'birth_rect': None,
                'survival_rect': None
            }

    def update_initial_alive_percentage(self, value):
        """
        Update the initial alive percentage in the game.
        """
        self.game.initial_alive_percentage = value / 100.0

    def update_simulation_speed(self, value):
        """
        Update the simulation speed (FPS) in the game.
        """
        self.game.fps = value

    def update_number_of_lifeforms(self, value):
        """
        Update the number of lifeforms in the game.
        """
        self.game.number_of_lifeforms = value
        # Regenerate lifeforms to match the new count
        self.game.randomise_lifeforms()
        self.game.create_grid()

    def update_grid_width(self, value):
        """
        Update the grid width in the game.
        """
        self.game.grid_width = value
        self.game.create_grid()

    def update_grid_height(self, value):
        """
        Update the grid height in the game.
        """
        self.game.grid_height = value
        self.game.create_grid()

    def update_number_of_generations(self, value):
        """
        Update the number of generations for auto-run.
        """
        self.game.auto_run_generations = value
    
    def update_number_of_sessions(self, value):
        """
        Update the number of sessions for auto-run.
        """
        self.game.auto_run_sessions = value
    
    def handle_event(self, event):
        """
        Handle events specific to the settings panel, including sliders and buttons.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                pos = event.pos
                # Check if clicking on any selection box
                for key, data in self.selections.items():
                    if data['rect'] and data['rect'].collidepoint(pos):
                        # Cycle through options
                        current_index = data['options'].index(data['selected'])
                        next_index = (current_index + 1) % len(data['options'])
                        data['selected'] = data['options'][next_index]
                        # Update the game setting
                        self.game.shape = data['selected']
                        self.game.create_grid()
                # Check if any button is clicked
                for key, rect in self.buttons.items():
                    if rect and rect.collidepoint(pos):
                        if key == 'Apply':
                            self.apply_settings()
                        elif key == 'Randomise Lifeforms':
                            self.randomise_lifeforms()
                        elif key == 'Auto Run':
                            self.auto_run()
                        break
            elif event.button == 4:  # Scroll up
                self.scroll_y -= self.scroll_speed
                self.scroll_y = max(0, self.scroll_y)
                self.update_scrollbar()
            elif event.button == 5:  # Scroll down
                self.scroll_y += self.scroll_speed
                self.scroll_y = min(self.scroll_y, self.get_max_scroll())
                self.update_scrollbar()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging and self.handle_rect:
                mouse_y = event.pos[1]
                delta_y = mouse_y - self.drag_start_y
                self.drag_start_y = mouse_y
                max_scroll = self.get_max_scroll()
                self.scroll_y += delta_y * (self.content_height / self.scrollbar_rect.height)
                self.scroll_y = max(0, min(self.scroll_y, max_scroll))
                self.update_scrollbar()

        elif event.type == pygame.MOUSEWHEEL:
            # Handle scrolling with mouse wheel
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, self.get_max_scroll()))
            self.update_scrollbar()

        # Pass events to sliders
        for label, slider_info in self.sliders.items():
            slider_obj = getattr(self, f"slider_{label.replace(' ', '_')}", None)
            if slider_obj:
                slider_obj.handle_event(event)

    def apply_settings(self):
        """
        Apply the settings from the input fields to the game.
        """
        # Update lifeform rules from input fields
        for idx, rules in self.lifeform_rules.items():
            birth_input = rules['birth_rules']
            survival_input = rules['survival_rules']

            try:
                birth_rules = [int(num.strip()) for num in birth_input.split(',') if num.strip().isdigit()]
                survival_rules = [int(num.strip()) for num in survival_input.split(',') if num.strip().isdigit()]
            except ValueError:
                # If parsing fails, default to empty rules
                birth_rules = []
                survival_rules = []

            # Ensure unique lifeform IDs and existence
            if idx <= len(self.game.lifeforms):
                lifeform = self.game.lifeforms[idx - 1]
                lifeform.birth_rules = sorted(birth_rules)
                lifeform.survival_rules = sorted(survival_rules)
            else:
                # Create new lifeform if it doesn't exist
                lifeform = Lifeform(lifeform_id=idx, birth_rules=birth_rules, survival_rules=survival_rules)
                self.game.lifeforms.append(lifeform)

        # Apply settings to the game
        self.game.update_settings()

    def randomise_lifeforms(self):
        """
        Randomize lifeform profiles by generating new ones.
        """
        self.game.randomise_lifeforms()
        self.update_lifeform_rules()
        self.game.create_grid()

    def auto_run(self):
        """
        Trigger the auto-run mode in the game.
        """
        num_sessions = self.game.auto_run_sessions
        if num_sessions >= 1:
            self.game.start_auto_run(num_sessions)

    def update_lifeform_rules(self):
        """
        Update the lifeform rule inputs based on the game's lifeforms.
        """
        for idx, lifeform in enumerate(self.game.lifeforms, start=1):
            if idx > 10:
                break  # Limit to 10 lifeforms
            if idx in self.lifeform_rules:
                self.lifeform_rules[idx]['birth_rules'] = ','.join(map(str, lifeform.birth_rules))
                self.lifeform_rules[idx]['survival_rules'] = ','.join(map(str, lifeform.survival_rules))

    def get_max_scroll(self):
        """
        Calculate the maximum scroll offset based on content height and visible height.
        """
        return max(self.content_height - self.visible_height, 0)

    def update_scrollbar(self):
        """
        Update the scrollbar handle based on the current scroll position.
        """
        if self.content_height <= self.visible_height:
            # No need for scrollbar
            self.handle_rect = None
            return

        # Calculate handle size proportionally
        track_height = self.scrollbar_rect.height
        self.handle_height = max(int(track_height * self.visible_height / self.content_height), 20)

        # Calculate handle position proportionally
        max_scroll = self.get_max_scroll()
        proportion = self.scroll_y / max_scroll if max_scroll > 0 else 0
        handle_y = self.scrollbar_rect.y + int(proportion * (track_height - self.handle_height))
        self.handle_rect = pygame.Rect(
            self.scrollbar_rect.x,
            handle_y,
            self.scrollbar_rect.width,
            self.handle_height
        )

    def draw(self, surface, x, y, width):
        """
        Draw the settings panel within the left panel with improved UI.

        Args:
            surface (pygame.Surface): The surface to draw on.
            x (int): The x-coordinate to start drawing.
            y (int): The y-coordinate to start drawing.
            width (int): The width of the area to draw in.
        """
        # Define the visible area for the settings panel
        self.visible_height = surface.get_height() - y  # Assuming y is the top margin
        self.content_height = 0  # Will calculate as we draw

        # Define padding at the top
        padding_top = 20  # Adjust this value as needed

        # Define scrollbar properties
        scrollbar_width = 15
        self.scrollbar_rect = pygame.Rect(x + width - scrollbar_width, y, scrollbar_width, self.visible_height)

        # Enable clipping to the visible area
        surface.set_clip(pygame.Rect(x, y, width - scrollbar_width, self.visible_height))

        # Start drawing content with scroll offset and padding
        current_y = y - self.scroll_y + padding_top
        self.content_height = padding_top  # Initialize content_height with padding

        line_height = 25
        spacing = 10

        # Draw Sliders
        for label, slider_info in self.sliders.items():
            # Create Slider instance if not already created
            slider_obj = getattr(self, f"slider_{label.replace(' ', '_')}", None)
            if not slider_obj:
                slider_obj = Slider(
                    label=label,
                    min_val=slider_info['min'],
                    max_val=slider_info['max'],
                    current_val=slider_info['value'],
                    x=x + 10,
                    y=current_y,
                    width=width - 40,
                    height=15,
                    font=self.font,
                    live_callback=slider_info.get('live_callback'),
                    release_callback=slider_info.get('release_callback')
                )
                setattr(self, f"slider_{label.replace(' ', '_')}", slider_obj)

            slider_obj.rect.y = current_y  # Update y-position based on scroll
            slider_obj.handle_y = current_y + slider_obj.handle_radius
            slider_obj.handle_x = slider_obj.get_handle_position()
            slider_obj.draw(surface)
            current_y += 60
            self.content_height += 60

        # Draw Selection Fields
        for label, data in self.selections.items():
            # Draw label
            label_surf = self.font.render(label, True, TEXT_COLOR)
            surface.blit(label_surf, (x + 10, current_y))
            current_y += line_height

            # Draw selection box
            selection_rect = pygame.Rect(
                x + 10,
                current_y,
                width - 40,
                line_height + 10
            )
            data['rect'] = selection_rect  # Update the rect in data for event handling
            pygame.draw.rect(surface, BUTTON_COLOR, selection_rect)
            pygame.draw.rect(surface, TEXT_COLOR, selection_rect, 2)

            # Draw selected option
            selected_text = self.font.render(data['selected'], True, TEXT_COLOR)
            surface.blit(selected_text, (selection_rect.x + 10, selection_rect.y + 5))

            current_y += line_height + 20
            self.content_height += line_height + 20

        # Draw Buttons with hover effect
        button_height = 30
        button_spacing = 15
        for key in self.buttons.keys():
            rect = pygame.Rect(
                x + 10,
                current_y,
                width - 40,
                button_height
            )
            self.buttons[key] = rect  # Update rect based on current_y

            # Check hover state
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos):
                color = BUTTON_HOVER_COLOR
                self.hovered_button = key
            else:
                color = BUTTON_COLOR

            # Draw button
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, TEXT_COLOR, rect, 2, border_radius=5)

            # Draw button text
            button_text = self.font.render(key, True, TEXT_COLOR)
            text_rect = button_text.get_rect(center=rect.center)
            surface.blit(button_text, text_rect)

            current_y += button_height + button_spacing
            self.content_height += button_height + button_spacing

        # Draw Lifeform Rules Inputs
        current_y += 10  # Add some spacing before lifeform rules
        self.content_height += 10
        for lifeform_id, rules in self.lifeform_rules.items():
            # Lifeform Header
            lf_header = self.font.render(f'Lifeform {lifeform_id} Rules', True, TEXT_COLOR)
            surface.blit(lf_header, (x + 10, current_y))
            current_y += line_height + 5
            self.content_height += line_height + 5

            # Birth Rules Input
            label_text = self.font.render('  Birth Rules (e.g., 3,6)', True, TEXT_COLOR)
            surface.blit(label_text, (x + 10, current_y))
            current_y += line_height

            birth_rect = pygame.Rect(
                x + 20,
                current_y,
                width - 60,
                line_height + 10
            )
            rules['birth_rect'] = birth_rect

            # Draw birth rules input box
            pygame.draw.rect(surface, BUTTON_COLOR, birth_rect)
            pygame.draw.rect(surface, TEXT_COLOR, birth_rect, 2)

            # Render birth rules text
            birth_text = self.font.render(rules['birth_rules'], True, TEXT_COLOR)
            surface.blit(birth_text, (birth_rect.x + 10, birth_rect.y + 5))

            current_y += line_height + 20
            self.content_height += line_height + 20

            # Survival Rules Input
            label_text = self.font.render('  Survival Rules (e.g., 2,3)', True, TEXT_COLOR)
            surface.blit(label_text, (x + 10, current_y))
            current_y += line_height

            survival_rect = pygame.Rect(
                x + 20,
                current_y,
                width - 60,
                line_height + 10
            )
            rules['survival_rect'] = survival_rect

            # Draw survival rules input box
            pygame.draw.rect(surface, BUTTON_COLOR, survival_rect)
            pygame.draw.rect(surface, TEXT_COLOR, survival_rect, 2)

            # Render survival rules text
            survival_text = self.font.render(rules['survival_rules'], True, TEXT_COLOR)
            surface.blit(survival_text, (survival_rect.x + 10, survival_rect.y + 5))

            current_y += line_height + 20
            self.content_height += line_height + 20

        # Remove clipping
        surface.set_clip(None)

        # Calculate scrollbar handle
        self.update_scrollbar()

        # Draw scrollbar background
        pygame.draw.rect(surface, SCROLLBAR_COLOR, self.scrollbar_rect)
        # Draw scrollbar handle
        if self.handle_rect:
            pygame.draw.rect(surface, SCROLLBAR_HANDLE_COLOR, self.handle_rect)

    def update_lifeform_rules(self):
        """
        Update the lifeform rule inputs based on the game's lifeforms.
        """
        for idx, lifeform in enumerate(self.game.lifeforms, start=1):
            if idx > 10:
                break  # Limit to 10 lifeforms
            if idx in self.lifeform_rules:
                self.lifeform_rules[idx]['birth_rules'] = ','.join(map(str, lifeform.birth_rules))
                self.lifeform_rules[idx]['survival_rules'] = ','.join(map(str, lifeform.survival_rules))

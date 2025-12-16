import pygame
from settings import (
    TEXT_COLOR,
    PANEL_BACKGROUND_COLOR,
    FONT_NAME,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    BUTTON_TEXT_COLOR,
    BUTTON_BORDER_RADIUS,
    BUTTON_HEIGHT_SMALL,
    BUTTON_HEIGHT_LARGE,
    SCROLLBAR_COLOR,
    SCROLLBAR_HANDLE_COLOR,
    DEFAULT_TRIANGLE_MODE,
    ACCENT_PRIMARY,
    SCROLLBAR_TRACK,
)
from lifeform import Lifeform
from neighbor_utils import get_max_neighbors
from db_explorer import query_rows, get_schema, get_row_by_id, get_unique_values

class CollapsibleSection:
    """A collapsible UI section with header and content."""
    
    def __init__(self, title, font, icon=None, initially_expanded=True):
        self.title = title
        self.font = font
        self.icon = icon
        self.expanded = initially_expanded
        self.header_rect = None
        self.content_height = 0
        self.animation_progress = 1.0 if initially_expanded else 0.0
        
    def toggle(self):
        self.expanded = not self.expanded
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.header_rect and self.header_rect.collidepoint(event.pos):
                self.toggle()
                return True
        return False
    
    def draw_header(self, surface, x, y, width):
        """Draw the collapsible header with expand/collapse indicator."""
        header_height = 32
        self.header_rect = pygame.Rect(x, y, width, header_height)
        
        # Background
        pygame.draw.rect(surface, BUTTON_COLOR, self.header_rect, border_radius=6)
        
        # Hover effect
        if self.header_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, BUTTON_HOVER_COLOR, self.header_rect, border_radius=6)
        
        # Title
        title_surf = self.font.render(self.title, True, TEXT_COLOR)
        surface.blit(title_surf, (x + 12, y + (header_height - title_surf.get_height()) // 2))
        
        # Expand/collapse indicator
        indicator = "▼" if self.expanded else "▶"
        ind_surf = self.font.render(indicator, True, TEXT_COLOR)
        surface.blit(ind_surf, (x + width - 24, y + (header_height - ind_surf.get_height()) // 2))
        
        return header_height
    
    def get_visible_height(self):
        """Get current visible content height based on animation."""
        return int(self.content_height * self.animation_progress)

class Button:
    """Shared button with consistent styling and hover handling."""
    def __init__(self, x, y, width, height, text, font, fill=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.fill = fill or BUTTON_COLOR

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        hovered = self.is_hovered(pygame.mouse.get_pos())
        color = BUTTON_HOVER_COLOR if hovered else self.fill
        pygame.draw.rect(surface, color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 1, border_radius=BUTTON_BORDER_RADIUS)
        txt = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        surface.blit(txt, txt.get_rect(center=self.rect.center))
        return self.rect

class Dropdown:
    """A dropdown menu UI element."""
    ITEM_HEIGHT = 28
    MAX_HEIGHT = 200
    PADDING_Y = 4

    def __init__(self, options, font, commit_callback=None):
        self.options, self.font, self.commit_callback = options, font, commit_callback
        self.active, self.selected_option, self.rect, self.dropdown_rects = False, None, None, []
        self.scroll_y, self.scroll_speed = 0, 20

    def handle_event(self, event, parent_scroll_y=0):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect and self.rect.collidepoint(event.pos):
                self.active = not self.active
                self.scroll_y = 0
            elif self.active:
                for i, rect in enumerate(self.dropdown_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = self.options[i]
                        if self.commit_callback:
                            self.commit_callback(self.selected_option)
                        self.active = False
                        break
                else:
                    self.active = False
        elif self.active and event.type == pygame.MOUSEWHEEL:
            max_scroll = max(len(self.options) * self.ITEM_HEIGHT - self.MAX_HEIGHT, 0)
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, max_scroll))

    def draw(self, surface, rect):
        self.rect = rect
        pygame.draw.rect(surface, BUTTON_COLOR, rect, border_radius=3)
        pygame.draw.rect(surface, BUTTON_HOVER_COLOR if self.active else TEXT_COLOR, rect, 2, border_radius=3)
        surface.blit(self.font.render(self.selected_option or "Select a rule...", True, TEXT_COLOR), (rect.x + 5, rect.y + 5))

        if not self.active:
            return

        self.dropdown_rects = []
        list_height = min(len(self.options) * self.ITEM_HEIGHT, self.MAX_HEIGHT)
        list_rect = pygame.Rect(rect.x, rect.bottom + 2, rect.width, list_height)
        pygame.draw.rect(surface, PANEL_BACKGROUND_COLOR, list_rect, border_radius=4)
        pygame.draw.rect(surface, BUTTON_COLOR, list_rect, 2, border_radius=4)

        for i, option in enumerate(self.options):
            y_pos = list_rect.y + i * self.ITEM_HEIGHT - self.scroll_y
            if y_pos + self.ITEM_HEIGHT < list_rect.y or y_pos > list_rect.bottom:
                continue
            option_rect = pygame.Rect(rect.x, y_pos, rect.width, self.ITEM_HEIGHT)
            self.dropdown_rects.append(option_rect)
            color = BUTTON_HOVER_COLOR if option_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
            pygame.draw.rect(surface, color, option_rect, border_radius=3)
            surface.blit(self.font.render(option, True, TEXT_COLOR), (option_rect.x + 5, option_rect.y + self.PADDING_Y))

class TextInput:
    """Lightweight text input with placeholder support."""
    def __init__(self, text, font, width=140, placeholder="", commit_callback=None):
        self.text, self.font, self.width = text, font, width
        self.placeholder, self.commit_callback = placeholder, commit_callback
        self.active, self.rect = False, None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect and self.rect.collidepoint(event.pos)
            if not self.active and self.commit_callback:
                self.commit_callback()
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.commit_callback:
                    self.commit_callback()
                self.active = False
            elif event.unicode:
                self.text += event.unicode

    def draw(self, surface, rect):
        self.rect = rect
        pygame.draw.rect(surface, BUTTON_COLOR, rect, border_radius=4)
        pygame.draw.rect(surface, BUTTON_HOVER_COLOR if self.active else TEXT_COLOR, rect, 2, border_radius=4)
        display_text = self.text if self.text else self.placeholder
        color = TEXT_COLOR if self.text else BUTTON_HOVER_COLOR
        txt_surf = self.font.render(display_text, True, color)
        surface.blit(txt_surf, txt_surf.get_rect(midleft=(rect.x + 8, rect.centery)))

class NumericInput:
    """Simple numeric input box."""
    def __init__(self, value, min_val, max_val, font, commit_callback=None):
        self.value, self.text = value, str(value); self.min, self.max = min_val, max_val
        self.font, self.commit_callback = font, commit_callback
        self.active, self.rect = False, None
    def clamp(self, val): return max(self.min, min(self.max, val))
    def set_value(self, val, fire_callback=False):
        val = int(self.clamp(val)); self.value, self.text = val, str(val)
        if fire_callback and self.commit_callback: self.commit_callback(val)
    def commit(self):
        try: val = int(self.text) if self.text else self.value
        except ValueError: val = self.value
        val = self.clamp(val); changed = val != self.value; self.value, self.text = val, str(val)
        if changed and self.commit_callback: self.commit_callback(val)
        return changed
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect and self.rect.collidepoint(event.pos)
            if self.active is False and self.text != str(self.value): self.commit()
        if not self.active: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN: self.commit(); self.active = False
            elif event.unicode.isdigit(): self.text += event.unicode
    def draw(self, surface, rect):
        self.rect = rect; pygame.draw.rect(surface, BUTTON_COLOR, rect, border_radius=3)
        pygame.draw.rect(surface, BUTTON_HOVER_COLOR if self.active else TEXT_COLOR, rect, 2, border_radius=3)
        txt_surf = self.font.render(self.text or "0", True, TEXT_COLOR)
        surface.blit(txt_surf, txt_surf.get_rect(center=rect.center))

class Slider:
    """Improved slider with larger hit area and visual feedback."""
    
    TRACK_HEIGHT = 6
    HANDLE_RADIUS = 10
    ACTIVE_HANDLE_RADIUS = 12
    
    def __init__(self, label, min_val, max_val, current_val, font, 
                 live_callback=None, release_callback=None, format_fn=None):
        self.label = label
        self.min = min_val
        self.max = max_val
        self.value = current_val
        self.font = font
        self.live_callback = live_callback
        self.release_callback = release_callback
        self.format_fn = format_fn or (lambda v: str(v))
        
        self.rect = None
        self.dragging = False
        self.hovered = False
        
    def get_handle_x(self):
        if self.rect is None:
            return 0
        ratio = (self.value - self.min) / (self.max - self.min) if (self.max - self.min) != 0 else 0
        return self.rect.x + int(ratio * self.rect.width)
    
    def handle_event(self, event):
        if self.rect is None:
            return
            
        handle_x = self.get_handle_x()
        handle_y = self.rect.centery
        
        if event.type == pygame.MOUSEMOTION:
            # Check hover state
            dist = ((event.pos[0] - handle_x)**2 + (event.pos[1] - handle_y)**2)**0.5
            self.hovered = dist <= self.HANDLE_RADIUS * 1.5 or self.rect.collidepoint(event.pos)
            
            if self.dragging:
                # Update value during drag
                new_x = max(self.rect.x, min(event.pos[0], self.rect.right))
                ratio = (new_x - self.rect.x) / self.rect.width
                self.value = int(self.min + ratio * (self.max - self.min))
                if self.live_callback:
                    self.live_callback(self.value)
                    
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Start drag if clicking on handle or track
            if self.hovered or self.rect.collidepoint(event.pos):
                self.dragging = True
                # Jump to click position
                new_x = max(self.rect.x, min(event.pos[0], self.rect.right))
                ratio = (new_x - self.rect.x) / self.rect.width
                self.value = int(self.min + ratio * (self.max - self.min))
                if self.live_callback:
                    self.live_callback(self.value)
                    
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                if self.release_callback:
                    self.release_callback(self.value)
    
    def draw(self, surface, rect):
        self.rect = rect
        handle_x = self.get_handle_x()
        handle_y = rect.centery
        
        # Track background
        track_rect = pygame.Rect(
            rect.x, 
            rect.centery - self.TRACK_HEIGHT // 2,
            rect.width, 
            self.TRACK_HEIGHT
        )
        pygame.draw.rect(surface, SCROLLBAR_TRACK, track_rect, border_radius=3)
        
        # Filled portion
        filled_rect = pygame.Rect(
            rect.x,
            rect.centery - self.TRACK_HEIGHT // 2,
            handle_x - rect.x,
            self.TRACK_HEIGHT
        )
        pygame.draw.rect(surface, ACCENT_PRIMARY, filled_rect, border_radius=3)
        
        # Handle
        radius = self.ACTIVE_HANDLE_RADIUS if (self.dragging or self.hovered) else self.HANDLE_RADIUS
        
        # Handle shadow
        pygame.draw.circle(surface, (0, 0, 0, 50), (handle_x + 1, handle_y + 2), radius)
        
        # Handle fill
        handle_color = (130, 133, 255) if self.dragging else ACCENT_PRIMARY
        pygame.draw.circle(surface, handle_color, (handle_x, handle_y), radius)
        
        # Handle border
        pygame.draw.circle(surface, TEXT_COLOR, (handle_x, handle_y), radius, 2)
        
        # Value tooltip on drag
        if self.dragging:
            value_text = self.format_fn(self.value)
            value_surf = self.font.render(value_text, True, TEXT_COLOR)
            tooltip_rect = value_surf.get_rect(midbottom=(handle_x, handle_y - radius - 4))
            
            # Tooltip background
            bg_rect = tooltip_rect.inflate(12, 6)
            pygame.draw.rect(surface, (50, 52, 65), bg_rect, border_radius=4)
            surface.blit(value_surf, tooltip_rect)

class SettingsPanel:
    def __init__(self, game):
        self.game = game
        self.font = game.font_manager.get('base')
        self.active_view = "settings"
        self.padding = 12
        self.section_gap = 18
        self.control_gap = 8
        self.slider_track_height = 16

        self.sections = {
            "statistics": CollapsibleSection("STATISTICS", self.game.font_manager.get('lg')),
            "settings": CollapsibleSection("SETTINGS", self.game.font_manager.get('lg')),
            "lifeforms": CollapsibleSection("LIFEFORM STATUS", self.game.font_manager.get('lg')),
        }

        self.db_path, self.db_table = "species.db", "life_records"
        self.db_schema, self.db_columns, self.db_rows, self.db_total, self.db_page = {}, [], [], 0, 0
        self.db_page_size, self.db_sort_by, self.db_sort_dir = 50, "id", "DESC"
        self.db_filters, self.db_selected_row_id, self.db_loading = {}, None, False
        self.db_row_rects, self.db_result_rects = [], []
        self.db_scroll_y, self.db_scroll_speed = 0, 20
        self.db_content_height, self.db_visible_height = 0, 0
        self.db_scrollbar_rect, self.db_handle_rect, self.db_handle_height = None, None, 0
        self.db_filters_state = {"shape": None, "neighborhood": None, "signature": ""}
        self.db_filter_options = {"shape": [], "neighborhood": []}
        self.db_shape_dropdown = Dropdown([], self.font, commit_callback=self.apply_db_filters)
        self.db_neighborhood_dropdown = Dropdown([], self.font, commit_callback=self.apply_db_filters)
        self.db_rule_input = TextInput("", self.font, width=180, placeholder="B3/S23", commit_callback=self.apply_db_filters)
        self.available_columns = set()
        self.scroll_y, self.scroll_speed = 0, 20
        self.is_dragging, self.drag_start_y = False, 0
        self.content_height, self.visible_height, self.hovered_button = 0, 0, None
        self.buttons = {}
        self.setup_panel()

    def setup_panel(self):
        self.slider_configs = {
            'Initial Alive Percentage': { 'min_val': 0, 'max_val': 100, 'current_val': int(self.game.initial_alive_percentage * 100), 'live_callback': self.update_initial_alive_percentage },
            'Simulation Speed (FPS)': { 'min_val': 1, 'max_val': 60, 'current_val': self.game.fps, 'live_callback': self.update_simulation_speed },
            'Number of Lifeforms': { 'min_val': 1, 'max_val': 10, 'current_val': self.game.number_of_lifeforms, 'release_callback': self.update_number_of_lifeforms },
            'Grid Width': { 'min_val': 10, 'max_val': 400, 'current_val': self.game.grid_width, 'release_callback': self.update_grid_width },
            'Grid Height': { 'min_val': 10, 'max_val': 200, 'current_val': self.game.grid_height, 'release_callback': self.update_grid_height },
            'Number of Generations': { 'min_val': 1, 'max_val': 1000, 'current_val': self.game.auto_run_generations, 'release_callback': self.update_number_of_generations },
            'Number of Sessions': { 'min_val': 1, 'max_val': 100, 'current_val': 1, 'release_callback': self.update_number_of_sessions }
        }
        self.slider_objects = {label: Slider(label=label, font=self.font, **cfg) for label, cfg in self.slider_configs.items()}
        self.numeric_configs = {
            'Initial Alive Percentage': {'min': 0, 'max': 100, 'quick': [-5, -1, 1, 5]}, 'Grid Width': {'min': 10, 'max': 400, 'quick': [-10, 10]},
            'Grid Height': {'min': 10, 'max': 200, 'quick': [-10, 10]}, 'Number of Generations': {'min': 1, 'max': 1000, 'quick': ['half', 'double']},
            'Number of Sessions': {'min': 1, 'max': 100, 'quick': [-1, 1]}, 'Simulation Speed (FPS)': {'min': 1, 'max': 60, 'quick': [-5, -1, 1, 5]},
            'Number of Lifeforms': {'min': 1, 'max': 10, 'quick': [-1, 1]}
        }
        self.numeric_controls = {label: {'input': NumericInput(cfg['current_val'], self.numeric_configs[label]['min'], self.numeric_configs[label]['max'], self.font, lambda v, l=label: self.apply_numeric_value(l, v)), 'buttons':[]} for label, cfg in self.slider_configs.items() if label in self.numeric_configs}
        self._attach_slider_handlers()
        self.selections = {
            'Grid Shape': { 'options': ['triangle', 'square', 'hexagon'], 'selected': self.game.shape, 'rect': None },
            'Triangle Neighborhood': { 'options': ['edge', 'edge+vertex'], 'selected': self.game.triangle_mode, 'rect': None }
        }
        self.lifeform_rules = {idx: {'birth_rules': '', 'survival_rules': '', 'birth_rect': None, 'survival_rect': None} for idx in range(1, 11)}
        self.update_lifeform_rules()

    def update_initial_alive_percentage(self, value): self.game.initial_alive_percentage = value / 100.0
    def update_simulation_speed(self, value): self.game.fps = value
    def update_number_of_lifeforms(self, value): self.game.number_of_lifeforms = value; self.game.randomise_lifeforms(); self.game.create_grid()
    def update_grid_width(self, value): self.game.grid_width = value; self.game.create_grid()
    def update_grid_height(self, value): self.game.grid_height = value; self.game.create_grid()
    def update_number_of_generations(self, value): self.game.auto_run_generations = value
    def update_number_of_sessions(self, value): self.game.auto_run_sessions = value

    def _attach_slider_handlers(self):
        """Keep sliders, numeric inputs, and callbacks in sync."""
        for label, slider in self.slider_objects.items():
            original_live = slider.live_callback
            slider.live_callback = self._make_live_slider_callback(label, original_live)
            slider.release_callback = lambda value, l=label: self.apply_numeric_value(l, value)

    def _make_live_slider_callback(self, label, downstream):
        def wrapped(value):
            if label in self.numeric_controls:
                self.numeric_controls[label]['input'].set_value(value)
            if downstream:
                downstream(value)
        return wrapped

    def _reset_buttons(self):
        """Clear button registry for current view to avoid stale hit boxes."""
        self.buttons = {}

    def _switch_view(self, view_name):
        if view_name == self.active_view:
            return
        self.active_view = view_name
        self.scroll_y = 0
        self.db_scroll_y = 0
        self._reset_buttons()
        # Close transient inputs/dropdowns when changing views
        self.db_shape_dropdown.active = False
        self.db_neighborhood_dropdown.active = False
        self.db_rule_input.active = False
        for control in self.numeric_controls.values():
            control['input'].active = False
    
    def on_slider_change(self, label, value):
        if label in self.numeric_controls: self.numeric_controls[label]['input'].set_value(value)
        self.slider_configs[label]['live_callback'](value)

    def apply_numeric_value(self, label, value):
        cfg = self.numeric_configs.get(label, {'min': value, 'max': value}); value = max(cfg['min'], min(cfg['max'], value))
        if label in self.slider_objects: self.slider_objects[label].value = value; self.slider_objects[label].handle_x = self.slider_objects[label].get_handle_position()
        if label in self.numeric_controls: self.numeric_controls[label]['input'].set_value(value)
        slider_info = self.slider_configs.get(label, {})
        if slider_info.get('live_callback'): slider_info['live_callback'](value)
        if slider_info.get('release_callback'): slider_info['release_callback'](value)
    
    def apply_quick_action(self, label, action):
        control = self.numeric_controls.get(label)
        if not control:
            return
        current = control['input'].value
        cfg = self.numeric_configs.get(label, {})
        if isinstance(action, (int, float)):
            new_val = current + action
        elif action == 'half':
            new_val = max(1, current // 2)
        elif action == 'double':
            new_val = current * 2
        else:
            return
        self.apply_numeric_value(label, new_val)
    
    def handle_event(self, event):
        if self.active_view == "settings":
            self._handle_settings_event(event)
        else:
            self._handle_db_event(event)

    def _handle_settings_event(self, event):
        for control in self.numeric_controls.values():
            control['input'].handle_event(event)
        for slider in self.slider_objects.values():
            slider.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # Quick increment/decrement buttons
            for label, control in self.numeric_controls.items():
                for btn, action in control['buttons']:
                    if btn.rect and btn.rect.collidepoint(pos):
                        self.apply_quick_action(label, action)
                        return

            for key, btn in self.buttons.items():
                if not btn or not btn.rect.collidepoint(pos):
                    continue
                if key == 'DB Explorer':
                    self._switch_view('db_explorer')
                    self.refresh_db_view()
                    return
                if key == 'Apply':
                    self.apply_settings()
                elif key == 'Randomise Lifeforms':
                    self.randomise_lifeforms()
                elif key == 'Auto Run':
                    self.auto_run()

            # Toggle simple selections
            for data in self.selections.values():
                if data['rect'] and data['rect'].collidepoint(pos):
                    idx = (data['options'].index(data['selected']) + 1) % len(data['options'])
                    data['selected'] = data['options'][idx]
                    self.game.shape = self.selections['Grid Shape']['selected']
                    self.game.triangle_mode = self.selections['Triangle Neighborhood']['selected']
                    self.apply_settings()
                    self.game.create_grid()
                    return

    def _handle_db_event(self, event):
        self.db_shape_dropdown.handle_event(event)
        self.db_neighborhood_dropdown.handle_event(event)
        self.db_rule_input.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for key, btn in self.buttons.items():
                if not btn or not btn.rect.collidepoint(pos):
                    continue
                if key == 'Back to Settings':
                    self._switch_view('settings')
                    return
                if key == 'Clear Filter':
                    self.clear_db_filter()
                    return
                if key == 'Apply Filters':
                    self.apply_db_filters()
                    return
                if key == 'Load into Lifeform 1':
                    self.load_selected_rules()
                    return
                if key.startswith('Load-'):
                    try:
                        self.db_selected_row_id = int(key.split('-', 1)[1])
                    except ValueError:
                        self.db_selected_row_id = None
                    self.load_selected_rules()
                    return

            for row_rect, row_id in self.db_row_rects:
                if row_rect.collidepoint(pos):
                    self.db_selected_row_id = row_id
                    self.load_selected_rules()
                    return

        elif event.type == pygame.MOUSEWHEEL:
            if not (self.db_shape_dropdown.active or self.db_neighborhood_dropdown.active):
                max_scroll = max(self.db_content_height - self.db_visible_height, 0)
                self.db_scroll_y -= event.y * self.db_scroll_speed
                self.db_scroll_y = max(0, min(self.db_scroll_y, max_scroll))

    def apply_settings(self): self.game.create_grid()
    def update_lifeform_rules(self):
        for idx, lifeform in enumerate(self.game.lifeforms, start=1):
            if idx > 10: break
            if idx in self.lifeform_rules:
                self.lifeform_rules[idx]['birth_rules'] = ','.join(map(str, lifeform.birth_rules))
                self.lifeform_rules[idx]['survival_rules'] = ','.join(map(str, lifeform.survival_rules))
    def randomise_lifeforms(self): self.game.randomise_lifeforms(); self.update_lifeform_rules(); self.game.create_grid()
    def auto_run(self): 
        if hasattr(self, 'game') and self.game.auto_run_sessions >= 1: self.game.start_auto_run(self.game.auto_run_sessions)
    def apply_db_filters(self, *_):
        shape = self.db_shape_dropdown.selected_option
        neighborhood = self.db_neighborhood_dropdown.selected_option
        self.db_filters_state["shape"] = None if shape in (None, "Any") else shape
        self.db_filters_state["neighborhood"] = None if neighborhood in (None, "Any") else neighborhood
        self.db_filters_state["signature"] = (self.db_rule_input.text or "").strip()
        self.db_page = 0; self.db_scroll_y = 0; self.refresh_db_view()
    def clear_db_filter(self):
        self.db_shape_dropdown.selected_option = "Any" if self.db_filter_options["shape"] else None
        self.db_neighborhood_dropdown.selected_option = "Any" if self.db_filter_options["neighborhood"] else None
        self.db_rule_input.text = ""
        self.db_filters_state = {"shape": None, "neighborhood": None, "signature": ""}
        self.db_page = 0; self.db_scroll_y = 0; self.refresh_db_view()
    def load_selected_rules(self):
        if self.db_selected_row_id is None: return
        row = get_row_by_id(self.db_path, self.db_table, self.db_selected_row_id)
        if not row: return
        self.game.shape = row['shape']
        self.game.apply_ruleset_to_lifeform(0, row['lifeform_birth_rules'], row['lifeform_survival_rules'])
        self._switch_view("settings")
    def refresh_db_view(self):
        if not self.db_schema:
            self.db_schema = get_schema(self.db_path) or {}
        self.available_columns = set(self.db_schema.get(self.db_table, []))
        self._load_filter_options()
        filter_payload = self._build_db_filter_payload()
        offset = self.db_page * self.db_page_size
        self.db_rows, self.db_total, self.db_columns = query_rows(self.db_path, self.db_table, filter_payload, self.db_sort_by, self.db_sort_dir, self.db_page_size, offset)
        self.db_content_height = len(self.db_rows) * 72
        self.db_scroll_y = min(self.db_scroll_y, max(self.db_content_height - self.db_visible_height, 0))

    def _load_filter_options(self):
        if "shape" in self.available_columns:
            shapes = get_unique_values(self.db_path, self.db_table, "shape")
        else:
            shapes = []
        self.db_filter_options["shape"] = shapes
        self.db_shape_dropdown.options = ["Any"] + shapes if shapes else ["Any"]

        if "neighborhood" in self.available_columns:
            neighborhoods = get_unique_values(self.db_path, self.db_table, "neighborhood")
        else:
            neighborhoods = []
        self.db_filter_options["neighborhood"] = neighborhoods
        if neighborhoods:
            self.db_neighborhood_dropdown.options = ["Any"] + neighborhoods
            if self.db_neighborhood_dropdown.selected_option not in self.db_neighborhood_dropdown.options:
                self.db_neighborhood_dropdown.selected_option = "Any"
        else:
            self.db_neighborhood_dropdown.options = []
            self.db_filters_state["neighborhood"] = None

        if self.db_shape_dropdown.selected_option is None:
            self.db_shape_dropdown.selected_option = "Any"

    def _build_db_filter_payload(self):
        filters = {}
        shape = self.db_filters_state.get("shape")
        neighborhood = self.db_filters_state.get("neighborhood")
        signature = (self.db_filters_state.get("signature") or "").strip()
        if shape:
            filters["shape"] = {"eq": shape}
        if neighborhood and "neighborhood" in self.available_columns:
            filters["neighborhood"] = {"eq": neighborhood}
        parsed = self._parse_rule_signature(signature)
        if parsed:
            filters["rules"] = parsed
        elif signature:
            filters["search"] = {"contains": signature}
        return filters

    def _parse_rule_signature(self, text):
        if not text:
            return None
        normalized = text.strip().upper().replace(" ", "")
        if "/" in normalized:
            try:
                birth_part, surv_part = normalized.split("/", 1)
                birth = birth_part.replace("B", "")
                surv = surv_part.replace("S", "")
                if birth.isdigit() and surv.isdigit():
                    return {"birth": birth, "survival": surv}
            except ValueError:
                return None
        return None

    def draw(self, surface, x, y, width):
        self._reset_buttons()
        self.hovered_button = None
        if self.active_view == "db_explorer":
            return self._draw_db_explorer(surface, x, y, width)
        else:
            return self._draw_settings(surface, x, y, width)

    def _draw_db_explorer(self, surface, x, y, width):
        padding = 10
        current_y = y + padding
        self.db_row_rects = []

        # Nav
        back_btn = Button(x + padding, current_y, width - 2 * padding, BUTTON_HEIGHT_LARGE, "Back to Settings", self.font)
        back_btn.draw(surface); self.buttons['Back to Settings'] = back_btn
        if back_btn.is_hovered(pygame.mouse.get_pos()):
            self.hovered_button = "Back to Settings"
        current_y += 42

        # Filter panel
        panel_height = 130
        panel_rect = pygame.Rect(x + padding, current_y, width - 2 * padding, panel_height)
        pygame.draw.rect(surface, PANEL_BACKGROUND_COLOR, panel_rect, border_radius=8)
        pygame.draw.rect(surface, BUTTON_COLOR, panel_rect, 1, border_radius=8)
        title_surf = self.font.render("Search & Filter", True, TEXT_COLOR)
        surface.blit(title_surf, (panel_rect.x + 12, panel_rect.y + 8))

        row_y = panel_rect.y + 32
        col_width = (panel_rect.width - 3 * padding) // 2

        shape_label = self.font.render("Grid Shape", True, TEXT_COLOR); surface.blit(shape_label, (panel_rect.x + 12, row_y))
        shape_rect = pygame.Rect(panel_rect.x + 12, row_y + 16, col_width, 30)
        self.db_shape_dropdown.draw(surface, shape_rect)

        neigh_label = self.font.render("Neighborhood", True, TEXT_COLOR)
        surface.blit(neigh_label, (panel_rect.x + col_width + padding + 12, row_y))
        neigh_rect = pygame.Rect(panel_rect.x + col_width + padding + 12, row_y + 16, col_width, 30)
        if self.db_neighborhood_dropdown.options:
            self.db_neighborhood_dropdown.draw(surface, neigh_rect)
        else:
            pygame.draw.rect(surface, BUTTON_COLOR, neigh_rect, border_radius=4)
            pygame.draw.rect(surface, TEXT_COLOR, neigh_rect, 2, border_radius=4)
            surface.blit(self.font.render("Not in DB", True, TEXT_COLOR), (neigh_rect.x + 8, neigh_rect.y + 6))

        # Rule signature input
        rule_label = self.font.render("Rule signature (B3/S23)", True, TEXT_COLOR)
        surface.blit(rule_label, (panel_rect.x + 12, row_y + 56))
        rule_rect = pygame.Rect(panel_rect.x + 12, row_y + 72, col_width, 30)
        self.db_rule_input.draw(surface, rule_rect)

        # Filter buttons
        btn_width = (panel_rect.width - 3 * padding) // 2
        apply_btn = Button(panel_rect.x + padding + 12, row_y + 72, btn_width, BUTTON_HEIGHT_SMALL, "Apply Filters", self.font, fill=BUTTON_HOVER_COLOR)
        clear_btn = Button(apply_btn.rect.right + padding, row_y + 72, btn_width, BUTTON_HEIGHT_SMALL, "Clear", self.font)
        apply_btn.draw(surface); clear_btn.draw(surface)
        self.buttons['Apply Filters'], self.buttons['Clear Filter'] = apply_btn, clear_btn
        if apply_btn.is_hovered(pygame.mouse.get_pos()):
            self.hovered_button = "Apply Filters"
        elif clear_btn.is_hovered(pygame.mouse.get_pos()):
            self.hovered_button = "Clear Filter"

        current_y = panel_rect.bottom + padding

        # Results list
        list_top = current_y
        list_height = max(surface.get_height() - list_top - 50, 60)
        self.db_visible_height = max(list_height, 0)
        list_rect = pygame.Rect(x + padding, list_top, width - 2 * padding - 12, list_height)
        surface.blit(self.font.render(f"Results ({self.db_total})", True, TEXT_COLOR), (list_rect.x, list_rect.y - 20))

        card_height = 72
        self.db_content_height = len(self.db_rows) * card_height
        self.db_scrollbar_rect = pygame.Rect(list_rect.right + 4, list_rect.y, 8, list_rect.height)
        surface.set_clip(list_rect)

        y_pos = list_rect.y - self.db_scroll_y
        self.db_row_rects = []
        for row in self.db_rows:
            card_rect = pygame.Rect(list_rect.x, y_pos, list_rect.width, card_height - 8)
            if card_rect.bottom < list_rect.y or card_rect.top > list_rect.bottom:
                y_pos += card_height
                continue
            self.db_row_rects.append((card_rect, row['id']))
            is_selected = row['id'] == self.db_selected_row_id
            bg_color = BUTTON_HOVER_COLOR if card_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
            if is_selected: bg_color = SCROLLBAR_HANDLE_COLOR
            pygame.draw.rect(surface, bg_color, card_rect, border_radius=6)
            pygame.draw.rect(surface, TEXT_COLOR, card_rect, 1, border_radius=6)

            rule_text = f"Rule #{row['id']} • B{row['lifeform_birth_rules']}/S{row['lifeform_survival_rules']}"
            shape_text = f"Shape: {row.get('shape', 'n/a')}"
            meta_text = f"Alive: {row.get('alive_count', '-')}, Static: {row.get('static_count', '-')}"
            surface.blit(self.font.render(rule_text, True, TEXT_COLOR), (card_rect.x + 10, card_rect.y + 8))
            surface.blit(self.font.render(shape_text, True, TEXT_COLOR), (card_rect.x + 10, card_rect.y + 28))
            surface.blit(self.font.render(meta_text, True, TEXT_COLOR), (card_rect.x + 10, card_rect.y + 46))

            load_btn = Button(card_rect.right - 90, card_rect.y + 18, 80, BUTTON_HEIGHT_SMALL, "Load", self.font, fill=PANEL_BACKGROUND_COLOR)
            load_btn.draw(surface); self.buttons[f'Load-{row["id"]}'] = load_btn
            if load_btn.is_hovered(pygame.mouse.get_pos()):
                self.hovered_button = "Load rules"

            y_pos += card_height

        surface.set_clip(None)
        self.update_db_scrollbar()
        if self.db_scrollbar_rect and self.db_handle_rect:
            pygame.draw.rect(surface, SCROLLBAR_COLOR, self.db_scrollbar_rect, border_radius=4)
            pygame.draw.rect(surface, SCROLLBAR_HANDLE_COLOR, self.db_handle_rect, border_radius=4)

        if self.db_selected_row_id is not None:
            load_btn = Button(x + padding, surface.get_height() - 36, width - 2 * padding, BUTTON_HEIGHT_LARGE, "Load into Lifeform 1", self.font)
            load_btn.draw(surface); self.buttons['Load into Lifeform 1'] = load_btn
            if load_btn.is_hovered(pygame.mouse.get_pos()):
                self.hovered_button = "Load into Lifeform 1"
        return_height = surface.get_height() - y
        return return_height

    def _draw_slider_row(self, surface, origin_x, origin_y, layout_y, usable_width, label, slider):
        """Lay out one slider + numeric + quick buttons row."""
        label_surf = self.font.render(label, True, TEXT_COLOR)
        label_y = origin_y + layout_y
        surface.blit(label_surf, (origin_x, label_y))
        label_height = label_surf.get_height()

        quick_actions = self.numeric_configs.get(label, {}).get('quick', [])
        btn_w, btn_h = 32, BUTTON_HEIGHT_SMALL
        quick_total_width = len(quick_actions) * (btn_w + 4) - 4 if quick_actions else 0
        numeric_w = 70

        gap = self.control_gap
        quick_block = quick_total_width + (gap if quick_total_width else 0)
        slider_width = max(80, usable_width - numeric_w - quick_block - gap)

        slider_y = label_y + label_height + 6
        slider_rect = pygame.Rect(origin_x, slider_y, slider_width, self.slider_track_height)
        slider.draw(surface, slider_rect)

        btn_y = slider_y - 1
        btn_x = slider_rect.right + gap
        self.numeric_controls[label]['buttons'] = []
        for action in quick_actions:
            text = f"{action}" if isinstance(action, (int, float)) else ("1/2" if action == "half" else "x2")
            btn = Button(btn_x, btn_y, btn_w, btn_h, text, self.font)
            btn.draw(surface)
            self.numeric_controls[label]['buttons'].append((btn, action))
            btn_x += btn_w + 4

        num_rect = pygame.Rect(origin_x + usable_width - numeric_w, btn_y, numeric_w, btn_h)
        self.numeric_controls[label]['input'].draw(surface, num_rect)

        row_bottom = max(slider_rect.bottom, num_rect.bottom, btn_y + btn_h)
        return layout_y + (row_bottom - label_y) + self.section_gap

    def _draw_settings(self, surface, x, y, width):
        padding = self.padding
        usable_width = width

        layout_y = 0
        for label, slider in self.slider_objects.items():
            layout_y = self._draw_slider_row(surface, x, y, layout_y, usable_width, label, slider)

        layout_y += self.section_gap // 2
        line_height = self.font.get_linesize()
        for label, data in self.selections.items():
            label_surf = self.font.render(label, True, TEXT_COLOR)
            label_y = y + layout_y
            surface.blit(label_surf, (x + padding, label_y))
            layout_y += line_height + 4
            selection_rect = pygame.Rect(x + padding, y + layout_y, usable_width, line_height + 10)
            data['rect'] = selection_rect
            pygame.draw.rect(surface, BUTTON_COLOR, selection_rect, border_radius=BUTTON_BORDER_RADIUS)
            pygame.draw.rect(surface, TEXT_COLOR, selection_rect, 2, border_radius=BUTTON_BORDER_RADIUS)
            surface.blit(self.font.render(data['selected'], True, TEXT_COLOR), (selection_rect.x + 10, selection_rect.y + 5))
            layout_y += line_height + self.section_gap // 2

        actions = ['Apply', 'Randomise Lifeforms', 'Auto Run', 'DB Explorer']
        for key in actions:
            btn_rect_y = y + layout_y
            btn = Button(x + padding, btn_rect_y, usable_width, BUTTON_HEIGHT_LARGE, key, self.font)
            btn.draw(surface)
            self.buttons[key] = btn
            if btn.is_hovered(pygame.mouse.get_pos()):
                self.hovered_button = key
            layout_y += BUTTON_HEIGHT_LARGE + self.control_gap

        layout_y += self.section_gap // 2
        for lifeform_id, rules in self.lifeform_rules.items():
            if lifeform_id > self.game.number_of_lifeforms:
                continue
            max_n = get_max_neighbors(self.game.shape, getattr(self.game, "triangle_mode", "edge+vertex"))
            lf_label = self.font.render(f'Lifeform {lifeform_id} Rules (0-{max_n})', True, TEXT_COLOR)
            label_y = y + layout_y
            surface.blit(lf_label, (x + padding, label_y))
            layout_y += line_height + 4

            birth_label = self.font.render(f'  Birth Rules (0-{max_n})', True, TEXT_COLOR)
            surface.blit(birth_label, (x + padding, y + layout_y))
            layout_y += line_height
            birth_rect = pygame.Rect(x + padding + 10, y + layout_y, usable_width - 20, line_height + 10)
            rules['birth_rect'] = birth_rect
            pygame.draw.rect(surface, BUTTON_COLOR, birth_rect)
            pygame.draw.rect(surface, TEXT_COLOR, birth_rect, 2)
            surface.blit(self.font.render(rules['birth_rules'], True, TEXT_COLOR), (birth_rect.x + 10, birth_rect.y + 5))
            layout_y += line_height + 12

            surv_label = self.font.render(f'  Survival Rules (0-{max_n})', True, TEXT_COLOR)
            surface.blit(surv_label, (x + padding, y + layout_y))
            layout_y += line_height
            survival_rect = pygame.Rect(x + padding + 10, y + layout_y, usable_width - 20, line_height + 10)
            rules['survival_rect'] = survival_rect
            pygame.draw.rect(surface, BUTTON_COLOR, survival_rect)
            pygame.draw.rect(surface, TEXT_COLOR, survival_rect, 2)
            surface.blit(self.font.render(rules['survival_rules'], True, TEXT_COLOR), (survival_rect.x + 10, survival_rect.y + 5))
            layout_y += line_height + self.section_gap

        self.content_height = layout_y + padding
        
        return self.content_height
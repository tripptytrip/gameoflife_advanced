# settings.py

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 30  # Default FPS

# Grid settings
DEFAULT_SHAPE = 'triangle'  # Options: 'triangle', 'square', 'hexagon'
DEFAULT_TRIANGLE_MODE = 'edge+vertex'  # Options: 'edge', 'edge+vertex'

# Cell settings
CELL_SIZE_TRIANGLE = 8  # Size for triangular cells
CELL_SIZE_SQUARE = 4     # Size for square cells
CELL_SIZE_HEXAGON = 3     # Size for hexagonal cells

# Game rules (default rules)
DEFAULT_BIRTH_RULES = [5, 6]        # Adjusted as needed for triangle grid
DEFAULT_SURVIVAL_RULES = [4, 5, 6]  # Adjusted as needed for triangle grid

# Colors (RGB tuples)
BACKGROUND_COLOR = (25, 25, 30)
LIVE_CELL_COLOR = (0, 200, 150)
DEAD_CELL_COLOR = (45, 45, 50)
GRID_LINE_COLOR = (60, 60, 65)
TEXT_COLOR = (240, 240, 240)
PANEL_BACKGROUND_COLOR = (35, 35, 40)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
SCROLLBAR_COLOR = (80, 80, 85)
SCROLLBAR_HANDLE_COLOR = (120, 120, 125)

# Fonts
FONT_NAME = 'Arial'
FONT_SIZE = 12

# Default initial alive percentage
DEFAULT_INITIAL_ALIVE_PERCENTAGE = 50  # Percentage (0 to 100)

# Lifeform Colors (RGB tuples)
LIFEFORM_COLORS_ALIVE = [
    (220, 100, 100),  # Soft Red
    (100, 220, 100),  # Soft Green
    (150, 75, 75),    # Soft Brown
    (230, 230, 100),  # Muted Yellow
    (245, 180, 110),  # Soft Orange
    (150, 100, 180),  # Lavender
    (120, 200, 200),  # Soft Cyan
    (255, 182, 193),  # Light Pink
    (180, 180, 180),  # Light Gray
    (100, 140, 180),  # Muted Blue
]

# Define colors for static cells
LIFEFORM_COLORS_STATIC = [
    (245, 245, 245),  # Off-White
    (220, 220, 220),  # Very Light Gray
    (180, 180, 180),  # Light Gray
    (130, 130, 130),  # Medium Gray
    (90, 90, 90),     # Darker Gray
    (30, 30, 30),     # Very Dark Gray
    (150, 150, 90),   # Muted Olive
    (120, 90, 150),   # Muted Purple
    (90, 150, 150),   # Muted Teal
    (220, 180, 60),   # Muted Gold
]

# Left panel settings
LEFT_PANEL_WIDTH = 300  # Adjust as needed based on your UI design

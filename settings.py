# settings.py

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Grid settings
DEFAULT_TRIANGLE_MODE = 'edge+vertex'  # Options: 'edge', 'edge+vertex'

# Cell settings

# Game rules (default rules)

# Colors (RGB tuples)
# Modern dark theme with vibrant accents
BACKGROUND_COLOR = (18, 18, 24)          # Deeper, richer black
DEAD_CELL_COLOR = (32, 34, 42)           # Subtle blue-gray
GRID_LINE_COLOR = (45, 48, 58)           # Visible but not harsh
TEXT_COLOR = (235, 235, 245)             # Warm white, not pure
PANEL_BACKGROUND_COLOR = (24, 26, 32)    # Slightly elevated from bg

# Accent colors - choose a vibrant primary
ACCENT_PRIMARY = (99, 102, 241)          # Indigo-violet
ACCENT_SECONDARY = (34, 211, 238)        # Cyan
ACCENT_SUCCESS = (52, 211, 153)          # Emerald
ACCENT_WARNING = (251, 191, 36)          # Amber
ACCENT_DANGER = (248, 113, 113)          # Soft red

# Updated button colors
BUTTON_COLOR = (55, 58, 72)              # Elevated surface
BUTTON_HOVER_COLOR = (75, 78, 96)        # Lighter on hover
BUTTON_ACTIVE_COLOR = ACCENT_PRIMARY     # Accent when pressed
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_BORDER_RADIUS = 6
BUTTON_HEIGHT_SMALL = 25
BUTTON_HEIGHT_LARGE = 40

# Chart colors
CHART_BACKGROUND = (28, 30, 38)
CHART_GRID_LINES = (45, 48, 58)
CHART_AXIS_COLOR = (128, 130, 145)

# Scrollbar modernization
SCROLLBAR_TRACK = (35, 38, 48)
SCROLLBAR_HANDLE = (85, 88, 105)
SCROLLBAR_HANDLE_HOVER = (115, 118, 140)

# Fonts
# Typography scale
FONT_NAME = 'Segoe UI'  # Or 'SF Pro Display' on Mac, 'Ubuntu' on Linux
FONT_SIZE_XS = 10
FONT_SIZE_SM = 12
FONT_SIZE_BASE = 14
FONT_SIZE_LG = 16
FONT_SIZE_XL = 20
FONT_SIZE_2XL = 24

# Font weights (where supported)
FONT_WEIGHT_NORMAL = False
FONT_WEIGHT_BOLD = True

# Default initial alive percentage

# Lifeform Colors (RGB tuples)
LIFEFORM_COLORS_ALIVE = [
    (239, 68, 68),    # Red-500
    (34, 197, 94),    # Green-500
    (59, 130, 246),   # Blue-500
    (250, 204, 21),   # Yellow-400
    (168, 85, 247),   # Purple-500
    (236, 72, 153),   # Pink-500
    (20, 184, 166),   # Teal-500
    (249, 115, 22),   # Orange-500
    (132, 204, 22),   # Lime-500
    (6, 182, 212),    # Cyan-500
]

# Define colors for static cells
LIFEFORM_COLORS_STATIC = [
    (252, 165, 165),  # Red-300
    (134, 239, 172),  # Green-300
    (147, 197, 253),  # Blue-300
    (253, 224, 71),   # Yellow-300
    (216, 180, 254),  # Purple-300
    (249, 168, 212),  # Pink-300
    (94, 234, 212),   # Teal-300
    (253, 186, 116),  # Orange-300
    (190, 242, 100),  # Lime-300
    (103, 232, 249),  # Cyan-300
]

# Left panel settings
LEFT_PANEL_WIDTH = 300  # Adjust as needed based on your UI design

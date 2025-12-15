from settings import LIFEFORM_COLORS_ALIVE, LIFEFORM_COLORS_STATIC

class Lifeform:
    """
    Represents a single lifeform with its own rules and colors.
    """
    def __init__(self, lifeform_id, birth_rules, survival_rules):
        """
        Initialize a Lifeform.

        Args:
            lifeform_id (int): Unique identifier for the lifeform (1-10).
            birth_rules (list): List of neighbor counts for a dead cell to become alive.
            survival_rules (list): List of neighbor counts for a live cell to survive.
        """
        self.id = lifeform_id
        self.birth_rules = birth_rules
        self.survival_rules = survival_rules
        self.color_alive = LIFEFORM_COLORS_ALIVE[lifeform_id - 1]
        self.color_static = LIFEFORM_COLORS_STATIC[lifeform_id - 1]
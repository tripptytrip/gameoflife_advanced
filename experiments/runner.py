# experiments/runner.py
#
# Headless experiment runner for lattice simulations.

from __future__ import annotations

import random
from typing import Any, Dict, Optional

import numpy as np

from grid_factory import create_grid
from lifeform import Lifeform
from rules import Rule
import copy


def make_grid(
    shape: str,
    lifeform,
    width: int,
    height: int,
    p0: float,
    seed: Optional[int],
    wrap: bool,
    triangle_mode: str = "edge+vertex",
):
    """
    Create a grid for the requested lattice using a single lifeform.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    grid = create_grid(
        lifeforms=[lifeform],
        initial_alive_percentage=p0,
        shape=shape,
        grid_width=width,
        grid_height=height,
        wrap=wrap,
        triangle_neighborhood_mode=triangle_mode,
    )

    return grid

def run_damage_spreading(
    shape: str,
    rule: Rule,
    steps: int,
    seed: Optional[int],
    p0: float,
    width: int = 64,
    height: int = 64,
    wrap: bool = True,
    triangle_mode: str = "edge+vertex",
    flip_cells: int = 1,
) -> np.ndarray:
    """
    Classic damage spreading: evolve two copies with a tiny perturbation.
    Returns H(t) = mean disagreement over time.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    lf = Lifeform(1, birth_rules=sorted(rule.birth), survival_rules=sorted(rule.survive))
    grid_a = make_grid(shape, lf, width, height, p0, seed, wrap, triangle_mode)
    grid_b = copy.deepcopy(grid_a)

    total = grid_a.grid.size
    flip_cells = min(flip_cells, total)
    flat_indices = np.random.choice(total, flip_cells, replace=False)
    rows, cols = np.unravel_index(flat_indices, grid_a.grid.shape)
    for r, c in zip(rows, cols):
        if grid_b.grid[r, c] == 0:
            grid_b.grid[r, c] = lf.id
            grid_b.grid_lifespans[r, c] = 1
        else:
            grid_b.grid[r, c] = 0
            grid_b.grid_lifespans[r, c] = 0

    H = np.zeros(steps, dtype=float)
    H[0] = np.mean(grid_a.grid != grid_b.grid)

    for t in range(1, steps):
        grid_a.update()
        grid_b.update()
        H[t] = np.mean(grid_a.grid != grid_b.grid)

    return H


def run_timeseries(
    grid,
    lifeform_id: int,
    steps: int,
    burn_in_frac: float = 0.4,
    epsilon: float = 1e-6,
    freeze_window: int = 100,
) -> Dict[str, np.ndarray]:
    """
    Run a headless simulation and return rho/activity timeseries.
    """
    total_cells = grid.grid.size
    rho = np.zeros(steps, dtype=float)
    activity = np.zeros(steps, dtype=float)
    frozen_at: Optional[int] = None
    quiet_streak = 0

    burn_in = int(steps * burn_in_frac)

    for step in range(steps):
        if step > 0:
            grid.update()

        alive = np.count_nonzero(grid.grid == lifeform_id)
        rho[step] = alive / total_cells

        if step > 0:
            activity[step] = abs(rho[step] - rho[step - 1])

            # Freeze detection after burn-in
            if step >= burn_in and activity[step] <= epsilon:
                quiet_streak += 1
                if quiet_streak >= freeze_window and frozen_at is None:
                    frozen_at = step
            else:
                quiet_streak = 0

    result: Dict[str, Any] = {"rho": rho, "activity": activity, "frozen_at": frozen_at}
    return result

# analysis/criticality_score.py
#
# Heuristic criticality scoring based on rho/activity shape.

from __future__ import annotations

import numpy as np


def _band_score(value, low, high, target_low, target_high):
    """
    Piecewise reward: linear up into the target band, flat in band, linear down.
    """
    if value < low or value > high:
        return 0.0
    if value < target_low:
        return (value - low) / (target_low - low)
    if value > target_high:
        return (high - value) / (high - target_high)
    return 1.0


def score_timeseries(rho: np.ndarray, activity: np.ndarray, frozen_at, steps: int, H: np.ndarray | None = None) -> float:
    """
    Compute a heuristic criticality score from timeseries.

    Heuristics:
    - Alive-band: prefer rho_mean in ~[0.05, 0.40].
    - Activity-band: prefer moderate activity (not zero, not maximal).
    - Variance: reward some variance but clamp so pure noise doesn't dominate.
    - Freeze penalty: early freeze is penalized.
    """
    if len(rho) == 0 or len(activity) == 0:
        return 0.0

    burn_in = int(steps * 0.4)
    rho_post = rho[burn_in:]
    activity_post = activity[burn_in:]

    # Basic stats
    rho_mean = float(np.mean(rho_post))
    rho_std = float(np.std(rho_post))
    act_mean = float(np.mean(activity_post))
    act_std = float(np.std(activity_post))

    # Alive band: aim for mid occupancy
    alive_score = _band_score(rho_mean, low=0.0, high=0.6, target_low=0.05, target_high=0.40)

    # Activity band: reward moderate activity
    activity_score = _band_score(act_mean, low=0.0, high=0.2, target_low=0.005, target_high=0.05)

    # Variance rewards but clamped
    rho_var_score = min(rho_std / 0.1, 1.0)
    act_var_score = min(act_std / 0.05, 1.0)

    damage_score = 0.0
    if H is not None and len(H) >= steps:
        H_post = H[burn_in:]
        h_mean = float(np.mean(H_post))
        h_growth = float(H[-1] - H[burn_in])
        h_band = _band_score(h_mean, low=0.0, high=0.8, target_low=0.1, target_high=0.4)
        h_growth_band = _band_score(h_growth, low=-0.05, high=0.6, target_low=0.02, target_high=0.2)
        damage_score = 0.5 * h_band + 0.5 * h_growth_band

    # Freeze penalty: earlier freeze hurts more
    freeze_penalty = 0.0
    if frozen_at is not None:
        freeze_penalty = max(0.0, 1.0 - frozen_at / max(1, steps))

    # Weighted combination
    score = (
        0.3 * alive_score
        + 0.2 * activity_score
        + 0.15 * rho_var_score
        + 0.15 * act_var_score
        + 0.2 * damage_score
    )

    score *= (1.0 - 0.5 * freeze_penalty)

    # Clamp to [0,1]
    return max(0.0, min(1.0, score))

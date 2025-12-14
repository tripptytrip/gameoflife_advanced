# Lattice Baseline Audit

- Neighbor counts:
  - Square: 8 (Moore) via 3×3 convolution kernel with center removed in `square_grid.py:update`.
  - Hex: 6 offsets in `hexagon_grid_numpy.py:_create_neighbor_map` (odd-q layout).
  - Triangle: configurable; default `edge+vertex` gives 12 neighbors per cell (orientation-consistent sets) in `triangle_grid_numpy.py:_build_neighbor_offsets`; `edge` mode retains 3-neighbor edge-only adjacency.

- Hardcoded N=8 assumptions:
  - `game.py:randomise_lifeforms` seeds rules with `random.sample(range(0, 9), ...)`, assuming neighbor counts 0–8.
  - `rule_discovery.py` uses an 18-bit genome (9 birth + 9 survival) in `rules_to_gene`/`gene_to_rules` and seeds populations with `range(9)`, matching square’s 0–8 neighborhood.

- Boundary conditions:
  - Square: toroidal wrap via `convolve2d(..., boundary='wrap')` in `square_grid.py:update`.
  - Hex: now configurable; wrap by default (modulo indexing in neighbor map), clamp when `wrap=False`.
  - Triangle: now configurable; wrap by default (modulo indexing in neighbor map), clamp when `wrap=False`.

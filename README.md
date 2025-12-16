# Game of Life Advanced
![Game of Life Hexagon](game%20of%20life%20hexagon.png)
A sophisticated and extensible implementation of Conway's Game of Life, built with Python and Pygame. This project goes far beyond a traditional Game of Life simulator, offering a powerful platform for experimentation and discovery in the world of cellular automata.

It features multiple competing lifeforms, selectable grid geometries, and a background genetic algorithm that automatically discovers novel, complex rule sets.

### Table of Contents

- [Features](#features)
- [Core Components](#core-components)
- [Installation](#installation)
- [Usage](#usage)
- [Automated Rule Discovery](#automated-rule-discovery)
- [Data Recording & Analysis](#data-recording--analysis)
- [Dependencies](#dependencies)

---

### Features

- **Multiple Grid Geometries**: Run simulations on `square`, `hexagon`, or `triangle` grids.
- **Multi-Lifeform Simulation**: Simulate up to 10 distinct "species" at once, each with its own unique color and birth/survival rules.
- **Performant Backend**: The simulation grid is powered by NumPy and SciPy, allowing for large grid sizes and fast, efficient updates.
- **Automated Rule Discovery**: A genetic algorithm runs in a background thread, continuously searching for "interesting" and complex rules based on criticality analysis.
- **Advanced Data Recording**: Every simulation run is logged to a `species.db` SQLite database, capturing a rich set of metrics per-generation for each lifeform (e.g., population, cluster size, entropy, mobility).
- **Dynamic Settings Panel**: An interactive UI to control every aspect of the simulation on-the-fly, from grid size and shape to the rules of each lifeform.
- **Execution Modes**: Supports both interactive, visual simulation and a headless "Auto-Run" mode for rapid, large-scale data collection.
- **Kill Attribution**: A unique analysis feature that attempts to determine which lifeform "killed" another in cases of death by overcrowding.

---

### Core Components

- **`main.py`**: The primary entry point. It launches the visual simulation and the background rule discovery thread.
- **`game.py`**: Orchestrates the main application, including the Pygame window, the main loop, event handling, and rendering the UI and chart.
- **`rule_discovery.py`**: A background task that uses a genetic algorithm to find novel rules. Results are saved to `discovered_rules_*.json`.
- **`data_recorder.py`**: Manages all writing to the `species.db` database in a thread-safe, buffered manner.
- **`*_grid.py`**: The core simulation logic for each grid geometry, built on NumPy for performance.
- **`species.db`**: The SQLite database where all experimental data is stored.

---

### Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/tripptytrip/gameoflife_advanced.git
    cd gameoflife_advanced
    ```

2.  **Create a Virtual Environment (Recommended)**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

---

### Usage

1.  **Run the Main Script**

    To start the application, run `main.py`. This will open the Pygame window for the interactive simulation and start the rule discovery process in the background.

    ```bash
    python main.py
    ```

2.  **Controls**

    -   **Spacebar**: Start/Pause the simulation.
    -   **R**: Reset the grid to its initial random state.
    -   **N**: Generate a new random grid with a new set of random lifeforms.
    -   **S**: Step forward one generation (only when paused).
    -   **Click on a Cell**: Toggle the state (alive/dead) of a cell.

3.  **Settings Panel**

    The panel on the left of the screen provides full control over the simulation. You can adjust grid dimensions, select the grid shape, set the number of lifeforms, and define the specific `B/S` (Birth/Survival) rules for each one.

---

### Automated Rule Discovery

This project's most advanced feature is its ability to "discover" new rules on its own. The `rule_discovery.py` script uses a genetic algorithm to find rules that produce complex, "critical" behavior—somewhere between dying out and exploding.

-   The process runs automatically in the background when you start `main.py`.
-   It evaluates rules based on a fitness score derived from running headless simulations and analyzing the output (e.g., activity, damage spreading, and compression ratio).
-   When a high-scoring rule is found, it is saved to a JSON file named `discovered_rules_[shape].json` (e.g., `discovered_rules_square.json`).

---

### Data Recording & Analysis

The application is designed for rigorous data collection.

-   **Database**: All simulation data is recorded in a SQLite database named `species.db`.
-   **Tables**:
    -   `life_records`: Stores per-generation data for every lifeform, including its rules, alive/static counts, and advanced metrics like `average_cluster_size`, `growth_rate`, `entropy`, `mobility`, and more.
    -   `lifeform_meta`: Stores metadata for each unique lifeform profile to reduce data redundancy.
-   **Auto-Run Mode**: For high-throughput experiments, you can use the "Auto Run" feature in the settings panel. This will run multiple simulations back-to-back with randomized parameters, populating the database without requiring user interaction.

---

### Dependencies

-   Python 3.7+
-   Pygame
-   NumPy
-   SciPy
-   SQLite3 (built-in with Python)
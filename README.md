## Game of Life Advanced

A customisable and extensible implementation of Conway's Game of Life, featuring multiple lifeforms, different grid shapes, and comprehensive data recording.

### Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Controls](#controls)
  - [Settings Panel](#settings-panel)
  - [Auto-Run Mode](#auto-run-mode)
- [Data Recording](#data-recording)
- [Customization](#customization)
  - [Lifeforms](#lifeforms)
  - [Grid Shapes](#grid-shapes)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

---

### Features

- **Multiple Lifeforms**: Simulate up to 10 different lifeforms, each with unique birth and survival rules.
- **Different Grid Shapes**: Choose between triangle, square, or hexagon grids.
- **Dynamic Settings Panel**: Adjust simulation parameters on-the-fly with an interactive settings panel.
- **Data Recording**: Collect detailed statistics of each simulation session in a SQLite database.
- **Visualization**: Real-time rendering using Pygame with enhanced UI elements.
- **Auto-Run Mode**: Automate simulations for data collection and analysis.

---

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/gameoflife_advanced.git
   cd gameoflife_advanced

2. **Create a Virtual Environment (Optional but Recommended)**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    
3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt

    #Note: the main dependencies are:
    #    pygame
    #    sqlite3 (built-in with Python)

### Usage

1. **Run the main script to start the simulation:**

    ```bash
    python game.py


2. **Controls**

    Spacebar: Start/Pause the simulation.
    R: Reset the grid to the initial state.
    N: Generate a new random grid with new lifeforms.
    S: Step forward one generation (when paused).
    Click on Cells: Toggle the state (alive/dead) of individual cells.

### Settings Panel

1. **On the left side of the window, there is a settings panel where you can:**

    Adjust the Initial Alive Percentage of cells.
    Change the Simulation Speed (FPS).
    Set the Number of Lifeforms (1-10).
    Modify the Grid Width and Grid Height.
    Select the Grid Shape: triangle, square, or hexagon.
    Define custom Birth and Survival Rules for each lifeform.
    Apply changes to restart the simulation with new settings.
    Randomise Lifeforms to generate new rule sets.
    Initiate Auto Run mode for automated simulations.

2. **Auto-Run Mode - To collect data across multiple simulations:**

    Set the Number of Generations for each simulation in the settings panel.
    Click the Auto Run button.
    The simulation will run automatically for the specified number of generations, collecting data in the database.

    Note: During auto-run mode, the simulation UI may not update every frame to enhance performance.
   
### Data Recording

1. **All simulation data is recorded in a SQLite database named species.db.**
   
   The data_recorder.py script handles the insertion of records, including:

    Session ID: Unique identifier for each simulation session.
    Generation: The current generation number.
    Lifeform Data: Birth and survival rules, alive counts, and other metrics for each lifeform.
    Metrics: Statistics such as growth rate, death rate, average lifespan, cluster sizes, entropy, mobility, and diversity.

2. **The database consists of two tables:**

    life_records: Stores per-generation data for lifeforms.
    lifeform_meta: Stores metadata for each lifeform used in the simulations.

### Customization

1. **Lifeforms**

   You can customize lifeforms by setting their birth and survival rules:

   In the settings panel, scroll down to the Lifeform Rules section.

   For each lifeform (up to 10), input comma-separated numbers representing neighbor counts for:
   
     Birth Rules: Conditions under which a dead cell becomes alive.
     Survival Rules: Conditions under which a live cell continues to live.

    Click Apply to restart the simulation with the new rules.

2. **Grid Shapes**

    The simulation supports three grid shapes:

      Triangle Grid: Cells are arranged in a triangular lattice.
      Square Grid: Traditional Game of Life grid.
      Hexagon Grid: Cells are hexagonally packed.

    Select the desired grid shape from the settings panel under Grid Shape.
    
### Dependencies:

      Python 3.7 or higher
      Pygame library
      SQLite3 (included with Python)

### Acknowledgments

  Conway's Game of Life: A cellular automaton devised by mathematician John Horton Conway.
  Pygame: A set of Python modules designed for writing video games.

Additional Notes

  Ensure your system meets the necessary graphical requirements to run Pygame applications.
  The simulation's performance may vary based on grid size and the number of lifeforms.
  For large simulations or data collection, consider running the program without rendering the UI to improve performance.


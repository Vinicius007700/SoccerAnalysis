# SoccerAnalysis

This project is a tool designed to load soccer tracking data, visualize the match in 2D and show the ball possesion. 

It utilizes the **Metrica Sports** open data format and leverages libraries like `kloppy` for data loading and `mplsoccer` for pitch plotting.



## 🚀 Features

* **Data Parsing:** Efficiently loads tracking and event data using `kloppy` and `pandas`.
* **2D Match Animation:** Visualizes player movements and the ball on a scaled pitch.
* **Tactical Analysis:** Dynamically calculates and visualizes:
    * **Defensive Lines:** Identifies the structural shape of the defense.
    * **Attacking Lines:** Visualizes the formation of the attacking team.
* **Ball Possession:** (In development) Logic to track and visualize ball possession statistics.
* **Modular Architecture:** Organized into specific classes (`Match`, `Team`, `Player`, `Strategy`) for scalability.


## 📂 Project Structure

* **`main.py`**: The entry point. It sets up file paths, initializes the `Match` object, and runs the animation loop.
* **`assets/`**: Contains the core logic classes.
    * **`Match.py`**: Manages data loading, team initialization, and score tracking.
    * **`draw_game.py`**: Handles the visualization logic (`MatchAnimator`), drawing the pitch, players, and updating frames.
    * **`strategy.py`**: Contains algorithms to calculate tactical lines (e.g., defense depth, attacking width).
    * **`Team.py` & `Player.py`**: Data structures to organize team and player attributes.
    * **`manipulate_data.py`**: Helper functions for data transformations.
* **`data/`**: Stores the Metrica Sports sample data (`.xml`, `.txt`, `.json`).

## 🧠 Future Goals

The architecture of this project is designed to support increasing complexity. Future steps include:
* Integrating Machine Learning models for event prediction.
* Advanced possession metrics.
* Real-time tactical alerts.
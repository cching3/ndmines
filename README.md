# N-Dimensional Minesweeper

This project is an implementation of **Minesweeper** in an **N-dimensional space**. Instead of the usual 2D grid, this version supports an arbitrary number of dimensions. The game allows you to dig at different coordinates, and the goal is to reveal all safe squares (non-mine squares) without triggering any mines.

The game provides an interactive way to play, with a command-line interface, and supports multi-dimensional boards of arbitrary size.

---

## Features

- **N-Dimensional Gameplay**: Play Minesweeper in any number of dimensions (e.g., 2D, 3D, etc.).
- **Recursive Digging**: Automatically reveals neighboring safe squares, with recursive logic to expose connected empty spaces.
- **Interactive Game Loop**: Play the game in an interactive command-line interface, where you specify coordinates to dig.
- **Victory and Defeat Conditions**: The game tracks your progress and ends with a victory if all non-mine squares are revealed, or a defeat if you trigger a mine.

---

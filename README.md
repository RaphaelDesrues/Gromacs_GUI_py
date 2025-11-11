# GroGUI — Node-Based GUI for GROMACS

GroGUI is a graphical tool that lets you build and run GROMACS workflows visually, using interconnected nodes.  
Each node represents a GROMACS command (`gmx pdb2gmx`, `gmx editconf`, etc.) and displays its command-line preview in real time.

> **Note:** The code is a personal learning project — functional but not perfect — and may contain experimental parts or unfinished features.

Work still in progress...

---

## Features

- Visual node graph for GROMACS workflows (`pdb2gmx`, `editconf`, `solvate`, `grompp`, `mdrun`, etc.)
- Typed ports for automatic file propagation between connected nodes
- Per-node preview properties with optional “extra” flags / parameters (`Optional Props`)
- Command preview for the selected node
- Sequential execution with live console output
- Save/Load sessions (graph and UI state)
- Theming via QSS (rounded widgets, color-coded properties)

---

## Requirements

- Python 3.9+
- GROMACS installed and available in PATH (`gmx --version`)
- Python dependencies:
  - `Qt.py`
  - `PyQt5`
  - `NodeGraphQt`

# PCB Gmsh Generator

This repository provides tools for creating a Gmsh `.geo` script describing a simple PCB geometry.  The script can be generated via a small Tkinter GUI or directly from the command line.

## Prerequisites
- Python 3.8 or newer.
- The Tkinter module (included in most Python installations).
- Gmsh installed and accessible via the `gmsh` command.

## Module Layout
All Python files now live in the repository root:
- `config.py` – defines the `PCBParams` dataclass containing all geometry parameters.
- `gmsh_generator.py` – provides `generate_geo(params)` returning the `.geo` contents.
- `gui.py` – Tkinter GUI built on top of `PCBParams` and `generate_geo`.
- `utils.py` – helper utilities such as launching Gmsh.

`main.py` launches the GUI.

## Running the GUI
1. Execute `python main.py` to launch the GUI.
2. Adjust the PCB parameters as needed.
3. Specify the output directory and file name.
4. (Optional) Use **Browse...** next to *Gmsh Executable* to locate `gmsh` if it is not on your `PATH`. The selected path will be remembered.
5. Click **Generate GMSH Script**. If *Open in Gmsh after generation* is checked, the file opens in Gmsh automatically.

The generated script defines four volumes: the ground with vias, the trace, the surrounding air, and the dielectric. Comments in the file list these IDs for reference.

## Command Line Usage
A simple CLI is also available via `__main__.py`:

```bash
python __main__.py -o pcb_model.geo [--open | --mesh] [--param value ...]
```

Use `--mesh` to run Gmsh in batch mode so the `.msh` file is created without opening the Gmsh GUI.

All parameters from `PCBParams` are available as flags (e.g. `--ground-size 15`). Use `--help` to see the full list of options.

## Opening the file in Gmsh
1. Open the generated `.geo` file in Gmsh (or let the GUI/CLI do this step).
   The script now calls `Mesh 3;` to automatically generate a 3D mesh and save it as `pcb_model.msh`.

## Importing into Elmer
1. Convert the mesh using `ElmerGrid 4 2 pcb_model.msh`.
2. Open the generated mesh directory in ElmerGUI or reference it in your simulation setup.
3. Assign bodies according to the volume IDs noted in the `.geo` file.

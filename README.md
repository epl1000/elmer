# PCB Gmsh Generator

This repository provides tools for creating a Gmsh `.geo` script describing a simple PCB geometry.  The script can be generated via a small Tkinter GUI or directly from the command line.

## Prerequisites
- Python 3.8 or newer.
- The Tkinter module (included in most Python installations).
- Gmsh installed and accessible via the `gmsh` command.

## Module Layout
The code lives in the `src/pcb_gmsh_generator/` package:
- `config.py` – defines the `PCBParams` dataclass containing all geometry parameters.
- `gmsh_generator.py` – provides `generate_geo(params)` returning the `.geo` contents.
- `gui.py` – Tkinter GUI built on top of `PCBParams` and `generate_geo`.
- `utils.py` – helper utilities such as launching Gmsh.

The old monolithic script has been replaced by a thin `main.py` which simply launches the GUI.

## Running the GUI
1. Execute `python main.py` or `python -m pcb_gmsh_generator --gui`.
2. Adjust the PCB parameters as needed.
3. Specify the output directory and file name.
4. Click **Generate GMSH Script**. If *Open in Gmsh after generation* is checked, the file opens in Gmsh automatically.

The generated script defines four volumes: the ground with vias, the trace, the surrounding air, and the dielectric. Comments in the file list these IDs for reference.

## Command Line Usage
The package also exposes a CLI. Run:

```bash
python -m pcb_gmsh_generator -o pcb_model.geo [--open] [--param value ...]
```

All parameters from `PCBParams` are available as flags (e.g. `--ground-size 15`).  Use `--help` to see the full list of options.

## Opening the file in Gmsh
1. Open the generated `.geo` file in Gmsh (or let the GUI/CLI do this step).
2. Use **Mesh → 3D** to create the mesh.
3. Save the result as `pcb_model.msh`.

## Importing into Elmer
1. Convert the mesh using `ElmerGrid 4 2 pcb_model.msh`.
2. Open the generated mesh directory in ElmerGUI or reference it in your simulation setup.
3. Assign bodies according to the volume IDs noted in the `.geo` file.

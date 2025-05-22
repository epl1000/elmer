# PCB Gmsh Generator

This repository provides a small GUI for generating a Gmsh `.geo` script describing a simple PCB geometry. The script can launch Gmsh directly and is meant to facilitate importing the mesh into the Elmer solver.

## Prerequisites
- Python 3.8 or newer.
- The Tkinter module (included in most Python installations).
- Gmsh installed and accessible via the `gmsh` command.

## Running the GUI
1. Execute `python groundcut_030625.py`.
2. Adjust the PCB parameters as needed.
3. Specify the output directory and file name.
4. Click **Generate GMSH Script**. If *Open in Gmsh after generation* is checked, the file opens in Gmsh automatically.

The script produces a `.geo` file defining four volumes: the ground with vias, the trace, the surrounding air, and the dielectric. Comments in the file list these IDs for reference.

## Opening the file in Gmsh
1. Open the generated `.geo` file in Gmsh (or let the GUI do this step).
2. Use **Mesh \u2192 3D** to create the mesh.
3. Save the result as `pcb_model.msh`.

## Importing into Elmer
1. Convert the mesh using `ElmerGrid 4 2 pcb_model.msh`.
2. Open the generated mesh directory in ElmerGUI or reference it in your simulation setup.
3. Assign bodies according to the volume IDs noted in the `.geo` file.

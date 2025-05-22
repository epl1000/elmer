import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import platform

class PCBGmshGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("PCB GMSH Generator")
        self.root.geometry("650x750")

        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Parameter inputs
        param_frame = ttk.LabelFrame(main_frame, text="PCB Parameters", padding="10")
        param_frame.pack(fill=tk.X, padx=5, pady=5)

        # Existing parameters
        self.ground_size = tk.DoubleVar(value=10.0)
        self.ground_thickness = tk.DoubleVar(value=0.035)
        self.separation = tk.DoubleVar(value=0.15)
        self.trace_thickness = tk.DoubleVar(value=0.035)
        self.trace_width = tk.DoubleVar(value=0.2)
        self.trace_length = tk.DoubleVar(value=9.8)
        self.via_width = tk.DoubleVar(value=0.2)
        self.via_depth = tk.DoubleVar(value=0.2)
        self.guard_via_width = tk.DoubleVar(value=0.2)  # NEW for guard vias
        self.sphere_radius = tk.DoubleVar(value=20.0)

        # NEW parameters for rectangular cut
        self.cut_width = tk.DoubleVar(value=1.0)
        self.cut_height = tk.DoubleVar(value=1.0)

        # Create labeled parameter fields
        self.create_parameter_field(param_frame, "Ground Size (mm):", self.ground_size, 0)
        self.create_parameter_field(param_frame, "Ground Thickness (mm):", self.ground_thickness, 1)
        self.create_parameter_field(param_frame, "Separation (mm):", self.separation, 2)
        self.create_parameter_field(param_frame, "Trace Thickness (mm):", self.trace_thickness, 3)
        self.create_parameter_field(param_frame, "Trace Width (mm):", self.trace_width, 4)
        self.create_parameter_field(param_frame, "Trace Length (mm):", self.trace_length, 5)
        self.create_parameter_field(param_frame, "Via Width (mm):", self.via_width, 6)
        self.create_parameter_field(param_frame, "Guard Via Width (mm):", self.guard_via_width, 7)
        self.create_parameter_field(param_frame, "Via Depth (mm):", self.via_depth, 8)
        self.create_parameter_field(param_frame, "Sphere Radius (mm):", self.sphere_radius, 9)

        # NEW GUI fields for rectangular ground-plane cut
        self.create_parameter_field(param_frame, "Cut Width (mm):", self.cut_width, 10)
        self.create_parameter_field(param_frame, "Cut Height (mm):", self.cut_height, 11)

        # Mesh options
        mesh_frame = ttk.LabelFrame(main_frame, text="Mesh Options", padding="10")
        mesh_frame.pack(fill=tk.X, padx=5, pady=5)

        self.mesh_size_min = tk.DoubleVar(value=0.05)
        self.mesh_size_max = tk.DoubleVar(value=2.0)
        self.create_parameter_field(mesh_frame, "Min Mesh Size (mm):", self.mesh_size_min, 0)
        self.create_parameter_field(mesh_frame, "Max Mesh Size (mm):", self.mesh_size_max, 1)

        # Output options
        output_frame = ttk.LabelFrame(main_frame, text="Output Options", padding="10")
        output_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_file = tk.StringVar(value="pcb_model.geo")
        ttk.Entry(output_frame, textvariable=self.output_file, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(output_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir = tk.StringVar(value=os.getcwd())
        dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=30)
        dir_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_directory).grid(row=1, column=2, padx=5, pady=5)

        self.open_in_gmsh = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Open in Gmsh after generation", variable=self.open_in_gmsh).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5
        )

        # Script preview
        preview_frame = ttk.LabelFrame(main_frame, text="Script Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_text = tk.Text(preview_frame, wrap=tk.NONE, height=15)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.preview_text, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(button_frame, text="Update Preview", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate GMSH Script", command=self.generate_script).pack(side=tk.RIGHT, padx=5)

        self.update_preview()

    def create_parameter_field(self, parent, label_text, variable, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        entry = ttk.Entry(parent, textvariable=variable, width=10)
        entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        variable.trace_add("write", lambda *args: self.update_preview())
        return entry

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)

    def update_preview(self):
        try:
            script_content = self.generate_script_content()
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, script_content)
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "Error generating preview: " + str(e))

    def generate_script_content(self):
        # Retrieve parameter values
        g_size = self.ground_size.get()
        g_thk = self.ground_thickness.get()
        sep = self.separation.get()
        t_thk = self.trace_thickness.get()
        t_width = self.trace_width.get()
        t_length = self.trace_length.get()
        v_width = self.via_width.get()
        v_depth = self.via_depth.get()
        gv_width = self.guard_via_width.get()
        sph_rad = self.sphere_radius.get()
        mesh_min = self.mesh_size_min.get()
        mesh_max = self.mesh_size_max.get()

        # NEW: retrieve cut width/height
        cut_w = self.cut_width.get()
        cut_h = self.cut_height.get()

        template = f"""//***************************************************************************************************
// PCB Model - Generated by PCB GMSH Generator
//***************************************************************************************************

SetFactory("OpenCASCADE");
Geometry.OCCSewFaces      = 1;
Geometry.OCCFixSmallEdges = 1;
Geometry.OCCFixSmallFaces = 1;
Geometry.OCCAutoFix       = 1;
Geometry.Tolerance        = 1e-8;

//------------------------- 1) Parameters -------------------------//
ground_size      = {g_size};
ground_thickness = {g_thk};
separation       = {sep};
trace_thickness  = {t_thk};
trace_width      = {t_width};
trace_length     = {t_length};
via_width        = {v_width};
via_depth        = {v_depth};
sphere_radius    = {sph_rad};

z0_ground_bot    = 0.0;
z1_ground_top    = z0_ground_bot + ground_thickness;
z2_trace_bot     = z1_ground_top + separation;
z3_trace_top     = z2_trace_bot + trace_thickness;
via_z_bot        = z1_ground_top - 1e-5;
via_z_top        = z3_trace_top;
eps              = 1e-6;

//------------------------- 2) Create Geometry -------------------------//
// Ground plane (Box 1)
Box(1) = {{
  -ground_size/2, -ground_size/2, z0_ground_bot,
   ground_size,    ground_size,    ground_thickness
}};

// *** ADDED: rectangular cut only through the ground plane ***
// We'll center it under the trace.
cut_w = {cut_w};
cut_h = {cut_h};
x_cut_center = -5.0 + trace_length/2;
y_cut_center = 0.0;

// Create the cut box (Box 10)
Box(10) = {{
  x_cut_center - cut_w/2,
  y_cut_center - cut_h/2,
  z0_ground_bot,
  cut_w,
  cut_h,
  ground_thickness
}};

// Replace Volume(1) with a difference: ground minus the new cut
cutRes[] = BooleanDifference{{ Volume{{1}}; Delete; }}{{ Volume{{10}}; Delete; }};
// Rename that difference back to volume #1
SetId{{ Volume{{cutRes[0]}} }} 1;
// *** END ADDED LINES ***

// Main via (Box 2)
Box(2) = {{
  4.8, -0.1, via_z_bot,
  via_width, via_depth, (via_z_top - via_z_bot - eps)
}};

// Trace (Box 3)
Box(3) = {{
  -5.0, -trace_width/2, z2_trace_bot + eps,
   trace_length, trace_width, trace_thickness - 2*eps
}};

// Bounding sphere (Sphere 4)
Sphere(4) = {{ 0, 0, 0, sphere_radius }};

// Guard vias (Boxes 5 to 8)
x1 = -5.0 + trace_length/3.0;
x2 = -5.0 + 2.0*(trace_length/3.0);
Box(5) = {{
  x1, -0.4, via_z_bot,
  {gv_width}, {gv_width}, (via_z_top - via_z_bot - eps)
}};
Box(6) = {{
  x1,  0.2, via_z_bot,
  {gv_width}, {gv_width}, (via_z_top - via_z_bot - eps)
}};
Box(7) = {{
  x2, -0.4, via_z_bot,
  {gv_width}, {gv_width}, (via_z_top - via_z_bot - eps)
}};
Box(8) = {{
  x2,  0.2, via_z_bot,
  {gv_width}, {gv_width}, (via_z_top - via_z_bot - eps)
}};

// *** Added for dielectric ***
// This box fills the entire XY footprint of the PCB,
// from the top of the ground plane to the bottom of the trace.
Box(9) = {{
  -ground_size/2, -ground_size/2, z1_ground_top,
   ground_size,    ground_size,   (z2_trace_bot - z1_ground_top)
}};

//------------------------- 3) Boolean Operations -------------------------//
// Step 1: Fuse all vias together into a single volume array
vias_all[] = BooleanUnion{{Volume{{2}}; Delete; }}{{ Volume{{5,6,7,8}}; Delete; }};
Printf("Vias fusion result -> new volume(s): %g", vias_all[0]);

// Step 2: Union ground plane with all vias
ground_vias[] = BooleanUnion{{Volume{{1}}; Delete; }}{{ Volume{{vias_all[]}}; Delete; }};
Printf("Ground+Vias fusion result -> new volume(s): %g", ground_vias[0]);

// The trace is still Volume #3 by default
trace = 3;
Printf("Trace volume: %g", trace);

// Subtract ground+vias and the trace from Box(9)
// so the dielectric occupies only the gap.
dielectric[] = BooleanDifference{{ Volume{{9}}; Delete; }}{{ Volume{{ground_vias[], trace}}; }};
Printf("Dielectric volume result -> new volume(s): %g", dielectric[0]);

// Step 3: Subtract the PCB volumes (ground_vias, trace, dielectric) from the bounding sphere (#4)
// to define the air region surrounding everything.
air[] = BooleanDifference{{ Volume{{4}}; Delete; }}{{ Volume{{ground_vias[], trace, dielectric[]}}; }};
Printf("Air volume result -> new volume(s): %g", air[0]);

// Ensure geometry is consistent
Coherence;

//------------------------- 4) Define Physical Volumes -------------------------//
// We now have four distinct volumes instead of three:
//   ground_vias[]  -> the union of ground plane + all vias (ID = 1)
//   trace (which is volume #3, ID = 2)
//   dielectric[]   -> new volume for the gap (ID = 4)
//   air[]          -> bounding sphere minus the PCB (ID = 3)

Physical Volume("Ground and Vias", 1) = {{ ground_vias[] }};
Physical Volume("Trace", 2)          = {{ trace }};
// *** Added for dielectric ***
Physical Volume("Dielectric", 3)     = {{ dielectric[] }};
Physical Volume("Air", 4)            = {{ air[] }};

// Define the important surfaces for boundary conditions
// This helps Elmer identify boundaries properly
Physical Surface("Ground Bottom", 11) = {{5}}; // Bottom of ground plane
Physical Surface("Air Boundary", 12) = {{6}}; // Outer surface of air volume

//------------------------- 5) Mesh Settings -------------------------//
Point(200) = {{ 0, 0, z1_ground_top, 0.05 }};
Point(201) = {{ 4.8 + via_width/2, 0, via_z_bot, 0.05 }};
Point(202) = {{ x1, 0, via_z_bot, 0.05 }};
Point(203) = {{ x2, 0, via_z_bot, 0.05 }};
Point(204) = {{ -5.0 + trace_length/2.0, 0, z2_trace_bot, 0.05 }};

Field[1] = Distance;
Field[1].PointsList = {{200, 201, 202, 203, 204}};
Field[2] = MathEval;
Field[2].F = "0.05 + 0.1 * F1";
Field[3] = Min;
Field[3].FieldsList = {{2}};
Background Field = 3;

Mesh.Algorithm = 6;
Mesh.Algorithm3D = 10;
Mesh.OptimizeNetgen = 1;
Mesh.Optimize = 1;
Mesh.CharacteristicLengthMax = {mesh_max};
Mesh.CharacteristicLengthMin = {mesh_min};

// Uncomment the following lines to auto-generate the mesh
//Generate 3;
//Save "pcb_model.msh";

// Add helpful comments for Elmer import
Printf("//");
Printf("// IMPORTANT: When importing into Elmer, you should see exactly four volumes:");
Printf("// 1. Ground and Vias (ID 1)");
Printf("// 2. Trace (ID 2)");
Printf("// 3. Air (ID 3)");
Printf("// 4. Dielectric (ID 4)");
Printf("//");
"""
        return template

    def generate_script(self):
        try:
            output_path = os.path.join(self.output_dir.get(), self.output_file.get())
            script_content = self.generate_script_content()
            with open(output_path, 'w') as f:
                f.write(script_content)
            messagebox.showinfo("Success", f"GMSH script has been generated at:\n{output_path}")
            if self.open_in_gmsh.get():
                self.open_gmsh_with_file(output_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate script: {str(e)}")

    def open_gmsh_with_file(self, file_path):
        try:
            try:
                subprocess.Popen(['gmsh', file_path])
                return
            except (FileNotFoundError, subprocess.SubprocessError):
                pass
            if platform.system() == 'Windows':
                gmsh_exe_paths = [
                    r'E:\Gmsh\gmsh-4.13.1-Windows64\gmsh-4.13.1-Windows64',
                    r'C:\Program Files (x86)\Gmsh\gmsh.exe',
                    os.path.expanduser(r'~\AppData\Local\Gmsh\gmsh.exe')
                ]
                for gmsh_path in gmsh_exe_paths:
                    if os.path.exists(gmsh_path):
                        subprocess.Popen([gmsh_path, file_path])
                        return
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', '-a', 'Gmsh', file_path])
                return
            messagebox.showwarning("Gmsh Not Found", "Could not find Gmsh executable. Please open the file manually.")
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to open Gmsh: {str(e)}\nPlease open the file manually.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PCBGmshGenerator(root)
    root.mainloop()

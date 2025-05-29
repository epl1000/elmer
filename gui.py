import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config import PCBParams
from gmsh_generator import generate_geo
from utils import (
    load_last_gmsh_path,
    open_gmsh_with_file,
    save_last_gmsh_path,
)


class PCBGmshGUI:
    def __init__(self, params: PCBParams | None = None) -> None:
        self.params = params or PCBParams()
        self.root = tk.Tk()
        self.root.title("PCB GMSH Generator")
        # Give the window a wider aspect ratio to better fit landscape screens
        self.root.geometry("950x600")
        self._build_widgets()

    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # layout left-hand controls and right-hand preview side by side
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        param_frame = ttk.LabelFrame(left_frame, text="PCB Parameters", padding="10")
        param_frame.pack(fill=tk.X, padx=5, pady=5)

        self._vars = {
            "ground_size": tk.DoubleVar(value=self.params.ground_size),
            "ground_thickness": tk.DoubleVar(value=self.params.ground_thickness),
            "separation": tk.DoubleVar(value=self.params.separation),
            "trace_thickness": tk.DoubleVar(value=self.params.trace_thickness),
            "trace_width": tk.DoubleVar(value=self.params.trace_width),
            "trace_length": tk.DoubleVar(value=self.params.trace_length),
            "via_width": tk.DoubleVar(value=self.params.via_width),
            "via_depth": tk.DoubleVar(value=self.params.via_depth),
            "guard_via_width": tk.DoubleVar(value=self.params.guard_via_width),
            "sphere_radius": tk.DoubleVar(value=self.params.sphere_radius),
            "cut_width": tk.DoubleVar(value=self.params.cut_width),
            "cut_height": tk.DoubleVar(value=self.params.cut_height),
        }

        row = 0
        for label, key in [
            ("Ground Size (mm):", "ground_size"),
            ("Ground Thickness (mm):", "ground_thickness"),
            ("Separation (mm):", "separation"),
            ("Trace Thickness (mm):", "trace_thickness"),
            ("Trace Width (mm):", "trace_width"),
            ("Trace Length (mm):", "trace_length"),
            ("Via Width (mm):", "via_width"),
            ("Guard Via Width (mm):", "guard_via_width"),
            ("Via Depth (mm):", "via_depth"),
            ("Sphere Radius (mm):", "sphere_radius"),
            ("Cut Width (mm):", "cut_width"),
            ("Cut Height (mm):", "cut_height"),
        ]:
            self._create_parameter_field(param_frame, label, self._vars[key], row)
            row += 1

        mesh_frame = ttk.LabelFrame(left_frame, text="Mesh Options", padding="10")
        mesh_frame.pack(fill=tk.X, padx=5, pady=5)
        self._vars["mesh_size_min"] = tk.DoubleVar(value=self.params.mesh_size_min)
        self._vars["mesh_size_max"] = tk.DoubleVar(value=self.params.mesh_size_max)
        self._create_parameter_field(mesh_frame, "Min Mesh Size (mm):", self._vars["mesh_size_min"], 0)
        self._create_parameter_field(mesh_frame, "Max Mesh Size (mm):", self._vars["mesh_size_max"], 1)

        output_frame = ttk.LabelFrame(left_frame, text="Output Options", padding="10")
        output_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_file = tk.StringVar(value="pcb_model.geo")
        ttk.Entry(output_frame, textvariable=self.output_file, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(output_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir = tk.StringVar(value=os.getcwd())
        dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=30)
        dir_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_directory).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(output_frame, text="Gmsh Executable:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.gmsh_exe = tk.StringVar(value=load_last_gmsh_path() or "")
        ttk.Entry(output_frame, textvariable=self.gmsh_exe, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_gmsh_executable).grid(row=2, column=2, padx=5, pady=5)

        self.open_in_gmsh = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Open in Gmsh after generation", variable=self.open_in_gmsh).grid(
            row=3, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5
        )

        preview_frame = ttk.LabelFrame(content_frame, text="Script Preview", padding="10")
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_text = tk.Text(preview_frame, wrap=tk.NONE)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.preview_text, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(button_frame, text="Update Preview", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate GMSH Script", command=self.generate_script).pack(side=tk.RIGHT, padx=5)

        self.update_preview()

    # ------------------------------------------------------------------
    def _create_parameter_field(self, parent, label_text, variable, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        entry = ttk.Entry(parent, textvariable=variable, width=10)
        entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        variable.trace_add("write", lambda *_: self.update_preview())
        return entry

    def browse_directory(self) -> None:
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)

    def browse_gmsh_executable(self) -> None:
        initial = os.path.dirname(self.gmsh_exe.get()) or os.getcwd()
        path = filedialog.askopenfilename(initialdir=initial)
        if path:
            self.gmsh_exe.set(path)
            save_last_gmsh_path(path)

    def _collect_params(self) -> PCBParams:
        return PCBParams(
            ground_size=self._vars["ground_size"].get(),
            ground_thickness=self._vars["ground_thickness"].get(),
            separation=self._vars["separation"].get(),
            trace_thickness=self._vars["trace_thickness"].get(),
            trace_width=self._vars["trace_width"].get(),
            trace_length=self._vars["trace_length"].get(),
            via_width=self._vars["via_width"].get(),
            via_depth=self._vars["via_depth"].get(),
            guard_via_width=self._vars["guard_via_width"].get(),
            sphere_radius=self._vars["sphere_radius"].get(),
            cut_width=self._vars["cut_width"].get(),
            cut_height=self._vars["cut_height"].get(),
            mesh_size_min=self._vars["mesh_size_min"].get(),
            mesh_size_max=self._vars["mesh_size_max"].get(),
        )

    def update_preview(self) -> None:
        try:
            script_content = generate_geo(self._collect_params())
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, script_content)
        except Exception as exc:  # pragma: no cover - interface code
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error generating preview: {exc}")

    def generate_script(self) -> None:
        try:
            output_path = os.path.join(self.output_dir.get(), self.output_file.get())
            script_content = generate_geo(self._collect_params())
            with open(output_path, "w") as f:
                f.write(script_content)
            messagebox.showinfo("Success", f"GMSH script has been generated at:\n{output_path}")
            if self.open_in_gmsh.get():
                gmsh_path = self.gmsh_exe.get().strip() or None
                if gmsh_path:
                    save_last_gmsh_path(gmsh_path)
                open_gmsh_with_file(output_path, gmsh_path)
        except Exception as exc:  # pragma: no cover - interface code
            messagebox.showerror("Error", f"Failed to generate script: {exc}")

    def run(self) -> None:
        self.root.mainloop()

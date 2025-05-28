import os
import platform
import subprocess


def open_gmsh_with_file(file_path: str) -> None:
    """Try to open Gmsh with the given .geo file."""
    try:
        try:
            subprocess.Popen(["gmsh", file_path])
            return
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

        if platform.system() == "Windows":
            gmsh_exe_paths = [
                r"E:\\Gmsh\\gmsh-4.13.1-Windows64\\gmsh-4.13.1-Windows64",
                r"C:\\Program Files (x86)\\Gmsh\\gmsh.exe",
                os.path.expanduser(r"~\\AppData\\Local\\Gmsh\\gmsh.exe"),
            ]
            for gmsh_path in gmsh_exe_paths:
                if os.path.exists(gmsh_path):
                    subprocess.Popen([gmsh_path, file_path])
                    return
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", "Gmsh", file_path])
            return

        print("Warning: Could not find Gmsh executable. Please open the file manually.")
    except Exception as exc:  # pragma: no cover - just logging
        print(f"Warning: Failed to open Gmsh: {exc}\nPlease open the file manually.")

import os
import platform
import subprocess
from typing import Optional

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".pcb_gmsh_gui")


def load_last_gmsh_path() -> Optional[str]:
    """Return the previously saved Gmsh executable path if available."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            path = f.read().strip()
            return path or None
    except OSError:
        return None


def save_last_gmsh_path(path: str) -> None:
    """Persist the selected Gmsh executable path for future sessions."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(path)
    except OSError:
        pass


def open_gmsh_with_file(file_path: str, gmsh_path: Optional[str] = None) -> None:
    """Try to open Gmsh with the given .geo file."""
    try:
        if gmsh_path:
            try:
                subprocess.Popen([gmsh_path, file_path])
                return
            except (FileNotFoundError, subprocess.SubprocessError):
                pass

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

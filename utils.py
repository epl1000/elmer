import os
import platform
import subprocess
import uuid
from pathlib import Path
from typing import Optional

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".pcb_gmsh_gui")
ELMER_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".pcb_elmer_gui")


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


def load_last_elmer_path() -> Optional[str]:
    """Return the previously saved Elmer executable path if available."""
    try:
        with open(ELMER_CONFIG_PATH, "r", encoding="utf-8") as f:
            path = f.read().strip()
            return path or None
    except OSError:
        return None


def save_last_elmer_path(path: str) -> None:
    """Persist the selected Elmer executable path for future sessions."""
    try:
        with open(ELMER_CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(path)
    except OSError:
        pass


def open_gmsh_with_file(file_path: str, gmsh_path: Optional[str] = None) -> None:
    """Run Gmsh in headless mode with the given .geo file."""
    try:
        run_gmsh_batch(file_path, gmsh_path)
    except Exception as exc:  # pragma: no cover - just logging
        print(f"Warning: Failed to run Gmsh: {exc}\nPlease run Gmsh manually.")


def run_gmsh_batch(file_path: str, gmsh_path: Optional[str] = None) -> None:
    """Run Gmsh in batch mode to generate the mesh without launching the GUI."""
    try:
        if gmsh_path:
            try:
                subprocess.run([gmsh_path, file_path, "-nopopup", "-"], check=True)
                return
            except (FileNotFoundError, subprocess.SubprocessError, subprocess.CalledProcessError):
                pass

        try:
            subprocess.run(["gmsh", file_path, "-nopopup", "-"], check=True)
            return
        except (FileNotFoundError, subprocess.SubprocessError, subprocess.CalledProcessError):
            pass

        if platform.system() == "Windows":
            gmsh_exe_paths = [
                r"E:\\Gmsh\\gmsh-4.13.1-Windows64\\gmsh-4.13.1-Windows64",
                r"C:\\Program Files (x86)\\Gmsh\\gmsh.exe",
                os.path.expanduser(r"~\\AppData\\Local\\Gmsh\\gmsh.exe"),
            ]
            for gmsh_path in gmsh_exe_paths:
                if os.path.exists(gmsh_path):
                    subprocess.run([gmsh_path, file_path, "-nopopup", "-"], check=True)
                    return

        print("Warning: Could not find Gmsh executable. Please run Gmsh manually.")
    except Exception as exc:  # pragma: no cover - just logging
        print(f"Warning: Failed to run Gmsh: {exc}\nPlease run Gmsh manually.")


def run_gmsh(
    geo_file: str, output_dir: str, gmsh_path: Optional[str] = None
) -> Path:
    """Run Gmsh on ``geo_file`` and return the generated ``.msh`` path."""

    unique_name = f"mesh_{uuid.uuid4().hex}.msh"
    output_path = Path(output_dir) / unique_name

    args = [geo_file, "-3", "-o", str(output_path)]

    def _attempt(exe: str) -> bool:
        try:
            subprocess.run([exe, *args], check=True)
            return True
        except (FileNotFoundError, subprocess.SubprocessError, subprocess.CalledProcessError):
            return False

    if gmsh_path and _attempt(gmsh_path):
        return output_path

    if _attempt("gmsh"):
        return output_path

    if platform.system() == "Windows":
        gmsh_exe_paths = [
            r"E:\\Gmsh\\gmsh-4.13.1-Windows64\\gmsh-4.13.1-Windows64",
            r"C:\\Program Files (x86)\\Gmsh\\gmsh.exe",
            os.path.expanduser(r"~\\AppData\\Local\\Gmsh\\gmsh.exe"),
        ]
        for exe in gmsh_exe_paths:
            if os.path.exists(exe) and _attempt(exe):
                return output_path

    raise RuntimeError("Could not run Gmsh")

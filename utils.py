import os
import platform
import subprocess
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
            except (
                FileNotFoundError,
                subprocess.SubprocessError,
                subprocess.CalledProcessError,
                PermissionError,
            ):
                pass

        try:
            subprocess.run(["gmsh", file_path, "-nopopup", "-"], check=True)
            return
        except (
            FileNotFoundError,
            subprocess.SubprocessError,
            subprocess.CalledProcessError,
            PermissionError,
        ):
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


def run_gmsh(geo_file: str, output_dir: str, gmsh_path: Optional[str] = None) -> Path:
    """Run Gmsh on ``geo_file`` and return the generated ``.unv`` path."""

    base_name = Path(geo_file).stem
    output_path = Path(output_dir) / f"{base_name}.unv"

    args = [geo_file, "-3", "-o", str(output_path), "-format", "unv"]

    def _attempt(exe: str) -> bool:
        try:
            subprocess.run([exe, *args], check=True)
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except subprocess.CalledProcessError:
            # Some versions of Gmsh return a non-zero exit code even when the
            # mesh file has been written. Treat this as success if the file
            # exists afterwards.
            return output_path.exists()
        except subprocess.SubprocessError:
            return False
        return output_path.exists()

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


def run_elmer_grid(unv_file: str, elmergrid_path: Optional[str] = None) -> str:
    """Run ElmerGrid on ``unv_file`` and capture any output."""

    def _attempt(exe: str) -> Optional[str]:
        args = [exe, "8", "2", unv_file, "-autoclean"]
        try:
            proc = subprocess.run(args, capture_output=True, text=True)
        except FileNotFoundError:
            return None
        except PermissionError:
            return None
        except subprocess.SubprocessError:
            return None

        output = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            raise RuntimeError(output.strip() or f"{exe} exited with code {proc.returncode}")
        return output

    if elmergrid_path:
        result = _attempt(elmergrid_path)
        if result is not None:
            return result

    for exe in ("ElmerGrid", "elmergrid"):
        result = _attempt(exe)
        if result is not None:
            return result

    if platform.system() == "Windows":
        elmer_paths = [
            os.path.expanduser(r"~\\AppData\\Local\\Elmer\\bin\\ElmerGrid.exe"),
            r"C:\\Program Files\\Elmer\\bin\\ElmerGrid.exe",
        ]
        for exe in elmer_paths:
            if os.path.exists(exe):
                result = _attempt(exe)
                if result is not None:
                    return result

    raise RuntimeError("Could not run ElmerGrid")

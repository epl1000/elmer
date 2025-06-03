import argparse
from pathlib import Path
from datetime import datetime

from config import PCBParams
from gmsh_generator import generate_geo
from gui import PCBGmshGUI
from utils import open_gmsh_with_file, run_gmsh, run_elmer_grid


def _add_param_arguments(parser: argparse.ArgumentParser) -> None:
    for field in PCBParams.__dataclass_fields__.values():
        parser.add_argument(
            f"--{field.name.replace('_', '-')}",
            type=float,
            default=field.default,
            help=f"{field.name.replace('_', ' ').title()} (default: {field.default})",
        )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="PCB Gmsh Generator")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"pcb_model_{timestamp}.geo"
    parser.add_argument("-o", "--output", default=default_name, help="Output .geo file")
    parser.add_argument(
        "--open",
        action="store_true",
        help="Run Gmsh on the result without launching the GUI",
    )
    parser.add_argument(
        "--mesh",
        action="store_true",
        help="Run Gmsh in batch mode to generate the mesh without opening the GUI",
    )
    parser.add_argument(
        "--elmergrid",
        action="store_true",
        help="Run ElmerGrid on the generated mesh",
    )
    parser.add_argument(
        "--elmer-exe",
        default="",
        help="Path to the ElmerGrid executable",
    )
    parser.add_argument("--gui", action="store_true", help="Launch GUI instead of CLI")
    _add_param_arguments(parser)
    args = parser.parse_args(argv)

    params = PCBParams(**{f: getattr(args, f) for f in PCBParams.__dataclass_fields__})

    if args.gui:
        PCBGmshGUI(params).run()
        return

    script = generate_geo(params)
    output_path = Path(args.output)
    output_path.write_text(script)
    print(f"Gmsh script written to {output_path}")
    mesh_needed = args.mesh or args.elmergrid
    if mesh_needed:
        mesh_path = run_gmsh(str(output_path), output_path.parent)
        if args.elmergrid:
            output = run_elmer_grid(str(mesh_path), args.elmer_exe or None)
            if output.strip():
                print("ElmerGrid output:\n" + output)
    elif args.open:
        open_gmsh_with_file(str(output_path))


if __name__ == "__main__":
    main()

import argparse
from pathlib import Path

from config import PCBParams
from gmsh_generator import generate_geo
from gui import PCBGmshGUI
from utils import open_gmsh_with_file, run_gmsh_batch


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
    parser.add_argument("-o", "--output", default="pcb_model.geo", help="Output .geo file")
    parser.add_argument("--open", action="store_true", help="Open the result in Gmsh")
    parser.add_argument(
        "--mesh",
        action="store_true",
        help="Run Gmsh in batch mode to generate the mesh without opening the GUI",
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
    if args.mesh:
        run_gmsh_batch(str(output_path))
    elif args.open:
        open_gmsh_with_file(str(output_path))


if __name__ == "__main__":
    main()

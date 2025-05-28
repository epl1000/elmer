from dataclasses import dataclass

@dataclass
class PCBParams:
    ground_size: float = 10.0
    ground_thickness: float = 0.035
    separation: float = 0.15
    trace_thickness: float = 0.035
    trace_width: float = 0.2
    trace_length: float = 9.8
    via_width: float = 0.2
    via_depth: float = 0.2
    guard_via_width: float = 0.2
    sphere_radius: float = 20.0
    cut_width: float = 1.0
    cut_height: float = 1.0
    mesh_size_min: float = 0.05
    mesh_size_max: float = 2.0

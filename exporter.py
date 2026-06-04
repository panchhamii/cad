

from pathlib import Path
import cadquery as cq


def export_step(shape: cq.Workplane, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(output_path))

    bb = shape.val().BoundingBox()
    x: float = round(bb.xmax - bb.xmin, 2)
    y: float = round(bb.ymax - bb.ymin, 2)
    z: float = round(bb.zmax - bb.zmin, 2)

    print(f"  [DIMENSIONS]")
    print(f"    X (length) : {x} mm")
    print(f"    Y (width)  : {y} mm")
    print(f"    Z (height) : {z} mm")
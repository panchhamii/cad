"""
exporter.py
───────────
Handles exporting a CadQuery shape to a STEP file.

Also prints the bounding box dimensions of the exported shape
so the user can verify the output matches what they described.

Why STEP instead of STL?
STEP (Standard for the Exchange of Product model data) is an
industry-standard format used in professional CAD workflows.
It preserves exact geometry unlike STL which approximates with triangles.
"""

from pathlib import Path
import cadquery as cq


def export_step(shape: cq.Workplane, output_path: Path) -> None:
    """
    Export a CadQuery Workplane object to a STEP file and print dimensions.

    The output directory is created automatically if it does not exist.
    After export, the bounding box of the shape is printed so the user
    can verify the dimensions match the input description.

    Args:
        shape:       CadQuery Workplane object containing the final geometry
        output_path: Full path where the .step file should be saved

    Returns:
        None
    """
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export to STEP format
    cq.exporters.export(shape, str(output_path))

    # Print bounding box for dimension verification
    bb = shape.val().BoundingBox()
    x: float = round(bb.xmax - bb.xmin, 2)
    y: float = round(bb.ymax - bb.ymin, 2)
    z: float = round(bb.zmax - bb.zmin, 2)

    print(f"  [DIMENSIONS]")
    print(f"    X (length) : {x} mm")
    print(f"    Y (width)  : {y} mm")
    print(f"    Z (height) : {z} mm")
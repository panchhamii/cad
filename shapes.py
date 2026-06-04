
import re
import textwrap
from typing import Optional


def is_cone_request(description: str) -> bool:
    keywords: list[str] = ["cone", "conical"]
    return any(kw in description.lower() for kw in keywords)


def extract_cone_dimensions(description: str, llm_code: str) -> tuple[float, float]:
    radius_match = re.search(
        r'base\s+radius\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*mm', description, re.IGNORECASE
    ) or re.search(
        r'radius\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*mm', description, re.IGNORECASE
    )
    height_match = re.search(
        r'height\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*mm', description, re.IGNORECASE
    ) or re.search(
        r'(\d+(?:\.\d+)?)\s*mm\s+(?:tall|high)', description, re.IGNORECASE
    )

    base_r: Optional[float] = float(radius_match.group(1)) if radius_match else None
    height: Optional[float] = float(height_match.group(1)) if height_match else None

    if base_r is None or height is None:
        for line in llm_code.splitlines():
            line = line.strip()
            if re.match(r'^(base_r|base_radius|radius|r)\s*=\s*[\d.]+', line) and base_r is None:
                base_r = float(re.search(r'[\d.]+', line.split('=')[1]).group())
            if re.match(r'^(height|h)\s*=\s*[\d.]+', line) and height is None:
                height = float(re.search(r'[\d.]+', line.split('=')[1]).group())

    return base_r or 25.0, height or 50.0


def build_cone_code(base_r: float, height: float) -> str:
    return textwrap.dedent(f"""
        import cadquery as cq
        base_r = {base_r}
        height = {height}
        result = (
            cq.Workplane("XZ")
            .moveTo(0, 0)
            .lineTo(base_r, 0)
            .lineTo(0, height)
            .close()
            .revolve(360, (0, 0), (0, 1))
        )
    """).strip()
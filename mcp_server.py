import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CAD Viewer")

@mcp.tool()
def view_step_file(file_path: str) -> str:
    """Opens a STEP file in FreeCAD for viewing"""
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"
    
    subprocess.Popen([
        "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD",
        str(path)
    ])
    return f"Opened {path.name} in FreeCAD"

if __name__ == "__main__":
    mcp.run()
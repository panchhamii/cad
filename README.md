# LLM-Driven Parametric CAD Generation
**Problem Statement 2 — UST Automotive Data Science Internship, June 2026**
Panchami SV | panchami2004@gmail.com | [GitHub](https://github.com/panchhamii/cad)

---

## What I Built

A command-line tool that takes a plain English description of a 3D object and generates a valid STEP file using an LLM-powered pipeline. The system uses Groq's LLaMA 3.3-70b model to generate CadQuery Python code from natural language, executes it, and exports the result as a STEP file. A MCP (Model Context Protocol) server handles automatic viewing of the generated file in FreeCAD.

This is **Option A: Natural Language to CadQuery Script**.



## Project Structure

```
cadust/
├── main.py          # CLI entry point
├── pipeline.py      # Orchestrator — retry loop, flow control
├── llm.py           # Groq API client, conversation history
├── codegen.py       # Code extraction, syntax validation, exec()
├── shapes.py        # Cone special case — known-correct revolve template
├── exporter.py      # STEP export with bounding box verification
├── config.py        # Constants, model settings, system prompt
├── mcp_server.py    # MCP server — opens STEP file in FreeCAD
├── outputs/         # Generated STEP files saved here
└── .env             # GROQ_API_KEY (never committed)
```

---

## Setup

### Requirements
- Python 3.11+
- FreeCAD (for MCP viewer) — download from freecad.org

### Install

```bash
# Clone the repo
git clone https://github.com/panchhamii/cad.git
cd cad

# Create and activate virtual environment
python3.11 -m venv venv311
source venv311/bin/activate

# Install dependencies
pip install cadquery groq python-dotenv mcp
```

### Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

---

## How to Run

```bash
python main.py --prompt "Create a hollow cylinder with outer diameter 40mm, inner diameter 20mm, height 15mm"
```

The STEP file is saved to `outputs/` and opens automatically in FreeCAD.

---

## Example Runs



### 1. Rectangular Base Plate with Corner Holes
```bash
python main.py --prompt "Create a rectangular plate 80mm x 40mm x 8mm with four corner holes of diameter 5mm"
```
Output: `outputs/rectangular_plate_80mm_40mm_8mm.step`
Dimensions: X=80mm Y=40mm Z=8mm

---

### 2. Cycloidal Gear
```bash
python main.py --prompt "Create a cycloidal gear with 6 teeth, thickness 15mm, and a center hole of radius 2mm"
```
Output: `outputs/cycloidal_gear_6_teeth_15mm.step`
Dimensions: X=20mm Y=20mm Z=15mm

---

### 3. Solid Cone
```bash
python main.py --prompt "Create a solid cone with base radius 25mm and height 50mm"
```
Output: `outputs/solid_cone_base_radius_25mm.step`
Dimensions: X=50mm Y=50mm Z=50mm

---

### 4. Helical Spring
```bash
python main.py --prompt "Create a helical spring with wire diameter 3mm, coil radius 15mm, pitch 6mm, and height 60mm"
```
Output: `outputs/helical_spring_wire_diameter_3mm.step`
Dimensions verified via bounding box on export.

---

## MCP Viewer

After each successful generation, the STEP file is automatically opened in FreeCAD via an MCP tool. The `mcp_server.py` exposes a `view_step_file` tool that launches FreeCAD with the output file path.

Once FreeCAD opens, press **V then F** to fit the shape to the view if it does not appear immediately.

---

## Assumptions

- `GROQ_API_KEY` is set in `.env` — never hardcoded
- Internet connection required — Groq is a cloud API
- Python 3.11 required — CadQuery does not support Python 3.14+
- FreeCAD installed at `/Applications/FreeCAD.app` (macOS)
- CadQuery installed via pip — no external CAD software required for generation

---

## What Works

- Standard geometric shapes: box, cylinder, sphere
- Hollow shapes using `cutThruAll()`
- Plates with corner holes
- Solid and hollow cones via revolve template
- Helical springs via `makeHelix` and `sweep`
- Cycloidal gears via `parametricCurve`
- Self-correcting retry loop — LLM sees its own error and fixes it
- Automatic STEP viewer via MCP + FreeCAD

## What Does Not Work Reliably

- Bevel gears — cone-surface tooth profile requires `cq_gears` library
- Organic or freeform shapes — no CadQuery pattern exists
- Multi-part assemblies with constraints
- Very complex compound shapes often fail even after retries

---

## What I Would Improve With More Time

- Switch to a local Ollama model once a CadQuery-fine-tuned version is available, removing the cloud dependency
- Add geometry validation post-export using `trimesh` to verify watertight mesh
- Replace `exec()` with sandboxed subprocess execution for safety
- Add bevel gear support via `cq_gears` as a special case like cones
- Broader system prompt examples covering T-slots, threads, and bracket shapes
- Proper MCP integration with a parts database to look up standard dimensions

---

## Known Limitations

- Groq API is an online dependency — offline execution is not currently supported
- `exec()` is used to run generated code — acceptable for a prototype but not production-safe
- The LLM occasionally generates incorrect geometry for complex shapes; the retry loop handles most cases but not all
- FreeCAD viewer path is hardcoded for macOS

---


# LLM-Driven Parametric CAD Generation
**UST Automotive Data Science Internship — Problem Statement 2**

## What This Does
Converts a plain English description of a 3D object into a working CadQuery Python script,
executes it, and exports the result as an STL file.

Example:
> "Create a hollow cylinder with outer diameter 40mm, inner diameter 20mm, height 15mm"
→ Generates Python code → Runs it → Saves `outputs/hollow_cylinder.stl`

## Setup

```bash
pip install cadquery groq
export GROQ_API_KEY=your_key_here   #
```

## Usage



# Single custom prompt
python main.py --prompt "Create a solid box 60mm x 30mm x 20mm" --output my_box


```

## How It Works
1. Your text description is sent to LLaMA 3.1 70B (via Groq API)
2. The model generates a CadQuery Python script
3. The script is syntax-checked (ast.parse) before execution
4. CadQuery executes the script and captures the `result` shape
5. The shape is exported as an STL file to the `outputs/` folder
6. If execution fails, the error is sent back to the LLM for self-correction (up to 2 retries)

## Assumptions
- Inputs are in English with explicit dimensions in mm
- Targets simple geometric primitives (cylinders, boxes, cones, plates with holes)
- Groq API requires internet connection

## Known Limitations
- Very complex or abstract shapes may fail after retries
- Does not validate geometric constraints (e.g. inner_d < outer_d)
- STL output requires a separate viewer (e.g. MeshLab, Windows 3D Viewer)

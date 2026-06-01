"""
pipeline.py
───────────
The main orchestrator that connects all components into one pipeline.

Flow:
    User description
        → [shapes.py]   check if special-case shape (e.g. cone)
        → [llm.py]      call Groq LLM to generate CadQuery code
        → [codegen.py]  extract code, validate syntax, execute
        → [exporter.py] export to STEP file
        → return result dict

The retry loop feeds execution errors back to the LLM so it can
self-correct — up to MAX_RETRIES times before giving up.
"""

import time
from pathlib import Path

from config import MAX_RETRIES, OUTPUT_DIR
from llm import get_ollama_client, call_llm
from codegen import extract_code, validate_syntax, execute_cad_script
from exporter import export_step
from shapes import is_cone_request, extract_cone_dimensions, build_cone_code


def generate_cad(
    description: str,
    output_name: str = "output",
    verbose: bool = True,
) -> dict:
    """
    Full pipeline: natural language description → STEP file.

    For cone shapes, the LLM is called once for dimension extraction,
    then a known-correct revolve template is used instead of the LLM code.

    For all other shapes, the LLM generates the full CadQuery script.
    If execution fails, the error is sent back to the LLM for correction.

    Args:
        description: Natural language description of the 3D object
        output_name: Base filename for the output STEP file (no extension)
        verbose:     If True, print progress and results to stdout

    Returns:
        dict with keys:
            success   (bool)        — True if STEP file was created
            code      (str)         — Final CadQuery code that was executed
            step_path (str | None)  — Path to the saved STEP file
            error     (str)         — Error message if failed
            attempts  (int)         — Number of LLM calls made
    """
    client = get_ollama_client()
    conversation: list[dict] = []

    result: dict = {
        "success": False,
        "code": "",
        "step_path": None,
        "error": "",
        "attempts": 0,
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Input: {description}")
        print(f"{'='*60}")

    # ── Cone fast-path: bypass LLM revolve output ──────────────
    # The LLM often generates wrong revolve() axis for cones.
    # We call the LLM once only to help extract dimensions,
    # then discard its code and use our known-correct template.
    if is_cone_request(description):
        if verbose:
            print("\n[Cone detected] Using hardcoded revolve template...")

        raw = call_llm(client, description, conversation)
        llm_code = extract_code(raw)

        base_r, height = extract_cone_dimensions(description, llm_code)
        if verbose:
            print(f"  [Dimensions] base_r={base_r}mm  height={height}mm")

        code = build_cone_code(base_r, height)
        result["code"] = code
        result["attempts"] = 1

        return _execute_and_export(code, output_name, result, verbose)

    # ── Normal LLM path for all other shapes ──────────────────
    for attempt in range(1, MAX_RETRIES + 2):
        result["attempts"] = attempt

        if verbose:
            print(f"\n[Attempt {attempt}] Calling LLM...", end=" ", flush=True)

        t0: float = time.time()

        # On first attempt send the description; on retries send the error
        if attempt == 1:
            prompt = description
        else:
            prompt = (
                f"The code you generated failed with this error:\n{result['error']}\n\n"
                f"Please fix the code and output the corrected version only."
            )

        raw = call_llm(client, prompt, conversation)
        elapsed: float = time.time() - t0

        if verbose:
            print(f"done ({elapsed:.1f}s)")

        code = extract_code(raw)
        result["code"] = code

        # Step 1: syntax check before execution
        is_valid, syntax_err = validate_syntax(code)
        if not is_valid:
            result["error"] = syntax_err
            if verbose:
                print(f"  [SYNTAX ERROR] {syntax_err}")
            continue

        # Step 2: execute and export
        if verbose:
            print("  [Executing CadQuery script]...", end=" ", flush=True)

        result = _execute_and_export(code, output_name, result, verbose)

        if result["success"]:
            break

    if not result["success"] and verbose:
        print(f"\n  [FAILED after {result['attempts']} attempts] {result['error']}")

    return result


def _execute_and_export(
    code: str,
    output_name: str,
    result: dict,
    verbose: bool,
) -> dict:
    """
    Execute the CadQuery script and export to STEP if successful.

    This is a shared helper used by both the cone fast-path and the
    normal LLM retry loop to avoid duplicating the execute + export logic.

    Args:
        code:        CadQuery Python code to execute
        output_name: Base filename for the STEP output
        result:      Current result dict (updated in-place and returned)
        verbose:     Whether to print progress

    Returns:
        dict: Updated result dict
    """
    success, shape, exec_err = execute_cad_script(code)

    if not success:
        result["error"] = exec_err
        if verbose:
            print(f"FAILED\n  [EXEC ERROR] {exec_err}")
        return result

    step_path: Path = OUTPUT_DIR / f"{output_name}.step"
    try:
        export_step(shape, step_path)
        result["success"] = True
        result["step_path"] = str(step_path)
        result["error"] = ""
        if verbose:
            print("OK")
            print(f"  [SUCCESS] STEP saved → {step_path}")
    except Exception as e:
        result["error"] = f"STEP export failed: {e}"
        if verbose:
            print(f"FAILED\n  [EXPORT ERROR] {e}")

    return result
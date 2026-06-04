

import time
from mcp_server import view_step_file
from pathlib import Path

from config import MAX_RETRIES, OUTPUT_DIR
from llm import get_groq_client, call_llm
from codegen import extract_code, validate_syntax, execute_cad_script
from exporter import export_step
from shapes import is_cone_request, extract_cone_dimensions, build_cone_code


def _make_output_name(description: str) -> str:
    words = description.lower().replace(",", "").replace(".", "").split()
    keywords = [w for w in words if w not in ("create", "a", "an", "the", "with", "and", "of")]
    return "_".join(keywords[:4]) or "output"


def generate_cad(
    description: str,
    output_name: str = "",
    verbose: bool = True,
) -> dict:
    if not output_name:
        output_name = _make_output_name(description)

    client = get_groq_client()
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

    if is_cone_request(description):
        if verbose:
            print("\n[Cone detected] Using revolve template...")

        raw = call_llm(client, description, conversation)
        llm_code = extract_code(raw)
        base_r, height = extract_cone_dimensions(description, llm_code)

        if verbose:
            print(f"  [Dimensions] base_r={base_r}mm  height={height}mm")

        code = build_cone_code(base_r, height)
        result["code"] = code
        result["attempts"] = 1

        return _execute_and_export(code, output_name, result, verbose)

    for attempt in range(1, MAX_RETRIES + 2):
        result["attempts"] = attempt

        if verbose:
            print(f"\n[Attempt {attempt}] Calling LLM...", end=" ", flush=True)

        t0: float = time.time()
        prompt = description if attempt == 1 else (
            f"The code you generated failed with this error:\n{result['error']}\n\n"
            f"Please fix the code and output the corrected version only."
        )

        raw = call_llm(client, prompt, conversation)

        if verbose:
            print(f"done ({round(time.time() - t0, 1)}s)")

        code = extract_code(raw)
        result["code"] = code

        is_valid, syntax_err = validate_syntax(code)
        if not is_valid:
            result["error"] = syntax_err
            if verbose:
                print(f"  [SYNTAX ERROR] {syntax_err}")
            continue

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
        view_step_file(str(step_path))
    except Exception as e:
        result["error"] = f"STEP export failed: {e}"
        if verbose:
            print(f"FAILED\n  [EXPORT ERROR] {e}")

    return result
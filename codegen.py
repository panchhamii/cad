"""
codegen.py
──────────
Handles everything between receiving LLM output and running it as Python.

Three steps in order:
1. extract_code  — strip markdown fences the LLM may have added
2. validate_syntax — check for Python syntax errors before executing
3. execute_cad_script — run the code and capture the `result` variable
"""

import ast


def extract_code(raw_response: str) -> str:
    """
    Strip markdown code fences from the LLM response if present.

    The LLM is instructed not to use fences, but sometimes adds them anyway.
    This function handles both cases safely.

    Example input:
        ```python
        import cadquery as cq
        result = cq.Workplane("XY").box(10, 10, 10)
        ```

    Example output:
        import cadquery as cq
        result = cq.Workplane("XY").box(10, 10, 10)

    Args:
        raw_response: Raw string returned by the LLM

    Returns:
        str: Clean Python code with no markdown fences
    """
    lines = raw_response.splitlines()
    cleaned: list[str] = []
    inside_fence: bool = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            inside_fence = not inside_fence
            continue
        cleaned.append(line)

    return "\n".join(cleaned).strip()


def validate_syntax(code: str) -> tuple[bool, str]:
    """
    Check Python syntax of the generated code without executing it.

    Uses Python's built-in ast.parse() which catches SyntaxErrors
    before we risk running bad code through exec().

    Args:
        code: Python source code string to validate

    Returns:
        tuple[bool, str]:
            - True, ""               if syntax is valid
            - False, error_message   if a SyntaxError was found
    """
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"


def execute_cad_script(code: str) -> tuple[bool, object, str]:
    """
    Execute the generated CadQuery script in an isolated namespace.

    The script must define a variable called `result` which holds
    the final CadQuery Workplane object. This is then passed to
    the exporter.

    Why exec()? The LLM generates code dynamically at runtime —
    there is no other way to run it. The isolated namespace dict
    prevents the generated code from touching the main program.

    Args:
        code: Valid Python code using CadQuery

    Returns:
        tuple[bool, object, str]:
            - True, shape, ""          on success
            - False, None, error_msg   on failure
    """
    namespace: dict = {}
    try:
        exec(compile(code, "<generated>", "exec"), namespace)

        if "result" not in namespace:
            return False, None, "Code did not define a variable named `result`"

        shape = namespace["result"]
        return True, shape, ""

    except Exception as e:
        return False, None, f"{type(e).__name__}: {e}"
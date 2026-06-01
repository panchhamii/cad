"""
codegen.py — Code extraction, syntax validation, and execution.
"""

import ast


def extract_code(raw_response: str) -> str:
    lines = raw_response.splitlines()
    cleaned: list[str] = []
    inside_fence: bool = False

    for line in lines:
        if line.strip().startswith("```"):
            inside_fence = not inside_fence
            continue
        cleaned.append(line)

    return "\n".join(cleaned).strip()


def validate_syntax(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"


def execute_cad_script(code: str) -> tuple[bool, object, str]:
    namespace: dict = {}
    try:
        exec(compile(code, "<generated>", "exec"), namespace)
        if "result" not in namespace:
            return False, None, "Code did not define a variable named `result`"
        return True, namespace["result"], ""
    except Exception as e:
        return False, None, f"{type(e).__name__}: {e}"
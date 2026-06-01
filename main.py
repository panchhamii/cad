"""
main.py
───────
Command-line entry point for the LLM-Driven Parametric CAD Generator.

This file only handles argument parsing and calling the pipeline.
All actual logic lives in the other modules:
    config.py   — settings and system prompt
    llm.py      — Groq API client and LLM calls
    codegen.py  — code extraction, validation, execution
    shapes.py   — special-case shape handlers (e.g. cone)
    exporter.py — STEP file export
    pipeline.py — main orchestrator

Usage:
    python main.py --prompt "Create a hollow cylinder with outer diameter 40mm, inner diameter 20mm, height 15mm"
    python main.py                         (interactive mode)
    python main.py --prompt "..." --output my_shape
"""

import argparse
from pipeline import generate_cad


def run_interactive() -> None:
    """Run in interactive mode — accept prompts from the user one by one."""
    print("\n LLM-Driven Parametric CAD Generator")
    print("   Type a description or 'quit' to exit.\n")
    counter: int = 1

    while True:
        try:
            desc = input("Enter description: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if desc.lower() in ("quit", "exit", "q"):
            break

        if desc:
            generate_cad(desc, output_name=f"shape_{counter}")
            counter += 1


def main() -> None:
    """Parse CLI arguments and run the appropriate mode."""
    parser = argparse.ArgumentParser(
        description="LLM-Driven Parametric CAD Generator — UST Internship Problem 2"
    )
    parser.add_argument(
        "--prompt", type=str,
        help="Natural language description of the 3D object to generate"
    )
    parser.add_argument(
        "--output", type=str, default="output",
        help="Output filename without extension (default: output)"
    )
    args = parser.parse_args()

    if args.prompt:
        generate_cad(args.prompt, output_name=args.output)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
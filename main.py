
import argparse
from pipeline import generate_cad


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LLM-Driven Parametric CAD Generator — UST Internship Problem 2"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Natural language description of the 3D object to generate"
    )
    args = parser.parse_args()
    generate_cad(args.prompt)


if __name__ == "__main__":
    main()
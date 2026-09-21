"""Guardian Benchmark CLI: python -m guardian.benchmark"""

import argparse

from guardian.benchmark import run_experiments


def main():
    parser = argparse.ArgumentParser(description="Guardian Benchmark Runner")
    parser.add_argument("--data-dir", required=True, help="Path to RCAEval data")
    parser.add_argument(
        "--experiments", nargs="+", default=["e1", "e2"],
        help="Experiments to run: e1 e2 e3 e4 e5",
    )
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--classify-method", default="rule", choices=["rule", "llm"])
    parser.add_argument("--max-cases", type=int, default=None)

    args = parser.parse_args()
    run_experiments(
        data_dir=args.data_dir,
        experiments=args.experiments,
        output_dir=args.output_dir,
        classify_method=args.classify_method,
        max_cases=args.max_cases,
    )


if __name__ == "__main__":
    main()

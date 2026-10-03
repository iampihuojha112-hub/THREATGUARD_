"""SMS training: same TF-IDF + model-comparison pipeline as email, with the SMS loader and its own output folder."""
from __future__ import annotations

import argparse
import sys

from ml.training.pipeline import AVAILABLE_MODELS, run
from ml.training.sms_dataset import load_sms_dataset


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train ThreatGuard SMS scam detection models.")
    parser.add_argument("--data", required=True, help="Path to CSV/TSV with columns: message,label")
    parser.add_argument("--output-dir", default="models/sms")
    parser.add_argument("--models", nargs="+", default=AVAILABLE_MODELS, choices=AVAILABLE_MODELS)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-features", type=int, default=20000)
    parser.add_argument("--min-df", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        run(args.data, args.output_dir, args.models, args.test_size, args.seed, args.max_features, args.min_df, loader=load_sms_dataset)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

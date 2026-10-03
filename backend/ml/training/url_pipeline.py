"""URL training: load -> feature engineering -> train -> evaluate -> select -> save.

Evaluation, model construction and plotting are reused from the email pipeline.
Logistic Regression is wrapped with log1p + standard scaling because URL counts are heavy-tailed.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from ml.inference.url_audit import check_orientation, print_probe_report
from ml.preprocessing.url import FEATURE_NAMES, FEATURE_VERSION, feature_vector
from ml.training.pipeline import AVAILABLE_MODELS, build_models, evaluate, save_confusion_matrix
from ml.training.url_dataset import load_url_dataset


def _log1p(x):
    return np.log1p(np.clip(x, 0, None))


def run(
    data_path: str,
    output_dir: str = "models/url",
    models: list[str] | None = None,
    test_size: float = 0.2,
    seed: int = 42,
    invert_labels: bool = False,
    skip_label_check: bool = False,
) -> dict:
    models = models or AVAILABLE_MODELS
    out = Path(output_dir)
    reports = out / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    df, x, y = load_url_dataset(data_path, invert_labels=invert_labels, skip_label_check=skip_label_check)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, stratify=y, random_state=seed)
    print(f"[split] stratified holdout, seed {seed}: train {len(y_train):,} rows "
          f"(legit {int((y_train == 0).sum()):,} / malicious {int((y_train == 1).sum()):,}) | "
          f"test {len(y_test):,} rows (legit {int((y_test == 0).sum()):,} / malicious {int((y_test == 1).sum()):,})")

    pos_weight = float((y_train == 0).sum() / max(1, (y_train == 1).sum()))
    estimators = build_models(models, seed, pos_weight)
    if "logistic_regression" in estimators:
        estimators["logistic_regression"] = Pipeline([
            ("log", FunctionTransformer(_log1p, feature_names_out="one-to-one")),
            ("scale", StandardScaler()),
            ("clf", estimators["logistic_regression"]),
        ])

    results: dict[str, dict] = {}
    fitted: dict = {}
    for name, estimator in estimators.items():
        print(f"[train] fitting {name} ...")
        estimator.fit(x_train, y_train)
        if list(estimator.classes_) != [0, 1]:
            raise RuntimeError(f"{name}: unexpected class order {list(estimator.classes_)}; predict_proba column 1 must be label 1 (malicious)")
        metrics, cm, report = evaluate(estimator, x_test, y_test)
        results[name] = metrics
        fitted[name] = estimator
        save_confusion_matrix(cm, name, reports / f"confusion_matrix_{name}.png")
        (reports / f"classification_report_{name}.txt").write_text(report)
        tn, fp, fn, tp = (int(v) for v in cm.ravel())
        print(f"\n== {name} (evaluated on the {len(y_test):,}-row holdout) ==\n{report}")
        print("confusion matrix (rows = actual, columns = predicted):")
        print(f"pred legit   pred malicious\n    actual legit    {tn:>10,}   {fp:>14,}   (TN, FP)\n    actual malicious{fn:>10,}   {tp:>14,}   (FN, TP)\n")

    best_name = max(results, key=lambda n: (results[n]["f1"], results[n]["roc_auc"], results[n]["recall"]))

    print("[compare]")
    print(f"{'model':<22}{'accuracy':>10}{'precision':>11}{'recall':>9}{'f1':>8}{'roc_auc':>10}")
    for name, m in results.items():
        mark = "  <- best" if name == best_name else ""
        print(f"{name:<22}{m['accuracy']:>10.4f}{m['precision']:>11.4f}{m['recall']:>9.4f}{m['f1']:>8.4f}{m['roc_auc']:>10.4f}{mark}")

    # Per-feature class statistics (log1p space) used by the explainer for tree models.
    lx = _log1p(x_train.astype(np.float64))
    stats = {
        "legit_mean": lx[y_train == 0].mean(axis=0),
        "phish_mean": lx[y_train == 1].mean(axis=0),
        "std": lx.std(axis=0) + 1e-9,
    }
    best = fitted[best_name]
    probes = check_orientation(lambda u: float(best.predict_proba(np.asarray([feature_vector(u)], dtype=np.float64))[0][1]))
    print_probe_report(probes)

    joblib.dump(best, out / "model.pkl")
    joblib.dump(stats, out / "feature_stats.pkl")

    metadata = {
        "best_model": best_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(data_path),
        "rows": int(len(df)),
        "test_size": test_size,
        "seed": seed,
        "sklearn_version": sklearn.__version__,
        "feature_names": FEATURE_NAMES,
        "feature_version": FEATURE_VERSION,
        "label_encoding": {"0": "legitimate", "1": "malicious"},
        "labels_inverted_at_load": invert_labels,
        "probe_verdict": probes["verdict"],
        "metrics": results,
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (reports / "model_comparison.json").write_text(json.dumps(results, indent=2))
    print(f"\n[save] {out / 'model.pkl'} ({best_name})\n[save] {out / 'feature_stats.pkl'}")
    return metadata


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train ThreatGuard malicious URL detection models.")
    parser.add_argument("--data", required=True, help="Path to CSV/TSV with columns: url,label")
    parser.add_argument("--output-dir", default="models/url")
    parser.add_argument("--models", nargs="+", default=AVAILABLE_MODELS, choices=AVAILABLE_MODELS)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--invert-labels", action="store_true", help="Use when the dataset encodes 1 = legitimate and 0 = malicious")
    parser.add_argument("--skip-label-check", action="store_true", help="Train even if labels look reversed")
    args = parser.parse_args(argv)
    try:
         run(args.data, args.output_dir, args.models, args.test_size, args.seed, args.invert_labels, args.skip_label_check)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    main()

"""Training pipeline: load -> preprocess -> TF-IDF -> train -> evaluate -> select -> save."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import sklearn  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split  # noqa: E402

from ml.training.dataset import load_dataset  # noqa: E402

try:
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover
    XGBClassifier = None

AVAILABLE_MODELS = ["logistic_regression", "random_forest", "xgboost"]
CLASS_NAMES = ["Legitimate", "Phishing"]


def build_models(selected: list[str], seed: int, pos_weight: float) -> dict:
    models: dict = {}
    for name in selected:
        if name == "logistic_regression":
            models[name] = LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced", solver="liblinear", random_state=seed)
        elif name == "random_forest":
            models[name] = RandomForestClassifier(n_estimators=300, class_weight="balanced_subsample", n_jobs=-1, random_state=seed)
        elif name == "xgboost":
            if XGBClassifier is None:
                raise RuntimeError("xgboost is not installed. Run: pip install -r requirements.txt")
            models[name] = XGBClassifier(
                n_estimators=400, max_depth=6, learning_rate=0.1, subsample=0.9, colsample_bytree=0.8,
                scale_pos_weight=pos_weight, eval_metric="logloss", n_jobs=-1, random_state=seed, tree_method="hist",
            )
        else:
            raise ValueError(f"Unknown model '{name}'. Choose from {AVAILABLE_MODELS}")
    return models


def evaluate(model, x_test, y_test) -> tuple[dict, np.ndarray, str]:
    pred = model.predict(x_test)
    proba = model.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
    }
    cm = confusion_matrix(y_test, pred, labels=[0, 1])
    report = classification_report(y_test, pred, labels=[0, 1], target_names=CLASS_NAMES, zero_division=0)
    return metrics, cm, report


def save_confusion_matrix(cm: np.ndarray, name: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    ax.imshow(cm, cmap="Purples")
    ax.set_xticks([0, 1], CLASS_NAMES)
    ax.set_yticks([0, 1], CLASS_NAMES)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion matrix: {name}")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def run(
    data_path: str,
    output_dir: str = "models",
    models: list[str] | None = None,
    test_size: float = 0.2,
    seed: int = 42,
    max_features: int = 30000,
    min_df: int = 2,
    loader=None,
) -> dict:
    """`loader` lets other text modules (SMS) reuse this pipeline; it must return a frame with `text` and `label`."""
    models = models or AVAILABLE_MODELS
    out = Path(output_dir)
    reports = out / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    df = (loader or load_dataset)(data_path)
    x_train_txt, x_test_txt, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=test_size, stratify=df["label"], random_state=seed
    )

    tfidf = TfidfVectorizer(
        max_features=max_features, ngram_range=(1, 2), min_df=min_df, max_df=0.95, sublinear_tf=True, dtype=np.float32
    )
    x_train = tfidf.fit_transform(x_train_txt)
    x_test = tfidf.transform(x_test_txt)
    print(f"[tfidf] vocabulary size: {len(tfidf.vocabulary_)}")

    pos_weight = float((y_train == 0).sum() / max(1, (y_train == 1).sum()))
    estimators = build_models(models, seed, pos_weight)

    results: dict[str, dict] = {}
    fitted: dict = {}
    for name, estimator in estimators.items():
        print(f"[train] fitting {name} ...")
        estimator.fit(x_train, y_train)
        metrics, cm, report = evaluate(estimator, x_test, y_test)
        results[name] = metrics
        fitted[name] = estimator
        save_confusion_matrix(cm, name, reports / f"confusion_matrix_{name}.png")
        (reports / f"classification_report_{name}.txt").write_text(report)
        print(f"\n== {name} ==\n{report}\nconfusion matrix:\n{cm}\n")

    best_name = max(results, key=lambda n: (results[n]["f1"], results[n]["roc_auc"], results[n]["recall"]))
    best_model = fitted[best_name]

    print("[compare]")
    print(f"{'model':<22}{'accuracy':>10}{'precision':>11}{'recall':>9}{'f1':>8}{'roc_auc':>10}")
    for name, m in results.items():
        mark = "  <- best" if name == best_name else ""
        print(f"{name:<22}{m['accuracy']:>10.4f}{m['precision']:>11.4f}{m['recall']:>9.4f}{m['f1']:>8.4f}{m['roc_auc']:>10.4f}{mark}")

    # Direction of each term: positive = leans phishing. Used by the explainer for tree models.
    y_arr = y_train.to_numpy()
    phish_mean = np.asarray(x_train[y_arr == 1].mean(axis=0)).ravel()
    legit_mean = np.asarray(x_train[y_arr == 0].mean(axis=0)).ravel()
    term_direction = (phish_mean - legit_mean).astype(np.float32)

    joblib.dump(best_model, out / "model.pkl")
    joblib.dump(tfidf, out / "tfidf.pkl")
    joblib.dump(term_direction, out / "term_direction.pkl")

    metadata = {
        "best_model": best_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(data_path),
        "rows": int(len(df)),
        "test_size": test_size,
        "seed": seed,
        "sklearn_version": sklearn.__version__,
        "metrics": results,
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (reports / "model_comparison.json").write_text(json.dumps(results, indent=2))
    print(f"\n[save] {out / 'model.pkl'} ({best_name})\n[save] {out / 'tfidf.pkl'}")
    return metadata


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train ThreatGuard phishing detection models.")
    parser.add_argument("--data", required=True, help="Path to CSV/TSV dataset")
    parser.add_argument("--output-dir", default="models")
    parser.add_argument("--models", nargs="+", default=AVAILABLE_MODELS, choices=AVAILABLE_MODELS)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-features", type=int, default=30000)
    parser.add_argument("--min-df", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        run(args.data, args.output_dir, args.models, args.test_size, args.seed, args.max_features, args.min_df)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

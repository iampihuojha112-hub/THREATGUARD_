"""URL dataset loader. Format: url,label  (0 = legitimate, 1 = malicious)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ml.preprocessing.url import FEATURE_NAMES, feature_vector
from ml.training.dataset import LABEL_MAP, _find

URL_ALIASES = ["url", "urls", "link", "domain", "website"]
URL_LABEL_ALIASES = ["label", "class", "target", "type", "result", "status"]
URL_LABEL_MAP = {
    **LABEL_MAP,
    "good": 0, "benign": 0, "clean": 0, "legit": 0,
    "bad": 1, "malware": 1, "defacement": 1, "phishing": 1, "malicious": 1, "suspicious": 1,
}

_SUSPICION_FEATURES = ["has_ip_host", "suspicious_tld", "is_shortener", "brand_mismatch", "has_at_symbol",
                       "has_punycode", "has_redirect_param", "executable_extension"]
_SUSPICION_IDX = [FEATURE_NAMES.index(n) for n in _SUSPICION_FEATURES]
_KEYWORD_IDX = FEATURE_NAMES.index("keyword_count")
_SCHEME_IDX = FEATURE_NAMES.index("has_https")


def _map_url_label(value) -> int | None:
    key = str(value).strip().lower()
    if key.endswith(".0"):
        key = key[:-2]
    return URL_LABEL_MAP.get(key)


def suspicion_score(x: np.ndarray) -> np.ndarray:
    """Per-row attack-likeness in [0, 1] from structural red flags (no learning involved)."""
    flags = x[:, _SUSPICION_IDX].clip(0, 1).sum(axis=1)
    keywords = np.minimum(x[:, _KEYWORD_IDX], 3) / 3.0
    return (flags + keywords) / (len(_SUSPICION_IDX) + 1)


def label_orientation_report(x: np.ndarray, y: np.ndarray) -> dict:
    s = suspicion_score(x)
    s0, s1 = float(s[y == 0].mean()), float(s[y == 1].mean())
    return {"legit_mean": s0, "malicious_mean": s1, "reversed": s0 > s1, "strongly_reversed": s0 > 1.5 * s1 + 0.02}


def load_url_dataset(
    path: str | Path,
    invert_labels: bool = False,
    skip_label_check: bool = False,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    raw = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, encoding_errors="replace")
    columns = {c.strip().lower().replace(" ", "_"): c for c in raw.columns}
    url_col = _find(columns, URL_ALIASES)
    label_col = _find(columns, URL_LABEL_ALIASES)
    if url_col is None or label_col is None:
        raise ValueError(f"Expected columns 'url,label'. Got {list(raw.columns)}")

    print(f"[url-dataset] label column '{label_col}': raw value -> encoded (0 = legitimate, 1 = malicious)")
    for value, count in raw[label_col].value_counts().items():
        code = _map_url_label(value)
        shown = "UNRECOGNISED (row dropped)" if code is None else ("legitimate (0)" if code == 0 else "malicious (1)")
        if invert_labels and code is not None:
            shown += "  [inverted by --invert-labels]"
        print(f"    {value!r:<18} {count:>9,} rows  ->  {shown}")

    df = pd.DataFrame({"url": raw[url_col].str.strip(), "label": raw[label_col].map(_map_url_label)})
    df = df.dropna(subset=["label"])
    df = df[df["url"].str.len() > 0]
    df["label"] = df["label"].astype(int)
    if invert_labels:
        df["label"] = 1 - df["label"]

    before = len(df)
    conflict = df.groupby("url")["label"].transform("nunique") > 1   # same URL under both labels: drop all copies
    if conflict.any():
        print(f"[url-dataset] Dropping {int(conflict.sum())} rows whose URL appears with conflicting labels")
        df = df[~conflict]
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)
    if before != len(df):
        print(f"[url-dataset] Removed {before - len(df)} duplicate or conflicting rows in total")

    counts = df["label"].value_counts().to_dict()
    if len(counts) < 2 or min(counts.values()) < 10:
        raise ValueError(f"Need at least 10 samples of each class. Class counts: {counts}")

    print(f"[url-dataset] extracting {len(FEATURE_NAMES)} features from {len(df)} URLs ...")
    x = np.asarray([feature_vector(u) for u in df["url"]], dtype=np.float32)
    y = df["label"].to_numpy()

    total = len(df)
    print("[url-dataset] label distribution before training:")
    print(f"    0 legitimate : {counts.get(0, 0):>9,}  ({counts.get(0, 0) / total:6.1%})")
    print(f"    1 malicious  : {counts.get(1, 0):>9,}  ({counts.get(1, 0) / total:6.1%})")
    ratio = max(counts.values()) / min(counts.values())
    if ratio >= 4:
        print(f"[url-dataset] NOTE: classes are imbalanced ({ratio:.1f}:1). Class weights are applied; judge models by recall/F1/ROC-AUC, not accuracy.")

    scheme = x[:, _SCHEME_IDX]
    s0, s1 = float(scheme[y == 0].mean()), float(scheme[y == 1].mean())
    print(f"[url-dataset] share of URLs starting with https: legitimate {s0:.1%} | malicious {s1:.1%}")
    if abs(s0 - s1) > 0.5:
        print("[url-dataset] WARNING: https presence differs sharply between classes. The model may learn how the dataset was collected "
              "instead of what makes a URL malicious. Normalise the scheme across both classes before training.")

    rep = label_orientation_report(x, y)
    print(f"[url-dataset] structural suspicion score (IP hosts, shorteners, bad TLDs, brand tricks ...): "
          f"class 0 = {rep['legit_mean']:.3f} | class 1 = {rep['malicious_mean']:.3f}")
    if rep["reversed"]:
        msg = ("Class 0 looks MORE suspicious than class 1, so the labels are probably reversed "
               "(some datasets use 1 = legitimate). Re-run with --invert-labels if so.")
        if rep["strongly_reversed"] and not skip_label_check:
            raise ValueError(msg + " Use --skip-label-check to train anyway.")
        print(f"[url-dataset] WARNING: {msg}")
    return df, x, y
"""Dataset loading for both supported schemas.

Schema A: subject, sender, body, label
Schema B: email_text, label
Labels: 0 = legitimate, 1 = phishing (common string labels are mapped automatically).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.preprocessing import preprocess_email

SUBJECT_ALIASES = ["subject", "email_subject", "title"]
SENDER_ALIASES = ["sender", "from", "from_email", "sender_email"]
BODY_ALIASES = ["body", "email_body", "message", "content"]
TEXT_ALIASES = ["email_text", "text", "email", "email_content", "text_combined"]
LABEL_ALIASES = ["label", "class", "target", "is_phishing", "email_type", "type"]

LABEL_MAP = {
    "0": 0, "legitimate": 0, "legit": 0, "safe": 0, "safe email": 0, "ham": 0, "benign": 0, "not phishing": 0,
    "1": 1, "phishing": 1, "phish": 1, "phishing email": 1, "spam": 1, "malicious": 1, "fraud": 1,
}


def _find(columns: dict[str, str], aliases: list[str]) -> str | None:
    for alias in aliases:
        if alias in columns:
            return columns[alias]
    return None


def _map_label(value) -> int | None:
    key = str(value).strip().lower()
    if key.endswith(".0"):
        key = key[:-2]
    return LABEL_MAP.get(key)


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Return a DataFrame with columns: subject, sender, body, label, text (preprocessed)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    raw = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, encoding_errors="replace")
    columns = {c.strip().lower().replace(" ", "_"): c for c in raw.columns}

    label_col = _find(columns, LABEL_ALIASES)
    if label_col is None:
        raise ValueError(f"No label column found. Expected one of {LABEL_ALIASES}. Got {list(raw.columns)}")

    subject_col = _find(columns, SUBJECT_ALIASES)
    sender_col = _find(columns, SENDER_ALIASES)
    body_col = _find(columns, BODY_ALIASES)
    text_col = _find(columns, TEXT_ALIASES)

    if body_col is None and text_col is None:
        raise ValueError(
            "No body/text column found. Provide (subject, sender, body, label) or (email_text, label)."
        )

    df = pd.DataFrame()
    df["subject"] = raw[subject_col] if subject_col else ""
    df["sender"] = raw[sender_col] if sender_col else ""
    df["body"] = raw[body_col] if body_col else raw[text_col]
    df["label"] = raw[label_col].map(_map_label)

    unknown = df["label"].isna().sum()
    if unknown:
        bad = raw.loc[df["label"].isna(), label_col].unique()[:10]
        print(f"[dataset] Dropping {unknown} rows with unrecognised labels, e.g. {list(bad)}")
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    df["text"] = [preprocess_email(s, b) for s, b in zip(df["subject"], df["body"])]
    df = df[df["text"].str.len() > 0]
    before = len(df)
    df = df.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)
    if before != len(df):
        print(f"[dataset] Removed {before - len(df)} duplicate rows")

    counts = df["label"].value_counts().to_dict()
    if len(counts) < 2 or min(counts.values()) < 10:
        raise ValueError(f"Need at least 10 samples of each class. Class counts: {counts}")
    print(f"[dataset] {len(df)} rows | legitimate={counts.get(0, 0)} phishing={counts.get(1, 0)}")
    return df

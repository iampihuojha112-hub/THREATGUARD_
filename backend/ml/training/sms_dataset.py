"""SMS dataset loader. Format: message,label  (0 = legitimate, 1 = scam/spam)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.preprocessing.sms import preprocess_sms
from ml.training.dataset import LABEL_ALIASES, _find, _map_label

MESSAGE_ALIASES = ["message", "sms", "text", "content", "body", "v2"]
SMS_LABEL_ALIASES = LABEL_ALIASES + ["v1", "category"]


def load_sms_dataset(path: str | Path) -> pd.DataFrame:
    """Return a DataFrame with columns: message, label, text (preprocessed)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    raw = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, encoding_errors="replace")
    columns = {c.strip().lower().replace(" ", "_"): c for c in raw.columns}

    label_col = _find(columns, SMS_LABEL_ALIASES)
    message_col = _find(columns, MESSAGE_ALIASES)
    if label_col is None or message_col is None:
        raise ValueError(f"Expected columns 'message,label'. Got {list(raw.columns)}")

    df = pd.DataFrame({"message": raw[message_col], "label": raw[label_col].map(_map_label)})
    unknown = int(df["label"].isna().sum())
    if unknown:
        bad = raw.loc[df["label"].isna(), label_col].unique()[:10]
        print(f"[sms-dataset] Dropping {unknown} rows with unrecognised labels, e.g. {list(bad)}")
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    df["text"] = [preprocess_sms(m) for m in df["message"]]
    df = df[df["text"].str.len() > 0]
    before = len(df)
    df = df.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)
    if before != len(df):
        print(f"[sms-dataset] Removed {before - len(df)} duplicate rows")

    counts = df["label"].value_counts().to_dict()
    if len(counts) < 2 or min(counts.values()) < 10:
        raise ValueError(f"Need at least 10 samples of each class. Class counts: {counts}")
    print(f"[sms-dataset] {len(df)} rows | legitimate={counts.get(0, 0)} scam={counts.get(1, 0)}")
    return df

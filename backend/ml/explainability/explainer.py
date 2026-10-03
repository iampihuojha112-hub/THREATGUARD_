"""Combine model-derived term contributions with rule-based signals."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
from sklearn.linear_model import LogisticRegression

from ml.explainability.rules import analyze_signals


def top_terms(model, tfidf, x_row, term_direction: np.ndarray | None, limit: int = 8) -> List[Dict]:
    """Return the vocabulary terms that influenced this prediction most.

    Logistic regression: signed contribution = tf-idf value * coefficient.
    Tree models: tf-idf value * feature importance, signed by the class lean of the term.
    """
    row = x_row.tocsr()
    if row.nnz == 0:
        return []
    idx = row.indices
    values = row.data
    names = tfidf.get_feature_names_out()

    if isinstance(model, LogisticRegression):
        contrib = values * model.coef_[0][idx]
    elif hasattr(model, "feature_importances_"):
        magnitude = values * model.feature_importances_[idx]
        if term_direction is not None:
            contrib = magnitude * np.sign(term_direction[idx])
        else:
            contrib = magnitude
    else:
        return []

    order = np.argsort(-np.abs(contrib))[:limit]
    out = []
    for i in order:
        if contrib[i] == 0:
            continue
        out.append({
            "term": str(names[idx[i]]),
            "weight": round(float(contrib[i]), 4),
            "direction": "phishing" if contrib[i] > 0 else "legitimate",
        })
    return out


def build_summary(prediction: str, probability: float, factors: List[Dict], terms: List[Dict]) -> str:
    pct = round(probability * 100, 1)
    if prediction == "phishing":
        if factors:
            labels = ", ".join(f["title"].lower() for f in factors[:3])
            return f"Flagged as phishing with {pct}% probability. Key signals: {labels}."
        return f"Flagged as phishing with {pct}% probability based on the overall wording pattern of the email."
    if factors:
        labels = ", ".join(f["title"].lower() for f in factors[:2])
        return f"Classified as safe ({pct}% phishing probability), but review these minor signals: {labels}."
    return f"Classified as safe. The wording and structure match legitimate email ({pct}% phishing probability)."


def explain(prediction: str, probability: float, subject: str, sender: str, body: str,
            model, tfidf, x_row, term_direction) -> Dict:
    factors = analyze_signals(subject, sender, body)
    terms = top_terms(model, tfidf, x_row, term_direction)
    return {
        "summary": build_summary(prediction, probability, factors, terms),
        "factors": factors,
        "top_terms": terms,
    }

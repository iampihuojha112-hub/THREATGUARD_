"""URL explanations: per-feature model contributions + readable rule signals."""
from __future__ import annotations

from typing import Dict, List
from urllib.parse import unquote

import numpy as np
from sklearn.pipeline import Pipeline

from ml.explainability.rules import _factor, link_factors
from ml.preprocessing.url import FEATURE_LABELS, FEATURE_NAMES, SUSPICIOUS_KEYWORDS, _split, extract_features

BINARY = {n for n in FEATURE_NAMES if n.startswith(("has_", "is_")) or n in {"suspicious_tld", "brand_mismatch", "executable_extension"}}


def _fmt(name: str, value: float) -> str:
    label = FEATURE_LABELS[name]
    if name in BINARY:
        return f"{label}: {'yes' if value else 'no'}"
    if name.endswith("_ratio"):
        return f"{label}: {value:.2f}"
    if name.endswith("_entropy"):
        return f"{label}: {value:.1f}"
    return f"{label}: {int(round(value))}"


def feature_contributions(model, vector: np.ndarray, stats: dict | None, limit: int = 8) -> List[Dict]:
    """Signed contribution per feature. Positive pushes toward malicious.

    Logistic regression pipeline: exact coefficient x scaled value.
    Tree models: feature importance x z-score against the legitimate-class mean, signed by class lean.
    """
    row = vector.reshape(1, -1).astype(np.float64)
    if isinstance(model, Pipeline):
        scaled = model[:-1].transform(row)[0]
        contrib = scaled * model[-1].coef_[0]
    elif hasattr(model, "feature_importances_") and stats is not None:
        z = (np.log1p(np.clip(row[0], 0, None)) - stats["legit_mean"]) / stats["std"]
        direction = np.sign(stats["phish_mean"] - stats["legit_mean"])
        contrib = model.feature_importances_ * z * direction
    else:
        return []

    order = np.argsort(-np.abs(contrib))[:limit]
    return [
        {
            "term": _fmt(FEATURE_NAMES[i], row[0][i]),
            "weight": round(float(contrib[i]), 4),
            "direction": "phishing" if contrib[i] > 0 else "legitimate",
        }
        for i in order
        if abs(contrib[i]) > 1e-6
    ]


def url_signals(url: str) -> List[Dict]:
    raw, parts, host, port = _split(url)
    feats = extract_features(url)
    rule_text = raw if "://" in raw else "https://" + raw  # avoid a false "not encrypted" flag on scheme-less input
    factors = list(link_factors(rule_text))

    keywords = [k for k in SUSPICIOUS_KEYWORDS if k in unquote(raw).lower()]
    if len(keywords) >= 2:
        factors.append(_factor("sensitive_keywords", "Credential or payment keywords", "medium",
                               "The address contains words typical of fake login and payment pages.", keywords))
    if feats["has_redirect_param"]:
        factors.append(_factor("redirect", "Redirect to another address", "medium",
                               "The URL carries another address inside it, a trick used to launder a malicious destination.", []))
    if feats["url_length"] > 100:
        factors.append(_factor("long_url", "Very long URL", "low", f"The address is {int(feats['url_length'])} characters long. Long URLs hide their real destination.", []))
    if feats["num_percent_encoded"] >= 3:
        factors.append(_factor("encoding", "Heavy percent-encoding", "medium", "Many encoded characters can disguise what the address really says.", []))
    if feats["executable_extension"]:
        factors.append(_factor("download", "Links to an executable or archive", "high", "The path ends in a file type that can run code or hide malware.", [parts.path[-60:]]))
    if feats["host_hyphen_count"] >= 3 or feats["host_digit_count"] >= 5:
        factors.append(_factor("host_pattern", "Machine-generated looking domain", "medium", "Many hyphens or digits in the domain are common in throwaway attack domains.", [host]))
    if feats["has_port"]:
        factors.append(_factor("port", "Non-standard port", "low", f"The link connects on port {port}, which ordinary websites rarely need.", []))
    if feats["host_entropy"] > 4.0 and feats["host_length"] >= 18:
        factors.append(_factor("random_domain", "Random-looking domain", "medium", "The domain name looks randomly generated.", [host]))
    order = {"high": 0, "medium": 1, "low": 2}
    seen, unique = set(), []
    for f in sorted(factors, key=lambda f: order[f["severity"]]):
        if f["type"] not in seen:
            seen.add(f["type"])
            unique.append(f)
    return unique


def build_url_summary(prediction: str, probability: float, factors: List[Dict]) -> str:
    pct = round(probability * 100, 1)
    if prediction == "phishing":
        if factors:
            labels = ", ".join(f["title"].lower() for f in factors[:3])
            return f"Flagged as malicious with {pct}% probability. Key signals: {labels}."
        return f"Flagged as malicious with {pct}% probability based on the structure of the address."
    if factors:
        labels = ", ".join(f["title"].lower() for f in factors[:2])
        return f"Classified as safe ({pct}% malicious probability), but review these minor signals: {labels}."
    return f"Classified as safe. The address structure resembles legitimate sites ({pct}% malicious probability)."


def explain_url(prediction: str, probability: float, url: str, model, vector: np.ndarray, stats: dict | None) -> Dict:
    factors = url_signals(url)
    return {
        "summary": build_url_summary(prediction, probability, factors),
        "factors": factors,
        "top_terms": feature_contributions(model, vector, stats),
    }

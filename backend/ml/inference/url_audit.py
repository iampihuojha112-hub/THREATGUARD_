"""Sanity probes for a trained URL model: are probabilities oriented so that 1 = malicious?"""
from __future__ import annotations

from typing import Callable, Dict, List

SAFE_PROBES: List[str] = ["https://www.google.com", "https://github.com", "https://www.microsoft.com"]
MALICIOUS_PROBES: List[str] = ["http://paypal-login-security-update.xyz", "http://free-gift-card-winner.ru"]


def check_orientation(prob_fn: Callable[[str], float]) -> Dict:
    """`prob_fn(url)` must return P(malicious)."""
    safe = {u: prob_fn(u) for u in SAFE_PROBES}
    bad = {u: prob_fn(u) for u in MALICIOUS_PROBES}
    mean_safe = sum(safe.values()) / len(safe)
    mean_bad = sum(bad.values()) / len(bad)
    if all(p < 0.5 for p in safe.values()) and all(p >= 0.5 for p in bad.values()):
        verdict = "OK"
    elif mean_safe > 0.5 and mean_bad < 0.5:
        verdict = "REVERSED"
    elif mean_safe >= mean_bad:
        verdict = "NO_SEPARATION"
    else:
        verdict = "MIXED"
    return {"safe": safe, "malicious": bad, "mean_safe": mean_safe, "mean_malicious": mean_bad, "verdict": verdict}


def print_probe_report(report: Dict) -> None:
    print("[probe] P(malicious) for known URLs (expected: safe < 0.5, malicious >= 0.5)")
    for group in ("safe", "malicious"):
        for url, p in report[group].items():
            ok = (p < 0.5) if group == "safe" else (p >= 0.5)
            print(f"    {'ok ' if ok else 'XX '} {p:6.3f}  {group:<9} {url}")
    v = report["verdict"]
    note = {
        "OK": "probabilities are oriented correctly.",
        "REVERSED": "LABELS APPEAR REVERSED: safe sites score as malicious and vice versa. Check the dataset's label convention and retrain with --invert-labels.",
        "NO_SEPARATION": "the model does not separate known-safe from known-malicious URLs. Check the dataset and features.",
        "MIXED": "some probes are on the wrong side of 0.5. Orientation looks right on average, but the model is weak on these URLs.",
    }[v]
    print(f"[probe] verdict: {v} - {note}")
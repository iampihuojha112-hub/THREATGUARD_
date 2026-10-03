"""URL feature engineering. Pure lexical analysis: a URL is never fetched or resolved."""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List
from urllib.parse import parse_qsl, unquote, urlsplit

from ml.explainability.rules import (
    BRAND_SAFE_DOMAINS, BRANDS, IP_HOST_RE, SUSPICIOUS_TLDS, URL_SHORTENERS, _registered_domain, brand_in_host,
)

SUSPICIOUS_KEYWORDS = (
    "login", "signin", "sign-in", "verify", "verification", "secure", "account", "update", "confirm", "password",
    "banking", "wallet", "billing", "payment", "invoice", "support", "recover", "unlock", "suspend", "alert",
    "bonus", "prize", "claim", "webscr", "authenticate", "validate",
)
EXECUTABLE_EXTENSIONS = (".exe", ".zip", ".rar", ".apk", ".scr", ".bat", ".msi", ".jar", ".iso", ".dmg", ".vbs", ".ps1", ".cmd")
SPECIAL_CHARS = set("@?&=_%~#$!*+;,|\\^`[]{}()<>'\"")
REDIRECT_PARAMS = {"url", "redirect", "redirect_uri", "redirect_url", "next", "return", "returnurl", "goto", "dest", "destination", "continue", "link"}
HEX_RE = re.compile(r"%[0-9a-fA-F]{2}")
TOKEN_SPLIT_RE = re.compile(r"[^a-zA-Z0-9]+")

FEATURE_VERSION = 2
FEATURE_LABELS: Dict[str, str] = {
    "url_length": "URL length",
    "host_length": "Domain length",
    "domain_name_length": "Domain name length",
    "path_length": "Path length",
    "query_length": "Query length",
    "fragment_length": "Fragment length",
    "num_dots": "Dots",
    "num_hyphens": "Hyphens",
    "num_underscores": "Underscores",
    "num_digits": "Digits",
    "num_special_chars": "Special characters",
    "num_slashes": "Slashes",
    "num_at": "'@' symbols",
    "num_percent_encoded": "Percent-encoded characters",
    "num_query_params": "Query parameters",
    "has_https": "Uses HTTPS",
    "has_ip_host": "IP address as host",
    "has_port": "Non-standard port",
    "has_punycode": "Punycode domain",
    "has_at_symbol": "User-info '@' in host",
    "subdomain_count": "Subdomains",
    "tld_length": "Extension length",
    "suspicious_tld": "High-abuse extension",
    "is_shortener": "URL shortener",
    "path_depth": "Path depth",
    "digit_ratio": "Digit ratio",
    "letter_ratio": "Letter ratio",
    "host_digit_count": "Digits in domain",
    "host_hyphen_count": "Hyphens in domain",
    "host_entropy": "Domain randomness",
    "url_entropy": "URL randomness",
    "longest_token_length": "Longest word-like chunk",
    "keyword_count": "Sensitive keywords",
    "brand_mismatch": "Brand name on another domain",
    "has_redirect_param": "Redirect parameter",
    "has_double_slash_path": "Double slash in path",
    "executable_extension": "Executable file extension",
}
FEATURE_NAMES: List[str] = list(FEATURE_LABELS)


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _split(url: str):
    raw = (url or "").strip().strip("<>\"' \t\r\n")
    candidate = raw if "://" in raw else "//" + raw
    try:
        parts = urlsplit(candidate)
        host = (parts.hostname or "").lower()
        port = parts.port
    except ValueError:
        parts, host, port = urlsplit("//"), "", None
    return raw, parts, host, port


def extract_features(url: str) -> Dict[str, float]:
    raw, parts, host, port = _split(url)
    lower = raw.lower()

    body = raw.split("://", 1)[1] if "://" in raw else raw
    path, query, fragment = parts.path or "", parts.query or "", parts.fragment or ""
    is_ip = bool(IP_HOST_RE.match(host))
    registered = _registered_domain(host) if host and not is_ip else host
    labels = registered.split(".") if registered else []
    domain_name = labels[0] if len(labels) > 1 else registered
    tld = host.rsplit(".", 1)[-1] if "." in host and not is_ip else ""
    subdomain = host[: -len(registered)].strip(".") if host and not is_ip and host != registered else ""
    letters = sum(c.isalpha() for c in body)
    digits = sum(c.isdigit() for c in body)
    length = max(1, len(body))
    decoded = unquote(body.lower())
    haystack = decoded
    tokens = [t for t in TOKEN_SPLIT_RE.split(decoded) if t]
    params = parse_qsl(query, keep_blank_values=True)

    brand_mismatch = 0
    path_tokens = set(TOKEN_SPLIT_RE.split(path.lower()))
    for brand, official in BRANDS.items():
        if registered == official or registered in BRAND_SAFE_DOMAINS:
            continue
        if brand_in_host(host, brand) or (len(brand) >= 4 and brand in path_tokens and not brand_in_host(registered, brand)):
            brand_mismatch = 1
            break

    redirect = any(k.lower() in REDIRECT_PARAMS and ("http" in v.lower() or "//" in v) for k, v in params) or "://" in path

    return {
        "url_length": len(body),
        "host_length": len(host),
        "domain_name_length": len(domain_name),
        "path_length": len(path),
        "query_length": len(query),
        "fragment_length": len(fragment),
        "num_dots": body.count("."),
        "num_hyphens": body.count("-"),
        "num_underscores": body.count("_"),
        "num_digits": digits,
        "num_special_chars": sum(c in SPECIAL_CHARS for c in body),
        "num_slashes": body.count("/"),
        "num_at": body.count("@"),
        "num_percent_encoded": len(HEX_RE.findall(body)),
        "num_query_params": len(params),
        "has_https": int(lower.startswith("https")),
        "has_ip_host": int(is_ip),
        "has_port": int(port is not None and port not in (80, 443)),
        "has_punycode": int(host.startswith("xn--") or ".xn--" in host),
        "has_at_symbol": int("@" in (parts.netloc or "")),
        "subdomain_count": len([s for s in subdomain.split(".") if s]),
        "tld_length": len(tld),
        "suspicious_tld": int(tld in SUSPICIOUS_TLDS),
        "is_shortener": int(host in URL_SHORTENERS),
        "path_depth": len([p for p in path.split("/") if p]),
        "digit_ratio": digits / length,
        "letter_ratio": letters / length,
        "host_digit_count": sum(c.isdigit() for c in host),
        "host_hyphen_count": host.count("-"),
        "host_entropy": _entropy(host),
        "url_entropy": _entropy(body),
        "longest_token_length": max((len(t) for t in tokens), default=0),
        "keyword_count": sum(haystack.count(k) for k in SUSPICIOUS_KEYWORDS),
        "brand_mismatch": brand_mismatch,
        "has_redirect_param": int(bool(redirect)),
        "has_double_slash_path": int("//" in path),
        "executable_extension": int(path.lower().endswith(EXECUTABLE_EXTENSIONS)),
    }


def feature_vector(url: str) -> List[float]:
    feats = extract_features(url)
    return [float(feats[name]) for name in FEATURE_NAMES]

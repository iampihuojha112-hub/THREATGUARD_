"""Rule-based phishing signal detection used to explain a prediction."""
from __future__ import annotations

import re
from typing import Dict, List
from urllib.parse import urlparse

from ml.preprocessing.text import extract_urls

URGENCY_PHRASES = [
    "urgent", "immediately", "act now", "right away", "within 24 hours", "within 48 hours", "final notice",
    "last warning", "expires today", "limited time", "asap", "as soon as possible", "failure to comply",
    "account will be suspended", "account will be closed", "your account has been suspended", "action required",
    "respond immediately", "deadline",
]
CREDENTIAL_PHRASES = [
    "verify your account", "confirm your identity", "confirm your password", "reset your password", "update your password",
    "enter your password", "login to", "log in to", "sign in to", "verify your identity", "security alert",
    "unusual activity", "suspicious activity", "unusual sign-in", "validate your account", "update your billing",
    "update your payment", "social security", "ssn", "pin number", "one-time password", "otp", "credentials",
    "click here to verify", "re-activate", "reactivate",
]
FINANCIAL_PHRASES = [
    "wire transfer", "bank account", "routing number", "credit card", "gift card", "bitcoin", "cryptocurrency",
    "western union", "payment failed", "outstanding invoice", "overdue invoice", "refund", "tax refund", "prize",
    "lottery", "you have won", "inheritance", "transfer funds", "send money", "unpaid balance", "billing information",
]
THREAT_PHRASES = ["legal action", "will be terminated", "suspended", "locked", "penalty", "arrest", "lose access"]

SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "work", "tk", "ml", "ga", "cf", "gq", "zip", "mov", "icu", "buzz", "cyou", "rest",
    "country", "stream", "gdn", "men", "loan", "download", "support", "link", "monster", "cfd", "sbs",
}
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "rb.gy", "shorturl.at",
    "tiny.cc", "rebrand.ly", "s.id", "lnkd.in",
}
FREE_MAIL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "mail.com", "protonmail.com", "gmx.com", "icloud.com", "yandex.com"}
BRANDS = {
    "paypal": "paypal.com", "microsoft": "microsoft.com", "apple": "apple.com", "amazon": "amazon.com",
    "google": "google.com", "netflix": "netflix.com", "facebook": "facebook.com", "instagram": "instagram.com",
    "linkedin": "linkedin.com", "dropbox": "dropbox.com", "docusign": "docusign.com", "chase": "chase.com",
    "wellsfargo": "wellsfargo.com", "bankofamerica": "bankofamerica.com", "citibank": "citi.com", "dhl": "dhl.com",
    "fedex": "fedex.com", "ups": "ups.com", "irs": "irs.gov", "adobe": "adobe.com", "hdfc": "hdfcbank.com",
    "sbi": "sbi.co.in", "icici": "icicibank.com",
}
# NEW
BRAND_SAFE_DOMAINS = {
    "amazonaws.com", "amazon.in", "amazon.co.uk", "googleapis.com", "googleusercontent.com", "google.co.in", "google.co.uk",
    "microsoftonline.com", "office.com", "live.com", "windows.net", "azure.com", "azureedge.net", "apple.news",
    "icloud.com", "fbcdn.net", "facebook.net", "instagram.com", "linkedin.com", "paypalobjects.com",
}
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def brand_in_host(text: str, brand: str) -> bool:
    """Token-aware brand match, so 'groups.google.com' is not 'ups' and 'firstpost.com' is not 'irs'."""
    for token in _NON_ALNUM_RE.split(text.lower()):
        if not token:
            continue
        if token == brand:
            return True
        if len(brand) >= 4 and token.startswith(brand):
            return True
        if len(brand) >= 6 and token.endswith(brand):
            return True
    return False
IP_HOST_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
SENDER_EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@([a-z0-9.\-]+\.[a-z]{2,})", re.IGNORECASE)


def _found(text: str, phrases: List[str]) -> List[str]:
    out = []
    for phrase in phrases:
        if re.search(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", text):
            out.append(phrase)
    return out


def _registered_domain(host: str) -> str:
    parts = [p for p in host.lower().strip(".").split(".") if p]
    if len(parts) <= 2:
        return ".".join(parts)
    if len(parts[-1]) == 2 and parts[-2] in {"co", "com", "org", "net", "gov", "ac"}:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _factor(kind: str, title: str, severity: str, detail: str, evidence: List[str] | None = None) -> Dict:
    return {"type": kind, "title": title, "severity": severity, "detail": detail, "evidence": (evidence or [])[:6]}


def sender_factors(sender: str, text: str) -> List[Dict]:
    factors: List[Dict] = []
    match = SENDER_EMAIL_RE.search(sender or "")
    if not match:
        return factors
    address = match.group(0).lower()
    domain = match.group(1).lower()
    root = _registered_domain(domain)
    tld = domain.rsplit(".", 1)[-1]
    local = address.split("@")[0]
    issues: List[str] = []
    severity = "medium"

    if tld in SUSPICIOUS_TLDS:
        issues.append(f"uses the high-abuse top-level domain .{tld}")
    if domain.startswith("xn--") or ".xn--" in domain:
        issues.append("uses a punycode (look-alike character) domain")
        severity = "high"
    if sum(c.isdigit() for c in root.split(".")[0]) >= 3:
        issues.append("domain name contains many digits")
    if root.split(".")[0].count("-") >= 2:
        issues.append("domain name contains multiple hyphens")
    if domain.count(".") >= 3:
        issues.append("domain has an unusually deep subdomain chain")

    sender_blob = (sender or "").lower()
    for brand, official in BRANDS.items():
        in_name = brand_in_host(sender_blob, brand)
        if in_name and root != official and not root.endswith("." + official):
            if root in FREE_MAIL:
                issues.append(f"claims to be {brand.title()} but sends from a free mail provider ({root})")
            else:
                issues.append(f"mentions {brand.title()} but the sending domain is {root}, not {official}")
            severity = "high"
            break
    else:
        normalized = root.split(".")[0].replace("0", "o").replace("1", "l").replace("3", "e").replace("5", "s")
        for brand, official in BRANDS.items():
            if brand in normalized and root != official:
                issues.append(f"domain {root} imitates {brand.title()} using look-alike characters")
                severity = "high"
                break

    if root in FREE_MAIL and re.search(r"support|security|billing|admin|helpdesk|service|noreply|no-reply", local):
        issues.append("official-sounding mailbox on a free mail provider")

    if issues:
        factors.append(_factor("suspicious_sender", "Suspicious sender", severity, f"The sender {address} " + "; ".join(issues) + ".", [address]))
    return factors


def link_factors(raw_text: str) -> List[Dict]:
    urls = extract_urls(raw_text)
    if not urls:
        return []
    issues: List[str] = []
    evidence: List[str] = []
    severity = "medium"
    for url in urls:
        parsed = urlparse(url if "://" in url else "http://" + url)
        host = (parsed.hostname or "").lower()
        if not host:
            continue
        reasons = []
        if IP_HOST_RE.match(host):
            reasons.append("raw IP address instead of a domain")
            severity = "high"
        if host in URL_SHORTENERS:
            reasons.append("URL shortener hides the destination")
        tld = host.rsplit(".", 1)[-1]
        if tld in SUSPICIOUS_TLDS:
            reasons.append(f"high-abuse domain extension .{tld}")
        if "@" in parsed.netloc:
            reasons.append("contains '@' to disguise the real host")
            severity = "high"
        if host.startswith("xn--") or ".xn--" in host:
            reasons.append("punycode look-alike domain")
            severity = "high"
        if host.count(".") >= 4:
            reasons.append("excessive subdomains")
        if url.lower().startswith("http://"):
            reasons.append("not encrypted (http)")
        root = _registered_domain(host)
        for brand, official in BRANDS.items():
           if brand_in_host(host, brand) and root != official and root not in BRAND_SAFE_DOMAINS:
                reasons.append(f"impersonates {brand.title()} (real domain is {official})")
                severity = "high"
                break
        if reasons:
            issues.extend(reasons)
            evidence.append(url[:120])
    if not evidence:
        return []
    unique = list(dict.fromkeys(issues))
    return [_factor("suspicious_links", "Suspicious links", severity, "Links in this email show warning signs: " + "; ".join(unique[:4]) + ".", evidence)]


def language_factors(raw_text: str) -> List[Dict]:
    text = raw_text.lower()
    factors: List[Dict] = []

    urgency = _found(text, URGENCY_PHRASES)
    if urgency:
        factors.append(_factor("urgency", "Urgency language", "high" if len(urgency) >= 3 else "medium",
                               "The message pressures the reader to act quickly, a common manipulation tactic.", urgency))

    creds = _found(text, CREDENTIAL_PHRASES)
    if creds:
        factors.append(_factor("credential_harvesting", "Credential harvesting phrases", "high" if len(creds) >= 2 else "medium",
                               "The message asks the reader to verify, confirm or enter account credentials.", creds))

    fin = _found(text, FINANCIAL_PHRASES)
    if fin:
        factors.append(_factor("financial_request", "Financial request", "high" if len(fin) >= 2 else "medium",
                               "The message references payments, money transfers or financial incentives.", fin))

    threats = _found(text, THREAT_PHRASES)
    if threats:
        factors.append(_factor("threat", "Threatening language", "medium",
                               "The message warns of negative consequences to push the reader into acting.", threats))
    return factors


def analyze_signals(subject: str, sender: str, body: str) -> List[Dict]:
    raw = f"{subject}\n{body}"
    factors = sender_factors(sender, raw) + link_factors(raw) + language_factors(raw)
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(factors, key=lambda f: order[f["severity"]])

"""Reusable text preprocessing for ThreatGuard."""
from __future__ import annotations

import html
import re
from typing import List

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

URL_RE = re.compile(r"(?:https?://|ftp://|www\.)[^\s<>\"'\)\]]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
HTML_HREF_RE = re.compile(r"href\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")
WHITESPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = frozenset(ENGLISH_STOP_WORDS)
URL_TOKEN = "urltoken"
EMAIL_TOKEN = "emailtoken"


def extract_urls(text: str) -> List[str]:
    """Return unique URLs found in raw text, including href attribute values."""
    if not text:
        return []
    found = HTML_HREF_RE.findall(text) + URL_RE.findall(text)
    seen, urls = set(), []
    for url in found:
        url = url.rstrip(".,;:!?")
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def extract_emails(text: str) -> List[str]:
    """Return unique email addresses found in raw text (lowercased)."""
    if not text:
        return []
    seen, emails = set(), []
    for email in EMAIL_RE.findall(text):
        email = email.lower()
        if email not in seen:
            seen.add(email)
            emails.append(email)
    return emails


ANCHOR_RE = re.compile(r"<a\s[^>]*?href\s*=\s*[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)


def strip_html(text: str) -> str:
    """Remove HTML tags but keep anchor targets so links are still detected."""
    text = ANCHOR_RE.sub(lambda m: f" {m.group(1)} ", text)
    return html.unescape(HTML_TAG_RE.sub(" ", text))


def lowercase(text: str) -> str:
    return text.lower()


def replace_urls(text: str, token: str = URL_TOKEN) -> str:
    return URL_RE.sub(f" {token} ", text)


def replace_emails(text: str, token: str = EMAIL_TOKEN) -> str:
    return EMAIL_RE.sub(f" {token} ", text)


def remove_special_characters(text: str) -> str:
    return NON_ALNUM_RE.sub(" ", text)


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text).strip()


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text)


def remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS and not t.isdigit() and 2 <= len(t) <= 30]


def clean_text(text: str) -> str:
    """Full cleaning pipeline for one string; returns a space-joined token string."""
    if not isinstance(text, str) or not text:
        return ""
    text = strip_html(text)
    text = lowercase(text)
    text = replace_urls(text)
    text = replace_emails(text)
    text = remove_special_characters(text)
    text = normalize_whitespace(text)
    return " ".join(remove_stopwords(tokenize(text)))


def combine_subject_body(subject: str | None, body: str | None) -> str:
    subject = subject if isinstance(subject, str) else ""
    body = body if isinstance(body, str) else ""
    return f"{subject}\n{body}".strip()


def preprocess_email(subject: str | None, body: str | None) -> str:
    """Combine subject + body, then clean. Identical in training and inference."""
    return clean_text(combine_subject_body(subject, body))

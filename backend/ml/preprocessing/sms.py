"""SMS-specific preprocessing. Reuses the shared helpers in ml.preprocessing.text."""
from __future__ import annotations

import re

from ml.preprocessing.text import (
    STOPWORDS,
    lowercase,
    normalize_whitespace,
    remove_special_characters,
    replace_urls,
    tokenize,
)

PHONE_TOKEN = "phonetoken"
SHORTCODE_TOKEN = "shortcodetoken"
MONEY_TOKEN = "moneytoken"
NUMBER_TOKEN = "numbertoken"

PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,5}\)?[\s\-.]?){2,4}\d{2,4}(?!\w)")
SHORTCODE_RE = re.compile(r"(?<!\d)\d{4,6}(?!\d)")
MONEY_RE = re.compile(r"(?:[$£€₹]|\brs\.?|\binr\b|\busd\b)\s?\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s?(?:usd|gbp|eur|inr|rs|dollars|pounds)\b", re.IGNORECASE)

# Stopwords that carry signal in short messages and must be kept.
KEEP = {"call", "free", "now", "please", "once", "never", "only", "send", "show", "front", "fire", "bill", "cry", "system"}
SMS_STOPWORDS = frozenset(STOPWORDS - KEEP)


def extract_phone_numbers(text: str) -> list[str]:
    return [m.group(0).strip() for m in PHONE_RE.finditer(text or "") if sum(c.isdigit() for c in m.group(0)) >= 8]


def clean_sms(text: str) -> str:
    """lowercase -> URL/phone/money/short-code tokens -> strip symbols -> stopwords."""
    if not isinstance(text, str) or not text:
        return ""
    text = lowercase(text)
    text = replace_urls(text)
    text = MONEY_RE.sub(f" {MONEY_TOKEN} ", text)
    text = PHONE_RE.sub(lambda m: f" {PHONE_TOKEN} " if sum(c.isdigit() for c in m.group(0)) >= 8 else m.group(0), text)
    text = SHORTCODE_RE.sub(f" {SHORTCODE_TOKEN} ", text)
    text = remove_special_characters(text)
    text = normalize_whitespace(text)
    tokens = [t for t in tokenize(text) if t not in SMS_STOPWORDS and 2 <= len(t) <= 30]
    tokens = [NUMBER_TOKEN if t.isdigit() else t for t in tokens]
    return " ".join(tokens)


def preprocess_sms(message: str | None) -> str:
    return clean_sms(message if isinstance(message, str) else "")

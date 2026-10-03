"""SMS explanations: model term weights (shared with email) + SMS-specific rule signals."""
from __future__ import annotations

import re
from typing import Dict, List

from ml.explainability.explainer import top_terms
from ml.explainability.rules import (
    CREDENTIAL_PHRASES,
    FINANCIAL_PHRASES,
    THREAT_PHRASES,
    URGENCY_PHRASES,
    _factor,
    _found,
    link_factors,
)
from ml.preprocessing.sms import extract_phone_numbers

PRIZE_PHRASES = [
    "you have won", "you've won", "you won", "winner", "congratulations", "claim your", "free entry", "lucky draw",
    "cash prize", "free gift", "voucher", "reward points", "selected for", "you are eligible",
]
OTP_PHRASES = [
    "otp", "one time password", "verification code", "do not share", "cvv", "card number", "pin", "kyc", "aadhaar",
    "pan card", "net banking", "netbanking", "upi pin", "expire today",
]
DELIVERY_PHRASES = ["parcel", "package", "delivery", "customs fee", "redelivery", "undelivered", "shipment", "courier"]
FEE_PHRASES = ["fee", "pay", "charge", "reschedule", "address", "confirm"]
PREMIUM_PHRASES = ["reply stop", "text stop", "per minute", "premium", "subscription", "msg to", "txt ", "calls cost", "call now", "call us on"]
SHORTCODE_RE = re.compile(r"(?<!\d)\d{4,6}(?!\d)")


def sms_signals(message: str, sender: str = "") -> List[Dict]:
    text = message.lower()
    factors: List[Dict] = list(link_factors(message))

    urgency = _found(text, URGENCY_PHRASES + ["expires", "today only", "hurry", "last chance", "now or"])
    if urgency:
        factors.append(_factor("urgency", "Urgency language", "high" if len(urgency) >= 3 else "medium",
                               "The text pushes you to act immediately, before you can check it.", urgency))

    prize = _found(text, PRIZE_PHRASES)
    if prize:
        factors.append(_factor("prize_reward", "Prize or reward offer", "high" if len(prize) >= 2 else "medium",
                               "Unprompted prizes, vouchers and rewards are a staple of SMS scams.", prize))

    creds = _found(text, CREDENTIAL_PHRASES + OTP_PHRASES)
    if creds:
        factors.append(_factor("credential_harvesting", "Asks for codes or account details", "high",
                               "The text asks for passwords, PINs, OTPs or identity documents. Real senders do not request these by SMS.", creds))

    fin = _found(text, FINANCIAL_PHRASES)
    if fin:
        factors.append(_factor("financial_request", "Financial request", "high" if len(fin) >= 2 else "medium",
                               "The text mentions payments, transfers or money you supposedly owe or can claim.", fin))

    delivery = _found(text, DELIVERY_PHRASES)
    if delivery and (_found(text, FEE_PHRASES) or "http" in text or "www." in text):
        factors.append(_factor("delivery_scam", "Delivery notice with a fee or link", "medium",
                               "Fake courier notices ask for a small fee or address confirmation through a link.", delivery))

    premium = _found(text, PREMIUM_PHRASES)
    phones = extract_phone_numbers(message)
    shortcodes = SHORTCODE_RE.findall(message) if re.search(r"\b(?:reply|text|txt|send|sms)\b", text) else []
    if premium or phones or shortcodes:
        evidence = premium + phones[:2] + shortcodes[:2]
        factors.append(_factor("call_to_action", "Call or reply prompt", "medium" if premium else "low",
                               "The text steers you to a phone number or short code, a common route to premium-rate charges.", evidence))

    threats = _found(text, THREAT_PHRASES)
    if threats:
        factors.append(_factor("threat", "Threatening language", "medium",
                               "The text warns of consequences to pressure you.", threats))

    letters = [c for c in message if c.isalpha()]
    if len(letters) >= 20 and sum(c.isupper() for c in letters) / len(letters) > 0.5:
        factors.append(_factor("shouting", "Mostly capital letters", "low", "Messages written in capitals are common in bulk spam.", []))

    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(factors, key=lambda f: order[f["severity"]])


def build_sms_summary(prediction: str, probability: float, factors: List[Dict]) -> str:
    pct = round(probability * 100, 1)
    if prediction == "phishing":
        if factors:
            labels = ", ".join(f["title"].lower() for f in factors[:3])
            return f"Flagged as a scam with {pct}% probability. Key signals: {labels}."
        return f"Flagged as a scam with {pct}% probability based on the overall wording of the message."
    if factors:
        labels = ", ".join(f["title"].lower() for f in factors[:2])
        return f"Classified as safe ({pct}% scam probability), but review these minor signals: {labels}."
    return f"Classified as safe. The message reads like ordinary SMS ({pct}% scam probability)."


def explain_sms(prediction: str, probability: float, message: str, sender: str, model, tfidf, x_row, term_direction) -> Dict:
    factors = sms_signals(message, sender)
    return {
        "summary": build_sms_summary(prediction, probability, factors),
        "factors": factors,
        "top_terms": top_terms(model, tfidf, x_row, term_direction),
    }

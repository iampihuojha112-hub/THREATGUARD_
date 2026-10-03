import re
from datetime import datetime
from typing import List, Literal, Optional
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator

SENDER_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
ScanType = Literal["email", "url", "sms"]


class AnalyzeRequest(BaseModel):
    subject: str = Field(default="", max_length=998)
    sender: str = Field(min_length=3, max_length=320)
    body: str = Field(min_length=1, max_length=50000)

    @field_validator("subject", "body")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()

    @field_validator("sender")
    @classmethod
    def valid_sender(cls, v: str) -> str:
        v = v.strip()
        if not SENDER_RE.search(v):
            raise ValueError("Sender must contain a valid email address")
        return v

    @field_validator("body")
    @classmethod
    def body_not_blank(cls, v: str) -> str:
        if not v:
            raise ValueError("Email body cannot be empty")
        return v


class AnalyzeUrlRequest(BaseModel):
    url: str = Field(min_length=3, max_length=2048)

    @field_validator("url")
    @classmethod
    def valid_url(cls, v: str) -> str:
        v = v.strip()
        if not v or re.search(r"\s", v):
            raise ValueError("Enter a single URL without spaces")
        try:
            parts = urlsplit(v if "://" in v else "//" + v)
            host = parts.hostname or ""
            _ = parts.port
        except ValueError:
            raise ValueError("That does not look like a valid URL")
        if parts.scheme and parts.scheme.lower() not in ("http", "https", "ftp"):
            raise ValueError("Only http, https and ftp links can be analyzed")
        if "." not in host and not host.startswith("["):
            raise ValueError("The URL needs a domain name, for example example.com/login")
        return v


class AnalyzeSmsRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1600)
    sender: str = Field(default="", max_length=40)

    @field_validator("message", "sender")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v:
            raise ValueError("Message cannot be empty")
        return v


class Factor(BaseModel):
    type: str
    title: str
    severity: Literal["low", "medium", "high"]
    detail: str
    evidence: List[str] = []


class TermContribution(BaseModel):
    term: str
    weight: float
    direction: Literal["phishing", "legitimate"]


class Explanation(BaseModel):
    summary: str
    factors: List[Factor] = []
    top_terms: List[TermContribution] = []


class ScanResult(BaseModel):
    id: str
    scan_type: ScanType = "email"
    subject: str
    sender: str
    body: str
    prediction: Literal["phishing", "safe"]
    probability: float
    risk_score: float
    confidence_score: float
    risk_level: Literal["low", "medium", "high", "critical"]
    explanation: Explanation
    created_at: datetime


class ScanSummary(BaseModel):
    id: str
    scan_type: ScanType = "email"
    title: str = ""
    subject: str
    sender: str
    prediction: Literal["phishing", "safe"]
    risk_score: float
    confidence_score: float
    created_at: datetime


class HistoryResponse(BaseModel):
    items: List[ScanSummary]
    total: int
    page: int
    page_size: int
    total_pages: int

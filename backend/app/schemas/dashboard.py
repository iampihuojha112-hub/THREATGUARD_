from typing import List

from pydantic import BaseModel


class Metrics(BaseModel):
    total_scans: int
    phishing_detected: int
    safe_emails: int
    average_risk_score: float
    email_scans: int = 0
    url_scans: int = 0
    sms_scans: int = 0


class WeeklyPoint(BaseModel):
    week: str
    phishing: int
    safe: int


class DailyPoint(BaseModel):
    date: str
    scans: int


class RiskBucket(BaseModel):
    range: str
    count: int


class DistributionSlice(BaseModel):
    name: str
    value: int


class TypeSlice(BaseModel):
    type: str
    name: str
    value: int
    threats: int


class RecentScan(BaseModel):
    id: str
    scan_type: str
    title: str
    prediction: str
    risk_score: float
    created_at: str


class DashboardResponse(BaseModel):
    metrics: Metrics
    weekly_trend: List[WeeklyPoint]
    daily_activity: List[DailyPoint]
    risk_distribution: List[RiskBucket]
    phishing_vs_safe: List[DistributionSlice]
    type_distribution: List[TypeSlice] = []
    recent_activity: List[RecentScan] = []

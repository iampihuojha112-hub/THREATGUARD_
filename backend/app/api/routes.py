from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import CurrentUser, get_current_user
from app.schemas import AnalyzeRequest, AnalyzeSmsRequest, AnalyzeUrlRequest, DashboardResponse, HistoryResponse, ScanResult
from app.services import scans
from app.services.analyzer import get_predictor, get_sms_predictor, get_url_predictor
from ml.inference import ModelNotLoadedError

router = APIRouter(prefix="/api")


@router.post("/analyze", response_model=ScanResult, status_code=status.HTTP_201_CREATED)
def analyze(payload: AnalyzeRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        result = get_predictor().predict(payload.subject, payload.sender, payload.body)
    except ModelNotLoadedError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc))
    row = scans.create_scan(user.id, user.email, payload.subject, payload.sender, payload.body, result)
    return scans.to_scan_result(row)


@router.post("/analyze/url", response_model=ScanResult, status_code=status.HTTP_201_CREATED)
def analyze_url(payload: AnalyzeUrlRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        result = get_url_predictor().predict(payload.url)
    except ModelNotLoadedError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc))
    row = scans.create_scan(user.id, user.email, "", "", payload.url, result, scan_type="url")
    return scans.to_scan_result(row)


@router.post("/analyze/sms", response_model=ScanResult, status_code=status.HTTP_201_CREATED)
def analyze_sms(payload: AnalyzeSmsRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        result = get_sms_predictor().predict(payload.message, payload.sender)
    except ModelNotLoadedError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc))
    row = scans.create_scan(user.id, user.email, "", payload.sender, payload.message, result, scan_type="sms")
    return scans.to_scan_result(row)


@router.get("/history", response_model=HistoryResponse)
def history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    prediction: str | None = Query(None, pattern="^(phishing|safe)$"),
    sort: str = Query("newest", pattern="^(newest|oldest|risk_desc|risk_asc)$"),
    scan_type: str | None = Query(None, pattern="^(email|url|sms)$"),
    user: CurrentUser = Depends(get_current_user),
):
    return scans.list_scans(user.id, page, page_size, search, prediction, sort, scan_type)


@router.get("/history/{scan_id}", response_model=ScanResult)
def scan_detail(scan_id: str, user: CurrentUser = Depends(get_current_user)):
    result = scans.get_scan(user.id, scan_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scan not found")
    return result


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(user: CurrentUser = Depends(get_current_user)):
    return scans.dashboard(user.id)

from functools import lru_cache

from app.core.config import get_settings
from ml.inference import PhishingPredictor, SmsPredictor, UrlPredictor


@lru_cache
def get_predictor() -> PhishingPredictor:
    return PhishingPredictor(get_settings().model_dir)


@lru_cache
def get_sms_predictor() -> SmsPredictor:
    return SmsPredictor(get_settings().sms_model_dir)


@lru_cache
def get_url_predictor() -> UrlPredictor:
    return UrlPredictor(get_settings().url_model_dir)

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logging.getLogger("threatguard").setLevel(logging.DEBUG)

logger = logging.getLogger("threatguard")

app = FastAPI(title="ThreatGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health():
    from app.services.analyzer import get_predictor, get_sms_predictor, get_url_predictor

    report, ok = {}, False
    for name, getter in (("email", get_predictor), ("sms", get_sms_predictor), ("url", get_url_predictor)):
        predictor = getter()
        try:
            predictor.load()
            report[name] = {"status": "ok", "model": predictor.model_name}
            ok = True
        except Exception as exc:
            report[name] = {"status": "not_trained", "detail": str(exc)}
    # `model` is kept for backwards compatibility with the email-only health response.
    return {"status": "ok" if ok else "degraded", "model": report["email"].get("model"), "models": report}


app.include_router(router)

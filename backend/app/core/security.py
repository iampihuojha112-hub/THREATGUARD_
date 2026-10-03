"""Verify Supabase Auth access tokens by asking Supabase who the token belongs to."""
import logging
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_supabase

logger = logging.getLogger("threatguard.security")

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    email: str


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        logger.warning("Auth failure: no bearer token provided")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    try:
        response = get_supabase().auth.get_user(credentials.credentials)
        user = response.user if response else None
    except Exception as exc:
        logger.warning("Auth failure: Supabase get_user raised an exception: %s", exc)
        user = None
    if user is None:
        logger.warning("Auth failure: token did not resolve to a valid user")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    logger.debug("Auth success: user_id=%s email=%s", user.id, user.email)
    return CurrentUser(id=str(user.id), email=user.email or "")

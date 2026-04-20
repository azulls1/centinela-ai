"""Authentication and authorization middleware."""
import os
import logging
import time
from functools import wraps
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

ADMIN_TOKEN = os.getenv("ADMIN_API_TOKEN", "")
API_KEYS = set(filter(None, os.getenv("API_KEYS", "").split(",")))

def verify_admin_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify admin bearer token."""
    if not credentials:
        token = None
    else:
        token = credentials.credentials

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    return token

def verify_api_key(request: Request):
    """Verify API key from header or query param."""
    api_key = request.headers.get("x-api-key") or request.query_params.get("api_key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    if api_key not in API_KEYS and api_key != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

def optional_api_key(request: Request):
    """Optional API key - allows public access but tracks authenticated users."""
    api_key = request.headers.get("x-api-key") or request.query_params.get("api_key")
    return api_key if (api_key and (api_key in API_KEYS or api_key == ADMIN_TOKEN)) else None

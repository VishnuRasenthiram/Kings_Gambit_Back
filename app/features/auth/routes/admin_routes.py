"""Admin authentication routes."""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ..services.jwt_service import create_access_token, verify_token
from ...bug_report.services.db_service import get_all_reports

ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")

router = APIRouter(prefix="/api/admin", tags=["admin"])
_security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> dict:
    """Dependency: validates JWT bearer token and returns payload."""
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


@router.post("/login")
async def admin_login(data: LoginRequest) -> dict:
    """Authenticate admin and return a JWT access token."""
    if data.username != ADMIN_USERNAME or data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(data.username)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/reports")
async def list_reports(admin: dict = Depends(get_current_admin)) -> dict:
    """Return all stored bug reports (admin only)."""
    reports = await get_all_reports()
    return {"reports": reports, "total": len(reports)}

"""Public bug report submission route."""
from fastapi import APIRouter

from ..models.report import BugReportSubmit
from ..services.db_service import save_report

router = APIRouter(prefix="/api", tags=["bug-reports"])


@router.post("/reports")
async def submit_report(report: BugReportSubmit) -> dict:
    """Accept a bug report from the frontend and store it in SQLite."""
    report_id = await save_report(report)
    return {"success": True, "id": report_id}

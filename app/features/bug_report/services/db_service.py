"""SQLite storage service for bug reports."""
import json
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from ..models.report import BugReportSubmit

DB_PATH: str = str(
    Path(__file__).parent.parent.parent.parent.parent / "kings_gambit.db")


async def init_db() -> None:
    """Create bug_reports table if it does not exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS bug_reports (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                payload    TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
            """
        )
        await db.commit()


async def save_report(report: BugReportSubmit) -> int:
    """Persist a report and return its generated id."""
    created_at = datetime.now(timezone.utc).isoformat()
    payload = report.model_dump()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO bug_reports (description, payload, created_at) VALUES (?, ?, ?)",
            (report.description, json.dumps(payload), created_at),
        )
        await db.commit()
        return int(cursor.lastrowid or 0)


async def get_all_reports() -> list[dict]:
    """Return all reports ordered newest first."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, description, payload, created_at FROM bug_reports ORDER BY id DESC"
        )
        rows = await cursor.fetchall()
    return [
        {
            "id": row["id"],
            "description": row["description"],
            "payload": json.loads(row["payload"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]

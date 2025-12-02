"""Data export endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.task import TaskStatus
from app.services.export_service import ExportService
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/tasks")
async def export_tasks(
    format: str = Query("csv", pattern="^(csv|json)$"),
    status: Optional[List[TaskStatus]] = Query(None),
    team_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export tasks to CSV or JSON format."""
    export_service = ExportService(db)
    content, filename = await export_service.export_tasks(
        user_id=current_user.id,
        format=format,
        status=status,
        team_id=team_id,
    )

    if format == "csv":
        media_type = "text/csv"
    else:
        media_type = "application/json"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

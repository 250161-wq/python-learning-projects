"""Export service for data export functionality."""
import csv
import io
import json
from datetime import datetime, timezone
from typing import List, Optional, Literal

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.models.user import User


class ExportService:
    """Service for exporting data in various formats."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_tasks(
        self,
        user_id: int,
        format: Literal["csv", "json"] = "csv",
        status: Optional[List[TaskStatus]] = None,
        team_id: Optional[int] = None,
    ) -> tuple[str, str]:
        """
        Export tasks to CSV or JSON format.
        Returns tuple of (content, filename).
        """
        # Build query
        query = select(Task).options(
            selectinload(Task.owner),
            selectinload(Task.assignee),
        )

        # Filter by user access
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user.is_admin:
            query = query.where(
                (Task.owner_id == user_id) | (Task.assignee_id == user_id)
            )

        if status:
            query = query.where(Task.status.in_(status))

        if team_id:
            query = query.where(Task.team_id == team_id)

        query = query.order_by(Task.created_at.desc())
        result = await self.db.execute(query)
        tasks = result.scalars().all()

        # Generate timestamp for filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            content = self._tasks_to_csv(tasks)
            filename = f"tasks_export_{timestamp}.csv"
        else:
            content = self._tasks_to_json(tasks)
            filename = f"tasks_export_{timestamp}.json"

        return content, filename

    def _tasks_to_csv(self, tasks: List[Task]) -> str:
        """Convert tasks to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "ID",
            "Title",
            "Description",
            "Status",
            "Priority",
            "Category",
            "Owner",
            "Assignee",
            "Due Date",
            "Estimated Hours",
            "Actual Hours",
            "Progress %",
            "Created At",
            "Updated At",
            "Completed At",
        ])

        # Data rows
        for task in tasks:
            writer.writerow([
                task.id,
                task.title,
                task.description or "",
                task.status.value,
                task.priority.value,
                task.category.value,
                task.owner.username if task.owner else "",
                task.assignee.username if task.assignee else "",
                task.due_date.isoformat() if task.due_date else "",
                task.estimated_hours or "",
                task.actual_hours or "",
                task.progress_percent,
                task.created_at.isoformat(),
                task.updated_at.isoformat(),
                task.completed_at.isoformat() if task.completed_at else "",
            ])

        return output.getvalue()

    def _tasks_to_json(self, tasks: List[Task]) -> str:
        """Convert tasks to JSON format."""
        data = []
        for task in tasks:
            data.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "category": task.category.value,
                "owner": {
                    "id": task.owner.id,
                    "username": task.owner.username,
                    "full_name": task.owner.full_name,
                } if task.owner else None,
                "assignee": {
                    "id": task.assignee.id,
                    "username": task.assignee.username,
                    "full_name": task.assignee.full_name,
                } if task.assignee else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "progress_percent": task.progress_percent,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "is_overdue": task.is_overdue,
            })

        return json.dumps({"tasks": data, "exported_at": datetime.now(timezone.utc).isoformat()}, indent=2)

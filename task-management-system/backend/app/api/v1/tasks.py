"""Task management endpoints."""
import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundError, AuthorizationError, FileUploadError
from app.models.user import User
from app.models.task import TaskStatus, TaskPriority, TaskCategory, Task
from app.models.attachment import Attachment
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskSearchParams,
    TaskOwnerResponse,
)
from app.schemas.attachment import AttachmentResponse
from app.schemas.common import MessageResponse
from app.services.task_service import TaskService
from app.services.notification_service import NotificationService
from app.api.deps import get_current_user

router = APIRouter()


def _task_to_response(task: Task) -> TaskResponse:
    """Convert task model to response schema."""
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        category=task.category,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        progress_percent=task.progress_percent,
        due_date=task.due_date,
        started_at=task.started_at,
        completed_at=task.completed_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_archived=task.is_archived,
        is_overdue=task.is_overdue,
        owner_id=task.owner_id,
        owner=TaskOwnerResponse(
            id=task.owner.id,
            username=task.owner.username,
            full_name=task.owner.full_name,
        ) if task.owner else None,
        assignee_id=task.assignee_id,
        assignee=TaskOwnerResponse(
            id=task.assignee.id,
            username=task.assignee.username,
            full_name=task.assignee.full_name,
        ) if task.assignee else None,
        team_id=task.team_id,
        parent_task_id=task.parent_task_id,
        subtasks_count=len(task.subtasks) if task.subtasks else 0,
        attachments_count=len(task.attachments) if task.attachments else 0,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task."""
    task_service = TaskService(db)
    task = await task_service.create(task_data, current_user.id)

    # Send notification if task is assigned to someone else
    if task.assignee_id and task.assignee_id != current_user.id:
        notification_service = NotificationService(db)
        await notification_service.notify_task_assigned(
            task_id=task.id,
            task_title=task.title,
            assignee_id=task.assignee_id,
            assigner_name=current_user.username,
        )

    return _task_to_response(task)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: Optional[str] = None,
    status: Optional[List[TaskStatus]] = Query(None),
    priority: Optional[List[TaskPriority]] = Query(None),
    category: Optional[List[TaskCategory]] = Query(None),
    assignee_id: Optional[int] = None,
    team_id: Optional[int] = None,
    due_date_from: Optional[datetime] = None,
    due_date_to: Optional[datetime] = None,
    is_archived: Optional[bool] = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List and search tasks with filters."""
    task_service = TaskService(db)
    search_params = TaskSearchParams(
        query=query,
        status=status,
        priority=priority,
        category=category,
        assignee_id=assignee_id,
        team_id=team_id,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        is_archived=is_archived,
    )

    tasks, total = await task_service.search(
        search_params=search_params,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size

    return TaskListResponse(
        items=[_task_to_response(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific task by ID."""
    task_service = TaskService(db)
    task = await task_service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check access
    if not current_user.is_admin and task.owner_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this task",
        )

    return _task_to_response(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a task."""
    task_service = TaskService(db)
    notification_service = NotificationService(db)

    # Get original task for comparison
    original_task = await task_service.get_by_id(task_id)
    if not original_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    original_assignee_id = original_task.assignee_id
    original_status = original_task.status

    try:
        task = await task_service.update(task_id, task_data, current_user)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )

    # Send notifications for relevant changes
    if task.assignee_id and task.assignee_id != original_assignee_id and task.assignee_id != current_user.id:
        await notification_service.notify_task_assigned(
            task_id=task.id,
            task_title=task.title,
            assignee_id=task.assignee_id,
            assigner_name=current_user.username,
        )

    if task.status == TaskStatus.COMPLETED and original_status != TaskStatus.COMPLETED:
        # Notify owner if task was completed by someone else
        if task.owner_id != current_user.id:
            await notification_service.notify_task_completed(
                task_id=task.id,
                task_title=task.title,
                user_id=task.owner_id,
                completer_name=current_user.username,
            )

    return _task_to_response(task)


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    task_service = TaskService(db)
    try:
        await task_service.delete(task_id, current_user)
        return MessageResponse(message="Task deleted successfully")
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.post("/{task_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file attachment to a task."""
    task_service = TaskService(db)
    task = await task_service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check access
    if not current_user.is_admin and task.owner_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload files to this task",
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB",
        )

    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(task_id))
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create attachment record
    attachment = Attachment(
        task_id=task_id,
        uploaded_by_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        content_type=file.content_type or "application/octet-stream",
    )
    db.add(attachment)
    await db.flush()
    await db.refresh(attachment)

    return AttachmentResponse(
        id=attachment.id,
        task_id=attachment.task_id,
        uploaded_by_id=attachment.uploaded_by_id,
        filename=attachment.filename,
        original_filename=attachment.original_filename,
        file_size=attachment.file_size,
        content_type=attachment.content_type,
        created_at=attachment.created_at,
        download_url=f"/api/v1/tasks/{task_id}/attachments/{attachment.id}/download",
    )


@router.get("/{task_id}/attachments", response_model=List[AttachmentResponse])
async def list_attachments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all attachments for a task."""
    task_service = TaskService(db)
    task = await task_service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return [
        AttachmentResponse(
            id=att.id,
            task_id=att.task_id,
            uploaded_by_id=att.uploaded_by_id,
            filename=att.filename,
            original_filename=att.original_filename,
            file_size=att.file_size,
            content_type=att.content_type,
            created_at=att.created_at,
            download_url=f"/api/v1/tasks/{task_id}/attachments/{att.id}/download",
        )
        for att in task.attachments
    ]


@router.get("/{task_id}/attachments/{attachment_id}/download")
async def download_attachment(
    task_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a file attachment."""
    from sqlalchemy import select

    result = await db.execute(
        select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.task_id == task_id,
        )
    )
    attachment = result.scalar_one_or_none()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server",
        )

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.content_type,
    )

"""Task-related Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.task import TaskCategory, TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Base task schema."""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    category: Optional[TaskCategory] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    category: TaskCategory = TaskCategory.OTHER
    estimated_hours: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    team_id: Optional[int] = None
    parent_task_id: Optional[int] = None


class TaskUpdate(TaskBase):
    """Schema for updating a task."""

    assignee_id: Optional[int] = None
    team_id: Optional[int] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    actual_hours: Optional[float] = Field(None, ge=0)
    is_archived: Optional[bool] = None


class TaskOwnerResponse(BaseModel):
    """Minimal user info for task owner/assignee."""

    id: int
    username: str
    full_name: Optional[str]

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    category: TaskCategory
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    progress_percent: int
    due_date: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    is_overdue: bool
    owner_id: int
    owner: TaskOwnerResponse
    assignee_id: Optional[int]
    assignee: Optional[TaskOwnerResponse]
    team_id: Optional[int]
    parent_task_id: Optional[int]
    subtasks_count: int = 0
    attachments_count: int = 0

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response with pagination."""

    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TaskSearchParams(BaseModel):
    """Schema for task search parameters."""

    query: Optional[str] = None
    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    category: Optional[List[TaskCategory]] = None
    assignee_id: Optional[int] = None
    team_id: Optional[int] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    is_overdue: Optional[bool] = None
    is_archived: Optional[bool] = False

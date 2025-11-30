"""Analytics-related Pydantic schemas."""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.models.task import TaskCategory, TaskPriority, TaskStatus


class TaskStatusCount(BaseModel):
    """Count of tasks by status."""

    status: TaskStatus
    count: int


class TaskPriorityCount(BaseModel):
    """Count of tasks by priority."""

    priority: TaskPriority
    count: int


class TaskCategoryCount(BaseModel):
    """Count of tasks by category."""

    category: TaskCategory
    count: int


class TaskCompletionTrend(BaseModel):
    """Task completion trend data point."""

    date: datetime
    completed: int
    created: int


class TaskAnalytics(BaseModel):
    """Task analytics data."""

    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    in_progress_tasks: int
    completion_rate: float
    average_completion_time_hours: Optional[float]
    status_breakdown: List[TaskStatusCount]
    priority_breakdown: List[TaskPriorityCount]
    category_breakdown: List[TaskCategoryCount]
    completion_trend: List[TaskCompletionTrend]


class TeamMemberStats(BaseModel):
    """Statistics for a team member."""

    user_id: int
    username: str
    full_name: Optional[str]
    tasks_assigned: int
    tasks_completed: int
    completion_rate: float


class TeamAnalytics(BaseModel):
    """Team analytics data."""

    team_id: int
    team_name: str
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    completion_rate: float
    member_stats: List[TeamMemberStats]


class UserAnalytics(BaseModel):
    """User-specific analytics data."""

    user_id: int
    total_tasks_owned: int
    total_tasks_assigned: int
    completed_tasks: int
    overdue_tasks: int
    completion_rate: float
    average_completion_time_hours: Optional[float]
    tasks_by_status: List[TaskStatusCount]
    tasks_by_priority: List[TaskPriorityCount]
    recent_activity: List[Dict]

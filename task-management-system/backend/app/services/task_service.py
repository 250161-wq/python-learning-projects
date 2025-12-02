"""Task service for task management operations."""
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, AuthorizationError
from app.models.task import Task, TaskStatus, TaskPriority, TaskCategory
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskUpdate, TaskSearchParams


class TaskService:
    """Service for task-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, task_id: int, include_relations: bool = True
    ) -> Optional[Task]:
        """Get task by ID with optional relations."""
        query = select(Task).where(Task.id == task_id)
        if include_relations:
            query = query.options(
                selectinload(Task.owner),
                selectinload(Task.assignee),
                selectinload(Task.attachments),
                selectinload(Task.subtasks),
            )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, task_data: TaskCreate, owner_id: int) -> Task:
        """Create a new task."""
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            status=task_data.status,
            category=task_data.category,
            estimated_hours=task_data.estimated_hours,
            due_date=task_data.due_date,
            assignee_id=task_data.assignee_id,
            team_id=task_data.team_id,
            parent_task_id=task_data.parent_task_id,
            owner_id=owner_id,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)

        # Load relations
        return await self.get_by_id(task.id)

    async def update(
        self,
        task_id: int,
        task_data: TaskUpdate,
        current_user: User,
    ) -> Task:
        """Update an existing task."""
        task = await self.get_by_id(task_id)
        if not task:
            raise NotFoundError(message="Task not found")

        # Check permissions
        if not self._can_modify_task(task, current_user):
            raise AuthorizationError(message="Not authorized to modify this task")

        update_data = task_data.model_dump(exclude_unset=True)

        # Handle status transitions
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == TaskStatus.IN_PROGRESS and task.started_at is None:
                task.started_at = datetime.now(timezone.utc)
            elif new_status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now(timezone.utc)
                task.progress_percent = 100

        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.flush()
        await self.db.refresh(task)
        return await self.get_by_id(task.id)

    async def delete(self, task_id: int, current_user: User) -> bool:
        """Delete a task."""
        task = await self.get_by_id(task_id)
        if not task:
            raise NotFoundError(message="Task not found")

        # Check permissions
        if not self._can_modify_task(task, current_user):
            raise AuthorizationError(message="Not authorized to delete this task")

        await self.db.delete(task)
        await self.db.flush()
        return True

    async def search(
        self,
        search_params: TaskSearchParams,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Task], int]:
        """Search tasks with filters."""
        query = select(Task).options(
            selectinload(Task.owner),
            selectinload(Task.assignee),
            selectinload(Task.attachments),
            selectinload(Task.subtasks),
        )

        # Build filter conditions
        conditions = []

        # Text search
        if search_params.query:
            search_term = f"%{search_params.query}%"
            conditions.append(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                )
            )

        # Status filter
        if search_params.status:
            conditions.append(Task.status.in_(search_params.status))

        # Priority filter
        if search_params.priority:
            conditions.append(Task.priority.in_(search_params.priority))

        # Category filter
        if search_params.category:
            conditions.append(Task.category.in_(search_params.category))

        # Assignee filter
        if search_params.assignee_id:
            conditions.append(Task.assignee_id == search_params.assignee_id)

        # Team filter
        if search_params.team_id:
            conditions.append(Task.team_id == search_params.team_id)

        # Due date range
        if search_params.due_date_from:
            conditions.append(Task.due_date >= search_params.due_date_from)
        if search_params.due_date_to:
            conditions.append(Task.due_date <= search_params.due_date_to)

        # Archived filter
        if search_params.is_archived is not None:
            conditions.append(Task.is_archived == search_params.is_archived)

        # Apply conditions
        if conditions:
            query = query.where(and_(*conditions))

        # Role-based visibility
        if not current_user.is_admin:
            # Non-admins can only see their own tasks or tasks assigned to them
            query = query.where(
                or_(
                    Task.owner_id == current_user.id,
                    Task.assignee_id == current_user.id,
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Task.created_at.desc())

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    async def get_user_tasks(
        self,
        user_id: int,
        status: Optional[List[TaskStatus]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Task], int]:
        """Get tasks for a specific user."""
        query = select(Task).where(
            or_(Task.owner_id == user_id, Task.assignee_id == user_id)
        )

        if status:
            query = query.where(Task.status.in_(status))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = (
            query.options(
                selectinload(Task.owner),
                selectinload(Task.assignee),
                selectinload(Task.attachments),
                selectinload(Task.subtasks),
            )
            .offset(offset)
            .limit(page_size)
            .order_by(Task.created_at.desc())
        )

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    async def get_team_tasks(
        self,
        team_id: int,
        status: Optional[List[TaskStatus]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Task], int]:
        """Get tasks for a specific team."""
        query = select(Task).where(Task.team_id == team_id)

        if status:
            query = query.where(Task.status.in_(status))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = (
            query.options(
                selectinload(Task.owner),
                selectinload(Task.assignee),
                selectinload(Task.attachments),
                selectinload(Task.subtasks),
            )
            .offset(offset)
            .limit(page_size)
            .order_by(Task.created_at.desc())
        )

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    def _can_modify_task(self, task: Task, user: User) -> bool:
        """Check if user can modify a task."""
        if user.is_admin:
            return True
        if task.owner_id == user.id:
            return True
        if task.assignee_id == user.id:
            return True
        return False

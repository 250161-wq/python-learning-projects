"""Analytics service for generating reports and statistics."""
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus, TaskPriority, TaskCategory
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.analytics import (
    TaskAnalytics,
    TeamAnalytics,
    UserAnalytics,
    TaskStatusCount,
    TaskPriorityCount,
    TaskCategoryCount,
    TaskCompletionTrend,
    TeamMemberStats,
)


class AnalyticsService:
    """Service for generating analytics and reports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_task_analytics(
        self,
        user_id: Optional[int] = None,
        team_id: Optional[int] = None,
        days: int = 30,
    ) -> TaskAnalytics:
        """Get comprehensive task analytics."""
        # Build base query conditions
        conditions = [Task.is_archived == False]
        if user_id:
            conditions.append(
                (Task.owner_id == user_id) | (Task.assignee_id == user_id)
            )
        if team_id:
            conditions.append(Task.team_id == team_id)

        # Total tasks
        total_result = await self.db.execute(
            select(func.count()).select_from(Task).where(and_(*conditions))
        )
        total_tasks = total_result.scalar()

        # Completed tasks
        completed_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(and_(*conditions, Task.status == TaskStatus.COMPLETED))
        )
        completed_tasks = completed_result.scalar()

        # Overdue tasks
        now = datetime.now(timezone.utc)
        overdue_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(
                and_(
                    *conditions,
                    Task.due_date < now,
                    Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.ARCHIVED]),
                )
            )
        )
        overdue_tasks = overdue_result.scalar()

        # In progress tasks
        in_progress_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(and_(*conditions, Task.status == TaskStatus.IN_PROGRESS))
        )
        in_progress_tasks = in_progress_result.scalar()

        # Completion rate
        completion_rate = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )

        # Average completion time
        avg_time_result = await self.db.execute(
            select(
                func.avg(
                    func.julianday(Task.completed_at) - func.julianday(Task.created_at)
                )
            )
            .select_from(Task)
            .where(
                and_(
                    *conditions,
                    Task.completed_at.isnot(None),
                )
            )
        )
        avg_completion_days = avg_time_result.scalar()
        avg_completion_hours = avg_completion_days * 24 if avg_completion_days else None

        # Status breakdown
        status_breakdown = await self._get_status_breakdown(conditions)

        # Priority breakdown
        priority_breakdown = await self._get_priority_breakdown(conditions)

        # Category breakdown
        category_breakdown = await self._get_category_breakdown(conditions)

        # Completion trend
        completion_trend = await self._get_completion_trend(conditions, days)

        return TaskAnalytics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            in_progress_tasks=in_progress_tasks,
            completion_rate=round(completion_rate, 2),
            average_completion_time_hours=round(avg_completion_hours, 2) if avg_completion_hours else None,
            status_breakdown=status_breakdown,
            priority_breakdown=priority_breakdown,
            category_breakdown=category_breakdown,
            completion_trend=completion_trend,
        )

    async def get_team_analytics(self, team_id: int) -> Optional[TeamAnalytics]:
        """Get analytics for a specific team."""
        # Get team
        team_result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        team = team_result.scalar_one_or_none()
        if not team:
            return None

        conditions = [Task.team_id == team_id, Task.is_archived == False]

        # Total tasks
        total_result = await self.db.execute(
            select(func.count()).select_from(Task).where(and_(*conditions))
        )
        total_tasks = total_result.scalar()

        # Completed tasks
        completed_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(and_(*conditions, Task.status == TaskStatus.COMPLETED))
        )
        completed_tasks = completed_result.scalar()

        # Overdue tasks
        now = datetime.now(timezone.utc)
        overdue_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(
                and_(
                    *conditions,
                    Task.due_date < now,
                    Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.ARCHIVED]),
                )
            )
        )
        overdue_tasks = overdue_result.scalar()

        # Completion rate
        completion_rate = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )

        # Member stats
        member_stats = await self._get_team_member_stats(team_id)

        return TeamAnalytics(
            team_id=team_id,
            team_name=team.name,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            completion_rate=round(completion_rate, 2),
            member_stats=member_stats,
        )

    async def get_user_analytics(self, user_id: int) -> Optional[UserAnalytics]:
        """Get analytics for a specific user."""
        # Check user exists
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None

        # Total tasks owned
        owned_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(Task.owner_id == user_id, Task.is_archived == False)
        )
        total_owned = owned_result.scalar()

        # Total tasks assigned
        assigned_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(Task.assignee_id == user_id, Task.is_archived == False)
        )
        total_assigned = assigned_result.scalar()

        # Completed tasks
        completed_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(
                Task.assignee_id == user_id,
                Task.status == TaskStatus.COMPLETED,
            )
        )
        completed_tasks = completed_result.scalar()

        # Overdue tasks
        now = datetime.now(timezone.utc)
        overdue_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(
                Task.assignee_id == user_id,
                Task.due_date < now,
                Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.ARCHIVED]),
            )
        )
        overdue_tasks = overdue_result.scalar()

        # Completion rate
        completion_rate = (
            (completed_tasks / total_assigned * 100) if total_assigned > 0 else 0.0
        )

        # Average completion time
        avg_time_result = await self.db.execute(
            select(
                func.avg(
                    func.julianday(Task.completed_at) - func.julianday(Task.created_at)
                )
            )
            .select_from(Task)
            .where(
                Task.assignee_id == user_id,
                Task.completed_at.isnot(None),
            )
        )
        avg_completion_days = avg_time_result.scalar()
        avg_completion_hours = avg_completion_days * 24 if avg_completion_days else None

        # Tasks by status
        conditions = [
            (Task.owner_id == user_id) | (Task.assignee_id == user_id),
            Task.is_archived == False,
        ]
        tasks_by_status = await self._get_status_breakdown(conditions)
        tasks_by_priority = await self._get_priority_breakdown(conditions)

        # Recent activity (last 10 tasks)
        recent_result = await self.db.execute(
            select(Task)
            .where((Task.owner_id == user_id) | (Task.assignee_id == user_id))
            .order_by(Task.updated_at.desc())
            .limit(10)
        )
        recent_tasks = recent_result.scalars().all()
        recent_activity = [
            {
                "task_id": task.id,
                "title": task.title,
                "status": task.status.value,
                "updated_at": task.updated_at.isoformat(),
            }
            for task in recent_tasks
        ]

        return UserAnalytics(
            user_id=user_id,
            total_tasks_owned=total_owned,
            total_tasks_assigned=total_assigned,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            completion_rate=round(completion_rate, 2),
            average_completion_time_hours=round(avg_completion_hours, 2) if avg_completion_hours else None,
            tasks_by_status=tasks_by_status,
            tasks_by_priority=tasks_by_priority,
            recent_activity=recent_activity,
        )

    async def _get_status_breakdown(self, conditions: list) -> List[TaskStatusCount]:
        """Get task count by status."""
        result = await self.db.execute(
            select(Task.status, func.count(Task.id))
            .where(and_(*conditions))
            .group_by(Task.status)
        )
        return [
            TaskStatusCount(status=row[0], count=row[1])
            for row in result.all()
        ]

    async def _get_priority_breakdown(self, conditions: list) -> List[TaskPriorityCount]:
        """Get task count by priority."""
        result = await self.db.execute(
            select(Task.priority, func.count(Task.id))
            .where(and_(*conditions))
            .group_by(Task.priority)
        )
        return [
            TaskPriorityCount(priority=row[0], count=row[1])
            for row in result.all()
        ]

    async def _get_category_breakdown(self, conditions: list) -> List[TaskCategoryCount]:
        """Get task count by category."""
        result = await self.db.execute(
            select(Task.category, func.count(Task.id))
            .where(and_(*conditions))
            .group_by(Task.category)
        )
        return [
            TaskCategoryCount(category=row[0], count=row[1])
            for row in result.all()
        ]

    async def _get_completion_trend(
        self, conditions: list, days: int
    ) -> List[TaskCompletionTrend]:
        """Get task completion trend over time."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        trend = []

        # For simplicity, aggregate by week
        for week in range(days // 7):
            week_start = start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(weeks=1)

            # Completed in this week
            completed_result = await self.db.execute(
                select(func.count())
                .select_from(Task)
                .where(
                    and_(
                        *conditions,
                        Task.completed_at >= week_start,
                        Task.completed_at < week_end,
                    )
                )
            )
            completed = completed_result.scalar()

            # Created in this week
            created_result = await self.db.execute(
                select(func.count())
                .select_from(Task)
                .where(
                    and_(
                        *conditions,
                        Task.created_at >= week_start,
                        Task.created_at < week_end,
                    )
                )
            )
            created = created_result.scalar()

            trend.append(
                TaskCompletionTrend(
                    date=week_start,
                    completed=completed,
                    created=created,
                )
            )

        return trend

    async def _get_team_member_stats(self, team_id: int) -> List[TeamMemberStats]:
        """Get statistics for each team member."""
        # Get team members
        members_result = await self.db.execute(
            select(TeamMember, User)
            .join(User, TeamMember.user_id == User.id)
            .where(TeamMember.team_id == team_id)
        )
        members = members_result.all()

        stats = []
        for member, user in members:
            # Tasks assigned to this member in this team
            assigned_result = await self.db.execute(
                select(func.count())
                .select_from(Task)
                .where(
                    Task.team_id == team_id,
                    Task.assignee_id == user.id,
                    Task.is_archived == False,
                )
            )
            tasks_assigned = assigned_result.scalar()

            # Completed tasks
            completed_result = await self.db.execute(
                select(func.count())
                .select_from(Task)
                .where(
                    Task.team_id == team_id,
                    Task.assignee_id == user.id,
                    Task.status == TaskStatus.COMPLETED,
                )
            )
            tasks_completed = completed_result.scalar()

            completion_rate = (
                (tasks_completed / tasks_assigned * 100) if tasks_assigned > 0 else 0.0
            )

            stats.append(
                TeamMemberStats(
                    user_id=user.id,
                    username=user.username,
                    full_name=user.full_name,
                    tasks_assigned=tasks_assigned,
                    tasks_completed=tasks_completed,
                    completion_rate=round(completion_rate, 2),
                )
            )

        return stats

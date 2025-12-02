"""Notification service for real-time notifications."""
import json
from datetime import datetime, timezone
from typing import List, Optional, Set
from collections import defaultdict

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationCreate


# In-memory WebSocket connections store (for simplicity)
# In production, use Redis pub/sub
class ConnectionManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[int, Set] = defaultdict(set)

    async def connect(self, websocket, user_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket, user_id: int):
        """Remove a WebSocket connection."""
        self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users."""
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)


# Global connection manager instance
manager = ConnectionManager()


class NotificationService:
    """Service for notification-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification and send via WebSocket."""
        notification = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            related_task_id=notification_data.related_task_id,
            related_team_id=notification_data.related_team_id,
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)

        # Send real-time notification
        await self._send_notification(notification)

        return notification

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Notification], int]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = (
            query.offset(offset)
            .limit(page_size)
            .order_by(Notification.created_at.desc())
        )

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return list(notifications), total

    async def mark_as_read(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = await self.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return None

        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
        return result.rowcount

    async def delete(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        notification = await self.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return False

        await self.db.delete(notification)
        await self.db.flush()
        return True

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return result.scalar()

    async def _send_notification(self, notification: Notification):
        """Send notification via WebSocket."""
        message = {
            "type": "notification",
            "data": {
                "id": notification.id,
                "type": notification.type.value,
                "title": notification.title,
                "message": notification.message,
                "related_task_id": notification.related_task_id,
                "related_team_id": notification.related_team_id,
                "created_at": notification.created_at.isoformat(),
            },
        }
        await manager.send_personal_message(message, notification.user_id)

    # Helper methods for creating specific notification types
    async def notify_task_assigned(
        self, task_id: int, task_title: str, assignee_id: int, assigner_name: str
    ) -> Notification:
        """Create notification for task assignment."""
        return await self.create(
            NotificationCreate(
                user_id=assignee_id,
                type=NotificationType.TASK_ASSIGNED,
                title="New Task Assigned",
                message=f'{assigner_name} assigned you to task "{task_title}"',
                related_task_id=task_id,
            )
        )

    async def notify_task_updated(
        self, task_id: int, task_title: str, user_id: int, updater_name: str
    ) -> Notification:
        """Create notification for task update."""
        return await self.create(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.TASK_UPDATED,
                title="Task Updated",
                message=f'{updater_name} updated task "{task_title}"',
                related_task_id=task_id,
            )
        )

    async def notify_task_completed(
        self, task_id: int, task_title: str, user_id: int, completer_name: str
    ) -> Notification:
        """Create notification for task completion."""
        return await self.create(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.TASK_COMPLETED,
                title="Task Completed",
                message=f'{completer_name} completed task "{task_title}"',
                related_task_id=task_id,
            )
        )

    async def notify_team_invited(
        self, team_id: int, team_name: str, user_id: int, inviter_name: str
    ) -> Notification:
        """Create notification for team invitation."""
        return await self.create(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.TEAM_INVITED,
                title="Team Invitation",
                message=f'{inviter_name} added you to team "{team_name}"',
                related_team_id=team_id,
            )
        )

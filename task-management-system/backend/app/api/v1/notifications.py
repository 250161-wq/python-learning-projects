"""Notification endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.notification_service import NotificationService, manager
from app.api.deps import get_current_user, get_current_user_ws

router = APIRouter()


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    notification_service = NotificationService(db)
    notifications, total = await notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=notifications,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications."""
    notification_service = NotificationService(db)
    count = await notification_service.get_unread_count(current_user.id)
    return {"count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    notification_service = NotificationService(db)
    notification = await notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.post("/mark-all-read", response_model=MessageResponse)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    notification_service = NotificationService(db)
    count = await notification_service.mark_all_as_read(current_user.id)
    return MessageResponse(message=f"Marked {count} notifications as read")


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a notification."""
    notification_service = NotificationService(db)
    success = await notification_service.delete(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return MessageResponse(message="Notification deleted successfully")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications."""
    # Get token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    async with AsyncSessionLocal() as db:
        user = await get_current_user_ws(websocket, db)
        if not user:
            await websocket.close(code=4001, reason="Invalid token")
            return

        await manager.connect(websocket, user.id)
        try:
            while True:
                # Keep connection alive, receive any client messages
                data = await websocket.receive_text()
                # Echo back for ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect:
            manager.disconnect(websocket, user.id)

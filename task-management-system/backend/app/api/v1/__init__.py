"""API v1 router configuration."""
from fastapi import APIRouter

from app.api.v1 import auth, users, tasks, teams, notifications, analytics, export

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])

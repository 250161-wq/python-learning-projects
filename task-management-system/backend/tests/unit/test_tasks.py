"""Unit tests for task endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus, TaskPriority, TaskCategory
from app.models.user import User


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers):
    """Test creating a new task."""
    response = await client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Test Task",
            "description": "Test description",
            "priority": "high",
            "category": "feature",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert data["status"] == "todo"


@pytest.mark.asyncio
async def test_create_task_minimal(client: AsyncClient, auth_headers):
    """Test creating a task with minimal data."""
    response = await client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Minimal Task",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["priority"] == "medium"  # default
    assert data["status"] == "todo"  # default


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test listing tasks."""
    # Create some tasks
    for i in range(3):
        task = Task(
            title=f"Task {i}",
            owner_id=test_user.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.OTHER,
        )
        db_session.add(task)
    await db_session.commit()

    response = await client.get(
        "/api/v1/tasks",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test getting a specific task."""
    task = Task(
        title="Get Task Test",
        owner_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        category=TaskCategory.BUG,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await client.get(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get Task Test"
    assert data["priority"] == "high"


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test updating a task."""
    task = Task(
        title="Update Task Test",
        owner_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        category=TaskCategory.OTHER,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await client.patch(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers,
        json={
            "title": "Updated Title",
            "status": "in_progress",
            "priority": "urgent",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"
    assert data["priority"] == "urgent"


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test deleting a task."""
    task = Task(
        title="Delete Task Test",
        owner_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        category=TaskCategory.OTHER,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await client.delete(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_task_not_found(client: AsyncClient, auth_headers):
    """Test getting a non-existent task."""
    response = await client.get(
        "/api/v1/tasks/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_tasks_by_status(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test filtering tasks by status."""
    # Create tasks with different statuses
    statuses = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]
    for i, status in enumerate(statuses):
        task = Task(
            title=f"Status Task {i}",
            owner_id=test_user.id,
            status=status,
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.OTHER,
        )
        db_session.add(task)
    await db_session.commit()

    response = await client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"status": ["todo", "in_progress"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_search_tasks_by_query(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test searching tasks by text query."""
    task1 = Task(
        title="Important meeting preparation",
        owner_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        category=TaskCategory.OTHER,
    )
    task2 = Task(
        title="Code review",
        owner_id=test_user.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        category=TaskCategory.OTHER,
    )
    db_session.add_all([task1, task2])
    await db_session.commit()

    response = await client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"query": "meeting"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "meeting" in data["items"][0]["title"].lower()

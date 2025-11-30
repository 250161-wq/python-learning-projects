"""Unit tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPassword123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration with duplicate email."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "anotheruser",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    """Test registration with duplicate username."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "another@example.com",
            "username": "testuser",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "WrongPassword123",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_json_success(client: AsyncClient, test_user):
    """Test successful JSON login."""
    response = await client.post(
        "/api/v1/auth/login/json",
        json={
            "username": "testuser",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user, auth_headers):
    """Test getting current user info."""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without authentication."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401

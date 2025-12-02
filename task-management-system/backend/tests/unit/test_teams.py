"""Unit tests for team endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team, TeamMember, TeamRole
from app.models.user import User


@pytest.mark.asyncio
async def test_create_team(client: AsyncClient, auth_headers):
    """Test creating a new team."""
    response = await client.post(
        "/api/v1/teams",
        headers=auth_headers,
        json={
            "name": "Test Team",
            "description": "A test team",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Team"
    assert data["members_count"] == 1  # Creator is added as owner


@pytest.mark.asyncio
async def test_create_duplicate_team(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test creating a team with duplicate name."""
    team = Team(name="Existing Team", description="Existing")
    db_session.add(team)
    await db_session.commit()

    response = await client.post(
        "/api/v1/teams",
        headers=auth_headers,
        json={
            "name": "Existing Team",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_teams(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test listing teams."""
    # Create a team and add the user as a member
    team = Team(name="My Team")
    db_session.add(team)
    await db_session.flush()

    member = TeamMember(
        team_id=team.id,
        user_id=test_user.id,
        role=TeamRole.OWNER,
    )
    db_session.add(member)
    await db_session.commit()

    response = await client.get(
        "/api/v1/teams",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_team_details(client: AsyncClient, test_user, auth_headers, db_session: AsyncSession):
    """Test getting team details."""
    team = Team(name="Detail Team", description="Team details")
    db_session.add(team)
    await db_session.flush()

    member = TeamMember(
        team_id=team.id,
        user_id=test_user.id,
        role=TeamRole.OWNER,
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(team)

    response = await client.get(
        f"/api/v1/teams/{team.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Detail Team"
    assert len(data["members"]) == 1
    assert data["members"][0]["role"] == "owner"


@pytest.mark.asyncio
async def test_add_team_member(client: AsyncClient, test_user, test_admin, auth_headers, db_session: AsyncSession):
    """Test adding a member to a team."""
    team = Team(name="Member Team")
    db_session.add(team)
    await db_session.flush()

    # Add test_user as owner
    member = TeamMember(
        team_id=team.id,
        user_id=test_user.id,
        role=TeamRole.OWNER,
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(team)

    response = await client.post(
        f"/api/v1/teams/{team.id}/members",
        headers=auth_headers,
        json={
            "user_id": test_admin.id,
            "role": "member",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_admin.id
    assert data["role"] == "member"


@pytest.mark.asyncio
async def test_remove_team_member(client: AsyncClient, test_user, test_admin, auth_headers, db_session: AsyncSession):
    """Test removing a member from a team."""
    team = Team(name="Remove Member Team")
    db_session.add(team)
    await db_session.flush()

    # Add test_user as owner
    owner = TeamMember(
        team_id=team.id,
        user_id=test_user.id,
        role=TeamRole.OWNER,
    )
    # Add admin as member
    member = TeamMember(
        team_id=team.id,
        user_id=test_admin.id,
        role=TeamRole.MEMBER,
    )
    db_session.add_all([owner, member])
    await db_session.commit()
    await db_session.refresh(team)

    response = await client.delete(
        f"/api/v1/teams/{team.id}/members/{test_admin.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200

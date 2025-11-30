"""Team service for team collaboration operations."""
from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError, AuthorizationError
from app.models.team import Team, TeamMember, TeamRole
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberCreate


class TeamService:
    """Service for team-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, team_id: int, include_members: bool = False
    ) -> Optional[Team]:
        """Get team by ID."""
        query = select(Team).where(Team.id == team_id)
        if include_members:
            query = query.options(
                selectinload(Team.members).selectinload(TeamMember.user),
                selectinload(Team.tasks),
            )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Team]:
        """Get team by name."""
        result = await self.db.execute(
            select(Team).where(Team.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, team_data: TeamCreate, creator_id: int) -> Team:
        """Create a new team."""
        # Check for existing team name
        existing = await self.get_by_name(team_data.name)
        if existing:
            raise ConflictError(
                message="Team name already exists",
                details={"field": "name"}
            )

        team = Team(
            name=team_data.name,
            description=team_data.description,
        )
        self.db.add(team)
        await self.db.flush()

        # Add creator as team owner
        member = TeamMember(
            team_id=team.id,
            user_id=creator_id,
            role=TeamRole.OWNER,
        )
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(team)

        return await self.get_by_id(team.id, include_members=True)

    async def update(
        self, team_id: int, team_data: TeamUpdate, current_user: User
    ) -> Team:
        """Update an existing team."""
        team = await self.get_by_id(team_id, include_members=True)
        if not team:
            raise NotFoundError(message="Team not found")

        # Check permissions
        if not await self._can_manage_team(team, current_user):
            raise AuthorizationError(message="Not authorized to modify this team")

        update_data = team_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            existing = await self.get_by_name(update_data["name"])
            if existing and existing.id != team_id:
                raise ConflictError(
                    message="Team name already exists",
                    details={"field": "name"}
                )

        for field, value in update_data.items():
            setattr(team, field, value)

        await self.db.flush()
        await self.db.refresh(team)
        return team

    async def delete(self, team_id: int, current_user: User) -> bool:
        """Delete a team."""
        team = await self.get_by_id(team_id, include_members=True)
        if not team:
            raise NotFoundError(message="Team not found")

        # Check permissions
        if not await self._can_manage_team(team, current_user):
            raise AuthorizationError(message="Not authorized to delete this team")

        await self.db.delete(team)
        await self.db.flush()
        return True

    async def add_member(
        self,
        team_id: int,
        member_data: TeamMemberCreate,
        current_user: User,
    ) -> TeamMember:
        """Add a member to a team."""
        team = await self.get_by_id(team_id, include_members=True)
        if not team:
            raise NotFoundError(message="Team not found")

        # Check permissions
        if not await self._can_manage_team(team, current_user):
            raise AuthorizationError(message="Not authorized to manage team members")

        # Check if user is already a member
        existing_member = await self._get_team_member(team_id, member_data.user_id)
        if existing_member:
            raise ConflictError(message="User is already a team member")

        member = TeamMember(
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role,
        )
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(
        self,
        team_id: int,
        user_id: int,
        current_user: User,
    ) -> bool:
        """Remove a member from a team."""
        team = await self.get_by_id(team_id, include_members=True)
        if not team:
            raise NotFoundError(message="Team not found")

        # Check permissions
        if not await self._can_manage_team(team, current_user):
            raise AuthorizationError(message="Not authorized to manage team members")

        member = await self._get_team_member(team_id, user_id)
        if not member:
            raise NotFoundError(message="Team member not found")

        # Can't remove the last owner
        if member.role == TeamRole.OWNER:
            owners = [m for m in team.members if m.role == TeamRole.OWNER]
            if len(owners) <= 1:
                raise ConflictError(message="Cannot remove the last team owner")

        await self.db.delete(member)
        await self.db.flush()
        return True

    async def update_member_role(
        self,
        team_id: int,
        user_id: int,
        new_role: TeamRole,
        current_user: User,
    ) -> TeamMember:
        """Update a team member's role."""
        team = await self.get_by_id(team_id, include_members=True)
        if not team:
            raise NotFoundError(message="Team not found")

        # Check permissions
        if not await self._can_manage_team(team, current_user):
            raise AuthorizationError(message="Not authorized to manage team members")

        member = await self._get_team_member(team_id, user_id)
        if not member:
            raise NotFoundError(message="Team member not found")

        # Can't demote the last owner
        if member.role == TeamRole.OWNER and new_role != TeamRole.OWNER:
            owners = [m for m in team.members if m.role == TeamRole.OWNER]
            if len(owners) <= 1:
                raise ConflictError(message="Cannot demote the last team owner")

        member.role = new_role
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def list_teams(
        self,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        include_inactive: bool = False,
    ) -> Tuple[List[Team], int]:
        """List teams the user has access to."""
        query = select(Team).options(
            selectinload(Team.members),
            selectinload(Team.tasks),
        )

        if not include_inactive:
            query = query.where(Team.is_active == True)

        # Non-admins can only see teams they're members of
        if not current_user.is_admin:
            query = query.join(TeamMember).where(TeamMember.user_id == current_user.id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Team.created_at.desc())

        result = await self.db.execute(query)
        teams = result.scalars().unique().all()

        return list(teams), total

    async def get_user_teams(self, user_id: int) -> List[Team]:
        """Get all teams a user is a member of."""
        query = (
            select(Team)
            .join(TeamMember)
            .where(TeamMember.user_id == user_id)
            .where(Team.is_active == True)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _get_team_member(
        self, team_id: int, user_id: int
    ) -> Optional[TeamMember]:
        """Get a specific team member."""
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def _can_manage_team(self, team: Team, user: User) -> bool:
        """Check if user can manage a team."""
        if user.is_admin:
            return True

        member = await self._get_team_member(team.id, user.id)
        if member and member.role in (TeamRole.OWNER, TeamRole.ADMIN):
            return True

        return False

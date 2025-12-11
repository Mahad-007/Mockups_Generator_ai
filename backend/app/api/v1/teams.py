"""Team management stubs for Agency tier."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import Team, TeamMembership, MembershipRole, SubscriptionTier, User

router = APIRouter()


class TeamCreate(BaseModel):
    name: str


class MemberResponse(BaseModel):
    user_id: str
    email: str
    role: MembershipRole

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    id: str
    name: str
    role: MembershipRole
    members: list[MemberResponse] = []

    class Config:
        from_attributes = True


def _require_agency(user: User):
    if (user.subscription_tier or SubscriptionTier.FREE) != SubscriptionTier.AGENCY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teams are available on the Agency tier.",
        )


@router.post("/", response_model=TeamResponse)
async def create_team(
    payload: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_agency(current_user)

    team = Team(name=payload.name, owner_id=current_user.id)
    membership = TeamMembership(team=team, user_id=current_user.id, role=MembershipRole.OWNER)
    db.add(team)
    db.add(membership)
    await db.flush()
    await db.refresh(team)

    return TeamResponse(
        id=team.id,
        name=team.name,
        role=MembershipRole.OWNER,
        members=[MemberResponse(user_id=current_user.id, email=current_user.email, role=MembershipRole.OWNER)],
    )


@router.get("/", response_model=list[TeamResponse])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_agency(current_user)

    result = await db.execute(
        select(TeamMembership).where(TeamMembership.user_id == current_user.id)
    )
    memberships = result.scalars().all()
    team_ids = [m.team_id for m in memberships]

    teams: list[TeamResponse] = []
    if not team_ids:
        return teams

    result = await db.execute(select(Team).where(Team.id.in_(team_ids)))
    db_teams = {t.id: t for t in result.scalars().all()}

    for m in memberships:
        team = db_teams.get(m.team_id)
        if not team:
            continue
        member_rows = await db.execute(
            select(TeamMembership, User)
            .join(User, User.id == TeamMembership.user_id)
            .where(TeamMembership.team_id == team.id)
        )
        members = [
            MemberResponse(
                user_id=row.User.id,
                email=row.User.email,
                role=row.TeamMembership.role,
            )
            for row in member_rows
        ]
        teams.append(TeamResponse(id=team.id, name=team.name, role=m.role, members=members))
    return teams


class InviteRequest(BaseModel):
    email: EmailStr


@router.post("/{team_id}/invite")
async def invite_member(
    team_id: str,
    payload: InviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_agency(current_user)
    membership = await db.execute(
        select(TeamMembership).where(TeamMembership.team_id == team_id, TeamMembership.user_id == current_user.id)
    )
    member = membership.scalar_one_or_none()
    if not member or member.role not in {MembershipRole.ADMIN, MembershipRole.OWNER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only team admins can invite members.")

    return {
        "message": "Invitations are stubbed for now. Share this email with support to add members.",
        "invite_email": payload.email,
    }


from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlmodel import Session, select

from app.db import get_session
from app.models import Project, ProjectMember, ProjectRole, User
from app.security import decode_access_token


def get_current_user(request: Request, session: Session = Depends(get_session)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_project_or_404(project_id: int, session: Session) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def get_project_membership(project_id: int, user_id: int, session: Session) -> ProjectMember | None:
    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    )
    return session.exec(statement).first()


def require_project_member(
    project_id: int,
    current_user: User,
    session: Session,
) -> ProjectMember:
    membership = require_role(project_id, {ProjectRole.admin, ProjectRole.member}, current_user, session)
    return membership


def require_role(
    project_id: int,
    allowed_roles: set[ProjectRole],
    current_user: User,
    session: Session,
) -> ProjectMember:
    membership = get_project_membership(project_id, current_user.id, session)
    if not membership or membership.role not in allowed_roles:
        detail = "Project access denied" if membership is None else "Insufficient role"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    return membership


def require_project_admin(
    project_id: int,
    current_user: User,
    session: Session,
) -> ProjectMember:
    return require_role(project_id, {ProjectRole.admin}, current_user, session)

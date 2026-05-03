from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.db import get_session
from app.deps import get_current_user, get_project_or_404, require_project_admin, require_project_member
from app.models import Project, ProjectMember, ProjectRole, Task, User
from app.schemas import (
    ProjectCreate,
    ProjectMemberCreate,
    ProjectMemberRead,
    ProjectMemberUpdate,
    ProjectRead,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Project]:
    statement = (
        select(Project)
        .join(ProjectMember, Project.id == ProjectMember.project_id)
        .where(ProjectMember.user_id == current_user.id)
        .order_by(Project.created_at.desc())
    )
    return list(session.exec(statement).all())


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Project:
    project = Project(name=payload.name, description=payload.description, owner_id=current_user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    owner_membership = ProjectMember(project_id=project.id, user_id=current_user.id, role=ProjectRole.admin)
    session.add(owner_membership)
    session.commit()

    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Project:
    require_project_member(project_id, current_user, session)
    return get_project_or_404(project_id, session)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Project:
    require_project_admin(project_id, current_user, session)
    project = get_project_or_404(project_id, session)

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    for key, value in updates.items():
        setattr(project, key, value)

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    require_project_admin(project_id, current_user, session)
    project = get_project_or_404(project_id, session)
    members = session.exec(select(ProjectMember).where(ProjectMember.project_id == project_id)).all()
    tasks = session.exec(select(Task).where(Task.project_id == project_id)).all()

    for member in members:
        session.delete(member)
    for task in tasks:
        session.delete(task)
    session.delete(project)
    session.commit()


@router.get("/{project_id}/members", response_model=list[ProjectMemberRead])
def list_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[ProjectMember]:
    require_project_member(project_id, current_user, session)
    statement = select(ProjectMember).where(ProjectMember.project_id == project_id)
    return list(session.exec(statement).all())


@router.post("/{project_id}/members", response_model=ProjectMemberRead, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    payload: ProjectMemberCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProjectMember:
    require_project_admin(project_id, current_user, session)
    get_project_or_404(project_id, session)

    normalized_email = str(payload.email).lower()
    user = session.exec(select(User).where(func.lower(User.email) == normalized_email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already in project")

    member = ProjectMember(project_id=project_id, user_id=user.id, role=payload.role)
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


@router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberRead)
def update_member_role(
    project_id: int,
    user_id: int,
    payload: ProjectMemberUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProjectMember:
    require_project_admin(project_id, current_user, session)

    member = session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    member.role = payload.role
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    require_project_admin(project_id, current_user, session)

    member = session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if member.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself")

    session.delete(member)
    session.commit()

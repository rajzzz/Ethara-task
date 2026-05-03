from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.deps import get_current_user, require_project_admin, require_project_member
from app.models import ProjectMember, ProjectRole, Task, User
from app.schemas import TaskCreate, TaskRead, TaskStatusUpdate, TaskUpdate

router = APIRouter(tags=["tasks"])


def _get_task_or_404(task_id: int, session: Session) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Task]:
    require_project_member(project_id, current_user, session)
    statement = select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())
    return list(session.exec(statement).all())


@router.post("/projects/{project_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    require_project_member(project_id, current_user, session)

    if payload.assignee_id:
        assignee_membership = session.exec(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == payload.assignee_id,
            )
        ).first()
        if not assignee_membership:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee must be project member")

    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        project_id=project_id,
        assignee_id=payload.assignee_id,
        created_by=current_user.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def get_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    require_project_member(project_id, current_user, session)
    task = _get_task_or_404(task_id, session)
    if task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    project_id: int,
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    require_project_admin(project_id, current_user, session)
    task = _get_task_or_404(task_id, session)
    if task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    if "assignee_id" in updates and updates["assignee_id"] is not None:
        assignee_membership = session.exec(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == updates["assignee_id"],
            )
        ).first()
        if not assignee_membership:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee must be project member")

    for key, value in updates.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/projects/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    require_project_admin(project_id, current_user, session)
    task = _get_task_or_404(task_id, session)
    if task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    session.delete(task)
    session.commit()


@router.patch("/tasks/{task_id}/status", response_model=TaskRead)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    task = _get_task_or_404(task_id, session)
    membership = require_project_member(task.project_id, current_user, session)

    is_admin = membership.role == ProjectRole.admin
    is_assigned_member = task.assignee_id == current_user.id

    if not is_admin and not is_assigned_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Members can only update assigned tasks",
        )

    task.status = payload.status
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

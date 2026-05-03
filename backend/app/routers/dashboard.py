from datetime import date

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.deps import get_current_user
from app.models import ProjectMember, Task, TaskStatus, User
from app.schemas import DashboardRead

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardRead)
def dashboard(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> DashboardRead:
    project_ids_stmt = select(ProjectMember.project_id).where(ProjectMember.user_id == current_user.id)
    project_ids = list(session.exec(project_ids_stmt).all())

    if not project_ids:
        return DashboardRead(total_tasks=0, overdue_tasks=0, by_status={"todo": 0, "in_progress": 0, "done": 0})

    tasks = list(session.exec(select(Task).where(Task.project_id.in_(project_ids))).all())

    today = date.today()
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    overdue = 0

    for task in tasks:
        by_status[task.status.value] += 1
        if task.due_date and task.due_date < today and task.status != TaskStatus.done:
            overdue += 1

    return DashboardRead(total_tasks=len(tasks), overdue_tasks=overdue, by_status=by_status)

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

from app.models import ProjectRole, TaskPriority, TaskStatus

NameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
EmailLookupStr = EmailStr
PasswordStr = Annotated[str, StringConstraints(min_length=8, max_length=128)]
ProjectNameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
ProjectDescriptionStr = Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)]
TaskTitleStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TaskDescriptionStr = Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)]


class MessageResponse(BaseModel):
    message: str


class UserCreate(BaseModel):
    name: NameStr
    email: EmailLookupStr
    password: PasswordStr


class UserLogin(BaseModel):
    email: EmailLookupStr
    password: PasswordStr


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime


class ProjectCreate(BaseModel):
    name: ProjectNameStr
    description: ProjectDescriptionStr | None = None


class ProjectUpdate(BaseModel):
    name: ProjectNameStr | None = None
    description: ProjectDescriptionStr | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime


class ProjectMemberCreate(BaseModel):
    email: EmailLookupStr
    role: ProjectRole = ProjectRole.member


class ProjectMemberUpdate(BaseModel):
    role: ProjectRole


class ProjectMemberRead(BaseModel):
    project_id: int
    user_id: int
    role: ProjectRole


class TaskCreate(BaseModel):
    title: TaskTitleStr
    description: TaskDescriptionStr | None = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: TaskTitleStr | None = None
    description: TaskDescriptionStr | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    assignee_id: int | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    project_id: int
    assignee_id: int | None
    created_by: int
    created_at: datetime


class DashboardRead(BaseModel):
    total_tasks: int
    overdue_tasks: int
    by_status: dict[str, int]

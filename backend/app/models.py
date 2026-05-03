from datetime import date, datetime
from enum import Enum

from sqlalchemy import Column, Enum as SAEnum, UniqueConstraint
from sqlmodel import Field, SQLModel


class ProjectRole(str, Enum):
    admin = "admin"
    member = "member"


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=120)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    owner_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectMember(SQLModel, table=True):
    __tablename__ = "project_member"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    project_id: int = Field(foreign_key="project.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role: ProjectRole = Field(
        default=ProjectRole.member,
        sa_column=Column(SAEnum(ProjectRole, name="project_role"), nullable=False),
    )


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = Field(
        default=TaskStatus.todo,
        sa_column=Column(SAEnum(TaskStatus, name="task_status"), nullable=False),
    )
    priority: TaskPriority = Field(
        default=TaskPriority.medium,
        sa_column=Column(SAEnum(TaskPriority, name="task_priority"), nullable=False),
    )
    due_date: date | None = Field(default=None)

    project_id: int = Field(foreign_key="project.id", index=True)
    assignee_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    created_by: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

from datetime import date, timedelta

from sqlmodel import Session, select

from app.db import engine, init_db
from app.models import Project, ProjectMember, ProjectRole, Task, TaskPriority, TaskStatus, User
from app.security import hash_password


def run() -> None:
    init_db()
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == "demo@ethara.dev")).first()
        if existing:
            print("Seed already applied")
            return

        owner = User(name="Demo Admin", email="demo@ethara.dev", password_hash=hash_password("password123"))
        member = User(name="Demo Member", email="member@ethara.dev", password_hash=hash_password("password123"))
        session.add(owner)
        session.add(member)
        session.commit()
        session.refresh(owner)
        session.refresh(member)

        project = Project(name="Ethara Launch", description="Demo project", owner_id=owner.id)
        session.add(project)
        session.commit()
        session.refresh(project)

        session.add(ProjectMember(project_id=project.id, user_id=owner.id, role=ProjectRole.admin))
        session.add(ProjectMember(project_id=project.id, user_id=member.id, role=ProjectRole.member))

        session.add(
            Task(
                title="Setup backend",
                description="Create auth and project endpoints",
                status=TaskStatus.in_progress,
                priority=TaskPriority.high,
                due_date=date.today() + timedelta(days=1),
                project_id=project.id,
                assignee_id=owner.id,
                created_by=owner.id,
            )
        )
        session.add(
            Task(
                title="Wire dashboard",
                description="Integrate stats API",
                status=TaskStatus.todo,
                priority=TaskPriority.medium,
                due_date=date.today() + timedelta(days=3),
                project_id=project.id,
                assignee_id=member.id,
                created_by=owner.id,
            )
        )

        session.commit()
        print("Seed complete: demo@ethara.dev / password123")


if __name__ == "__main__":
    run()

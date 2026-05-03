from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import normalized_database_url, settings


engine = create_engine(normalized_database_url(settings.database_url), echo=False)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)

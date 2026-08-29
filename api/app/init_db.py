from api.app import models  # noqa: F401 - registers models with SQLAlchemy
from api.app.db import Base, engine


def main() -> None:
    """Create any missing Day 2 PostgreSQL tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")


if __name__ == "__main__":
    main()

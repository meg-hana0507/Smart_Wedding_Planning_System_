from database.database import engine
from database.base import Base


def initialize_database():
    import database.models

    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")


if __name__ == "__main__":
    initialize_database()
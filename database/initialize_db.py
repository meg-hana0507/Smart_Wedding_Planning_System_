# pyrefly: ignore[missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore[missing-import]
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

# 1. Create the engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 2. Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base class for all models
Base = declarative_base()

# 4. Function to create all tables
def init_db():
    # Import models so Base registers all 11 tables before creation
    import database.models
    Base.metadata.create_all(bind=engine)
    print("✅ All 11 tables across all 5 modules created successfully in wedding_planner.db!")

if __name__ == "__main__":
    init_db()
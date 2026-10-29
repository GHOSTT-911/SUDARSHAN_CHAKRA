"""Create only newly introduced tables; existing tables and rows are left untouched."""
from app.db.database import Base, engine
import app.db.models  # noqa: F401 - registers all models with Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Secure document module tables are ready.")

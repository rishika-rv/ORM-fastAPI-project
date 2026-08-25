from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


DATABASE_URL = "sqlite:///./app.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# if __name__ == "__main__":
#     with engine.connect() as connection:
#         print("Database connection successful!")

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print(Base.metadata.tables)
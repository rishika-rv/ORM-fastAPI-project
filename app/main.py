from fastapi import Depends, FastAPI ,HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .import models
from .schemas import UserCreate, UserResponse
from sqlalchemy import select

app = FastAPI(
    title="ORM FastAPI Project",
    description="Learning SQLAlchemy ORM with FastAPI",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "message": "ORM API is running"
    }

@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):

    stmt = select(models.User)
    result = db.execute(stmt)
    users = result.scalars().all()

    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
    ):

    stmt = select(models.User).where(
        models.User.id == user_id)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"

        )

    return user

@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    return {

        "message": "Database session created successfully"

    }


@app.post("/users", response_model=UserResponse)
def create_user(

    user: UserCreate,
    db: Session = Depends(get_db)

):

    new_user = models.User(
        name=user.name,
        email=user.email,
        age=user.age

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
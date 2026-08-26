from fastapi import Depends, FastAPI ,HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .import models
from .schemas import UserCreate, UserResponse, UserUpdate
from sqlalchemy import select

app = FastAPI(
    title="ORM FastAPI Project",
    description="Learning SQLAlchemy ORM with FastAPI",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

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


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)):

    stmt = select(models.User).where(
        models.User.id == user_id
    )
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.name = user_data.name
    user.email = user_data.email
    user.age = user_data.age

    db.commit()
    db.refresh(user)

    return user


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


@app.delete("/users/{user_id}")
def delete_user(
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

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }
from redis.exceptions import RedisError
from fastapi import Depends, FastAPI ,HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .import models
from .schemas import UserCreate, UserResponse, UserUpdate, OrderCreate, OrderResponse
from sqlalchemy import select
import json
from .redis_client import redis_client

app = FastAPI(
    title="ORM FastAPI Project",
    description="Learning SQLAlchemy ORM with FastAPI",
    version="1.0.0"
)

# Base.metadata.create_all(bind=engine)

@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):

    cache_key = "users:all"

    try:
        cached_user = redis_client.get(cache_key)
        if cached_user:
            print(f"REDIS CACHE HIT: {cache_key}")
            return json.loads(cached_user)

        print(f"REDIS CACHE MISS: {cache_key}")

    except RedisError:
    # Redis unavailable - continue to database
        pass

    # Cache miss -> query database
    stmt = select(models.User)
    result = db.execute(stmt)
    users = result.scalars().all()

    # Convert SQLAlchemy objects to Pydantic
    users_data = [
        UserResponse.model_validate(user)
        for user in users
    ]

    # Store list in Redis for 60 seconds
    try:
        redis_client.set(
            cache_key,
            users_data.model_dump_json(),
            ex=60
        )
    except RedisError:
        pass

    return users_data

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    cache_key = f"user:{user_id}"

    # Check Redis first
    try:
        cached_user = redis_client.get(cache_key)

        if cached_user:
            print(f"REDIS CACHE HIT: {cache_key}")
            return json.loads(cached_user)

        print(f"REDIS CACHE MISS: {cache_key}")
    except RedisError:
        pass

    # Cache miss -> database
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

    # Convert SQLAlchemy model to Pydantic
    user_data = UserResponse.model_validate(user)

    # Store in Redis for 60 seconds
    redis_client.set(
        cache_key,
        user_data.model_dump_json(),
        ex=60
    )

    return user_data

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
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

    # Invalidate Redis cache
    redis_client.delete(f"user:{user_id}")
    redis_client.delete("users:all")

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

    # Invalidate users list cache

    redis_client.delete("users:all")

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
    redis_client.delete(f"user:{user_id}")
    redis_client.delete("users:all")

    return {
        "message": "User deleted successfully"
    }

@app.post("/orders", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    user = db.get(models.User, order.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_order = models.Order(
        product=order.product,
        price=order.price,
        user_id=order.user_id
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order

@app.get("/users-with-orders")
def users_with_orders(
    db: Session = Depends(get_db)
):
    stmt = (
        select(models.User, models.Order)
        .join(
            models.Order,
            models.User.id == models.Order.user_id
        )
    )

    result = db.execute(stmt)
    rows = result.all()

    return [
        {
            "user": user,
            "order": order
        }
        for user, order in rows
    ]
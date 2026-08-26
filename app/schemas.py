from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: str
    age: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    name: str
    email: str
    age: int
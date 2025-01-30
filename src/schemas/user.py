from pydantic import BaseModel, EmailStr
from typing import List, Optional

from .todo import TodoResponse
from datetime import datetime


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    email: EmailStr


class UserResponse(UserBase):
    id: int
    email: EmailStr
    created_at: datetime
    todos: List[Optional["TodoResponse"]] = []

    class Config:
        from_attributes = True

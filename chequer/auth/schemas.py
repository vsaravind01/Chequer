from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, user):
        return cls(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

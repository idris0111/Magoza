from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None

class UserRead(UserCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserShort(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)

class CategoryRead(CategoryCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

    

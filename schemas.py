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

    
class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    category_id: int = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)


class ProductShort(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int
    model_config = ConfigDict(from_attributes=True)


class ProductRead(ProductCreate):
    id: int
    category: CategoryRead
    average_rating: float | None = None
    model_config = ConfigDict(from_attributes=True)


class CategoryDetail(CategoryRead):
    products: list[ProductShort] = Field(default_factory=list)


class ProductPage(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: list[ProductRead]

class CartAdd(BaseModel):
    user_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1)

class CartQuantityUpdate(BaseModel):
    quantity: int = Field(ge=1)

class CartDecrease(BaseModel):
    amount: int = Field(default=1, ge=1)

class CartItemRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductShort
    subtotal: Decimal
    model_config = ConfigDict(from_attributes=True)

class CartRead(BaseModel):
    user_id: int
    items: list[CartItemRead]
    total_price: Decimal



class OrderCreate(BaseModel):
    user_id: int = Field(gt=0)


class OrderStatusUpdate(BaseModel):
    status: Literal['NEW', 'PAID', 'CANCELLED']


class OrderItemRead(BaseModel):
    id: int
    product_id: int | None
    product_name: str
    quantity: int
    price: Decimal
    subtotal: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderShort(BaseModel):
    id: int
    user_id: int
    total_price: Decimal
    status: Literal['NEW', 'PAID', 'CANCELLED']
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OrderRead(OrderShort):
    items: list[OrderItemRead] = Field(default_factory=list)


class OrderPage(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: list[OrderShort]

class PurchasedProductRead(BaseModel):
    product_id: int | None
    product_name: str
    orders_count: int
    total_quantity: int
    total_spent: Decimal


class UserStatistics(BaseModel):
    user_id: int
    orders_count: int
    total_spent: Decimal
    last_order: OrderShort | None = None
    most_expensive_order: OrderShort | None = None
    purchased_products: list[PurchasedProductRead] = Field(default_factory=list)

PurchasedProductRead,UserStatistics


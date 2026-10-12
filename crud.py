from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from model import User, Category, Product, CartItem, Order, OrderItem, Review, Favorite
from schemas import UserCreate, UserUpdate, CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate, CartAdd, CartQuantityUpdate, CartDecrease, OrderCreate, OrderStatusUpdate, ReviewCreate, FavoriteCreate



def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, pk: int):
    user = db.query(User).filter(User.id == pk).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


def create_user(db: Session, user: UserCreate):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already exists')
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(db: Session, pk: int, user: UserUpdate):
    old_user = get_user(db, pk)
    if 'name' in user.model_fields_set:
        if user.name is None:
            raise HTTPException(status_code=400, detail='Name cannot be empty')
        old_user.name = user.name
    if 'email' in user.model_fields_set:
        if user.email is None:
            raise HTTPException(status_code=400, detail='Email cannot be empty')
        existing = db.query(User).filter(User.email == user.email, User.id != pk).first()
        if existing:
            raise HTTPException(status_code=400, detail='Email already exists')
        old_user.email = user.email
    db.commit()
    db.refresh(old_user)
    return old_user


def delete_user(db: Session, pk: int):
    user = get_user(db, pk)
    db.delete(user)
    db.commit()
    return {'message': 'User deleted'}

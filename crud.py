from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from model import User, Category, Product, CartItem, Order, OrderItem, Review, Favorite
from schemas import UserCreate, UserUpdate, CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate, CartAdd, CartQuantityUpdate, OrderCreate, OrderStatusUpdate, ReviewCreate, FavoriteCreate

def get_users(db:Session):
    return db.query(User).all()

def get_user(db:Session,pk:int):
    user = db.query(User).filter(User.id==pk).first()
    if not user:
        raise HTTPException(status_code=404,detail='User not found')
    return user

def create_user(db:Session,user:UserCreate):
    old_user = db.query(User).filter(User.email==user.email).first()
    if old_user:
        raise HTTPException(status_code=400,detail='Email already exists')
    new_user = User(name=user.name,email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db:Session,pk:int,user:UserUpdate):
    old_user = get_user(db,pk)
    if user.name is not None:
        old_user.name = user.name
    if user.email is not None:
        same_email = db.query(User).filter(User.email==user.email,User.id!=pk).first()
        if same_email:
            raise HTTPException(status_code=400,detail='Email already exists')
        old_user.email = user.email
    db.commit()
    db.refresh(old_user)
    return old_user

def delete_user(db:Session,pk:int):
    user = get_user(db,pk)
    db.delete(user)
    db.commit()
    return {'message':'User deleted'}


def get_categories(db:Session,search:str=None):
    categories = db.query(Category)
    if search:
        categories = categories.filter(Category.name.ilike(f'%{search}%'))
    return categories.order_by(Category.name).all()

def get_category(db:Session,pk:int):
    category = db.query(Category).filter(Category.id==pk).first()
    if not category:
        raise HTTPException(status_code=404,detail='Category not found')
    return category

def create_category(db:Session,category:CategoryCreate):
    old_category = db.query(Category).filter(Category.name==category.name).first()
    if old_category:
        raise HTTPException(status_code=400,detail='Category already exists')
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def update_category(db:Session,pk:int,category:CategoryUpdate):
    old_category = get_category(db,pk)
    if category.name is not None:
        same_name = db.query(Category).filter(Category.name==category.name,Category.id!=pk).first()
        if same_name:
            raise HTTPException(status_code=400,detail='Category already exists')
        old_category.name = category.name
    db.commit()
    db.refresh(old_category)
    return old_category

def delete_category(db:Session,pk:int):
    category = get_category(db,pk)
    product = db.query(Product).filter(Product.category_id==pk).first()
    if product:
        raise HTTPException(status_code=400,detail='Category has products')
    db.delete(category)
    db.commit()
    return {'message':'Category deleted'}

def get_category_products(db:Session,pk:int):
    get_category(db,pk)
    return db.query(Product).filter(Product.category_id==pk).all()

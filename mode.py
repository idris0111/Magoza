from sqlalchemy import Column,Integer,String,Text,Numeric,ForeignKey,DateTime,UniqueConstraint,CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True)
    name = Column(String(100),nullable=True)
    email = Column(String(100),nullable=False,unique=True)
    create_at = Column(DateTime,server_default=func.now())
    cart_item = relationship('Cartitem',back_populates='user',cascade='all,delete-orphan')
    orders = relationship('Order',back_populates='user',cascade='all,delete-orphan')
    reviews = relationship('Review',back_populates='user',cascade='all,delete-orphan')
    favorites = relationship('Favorite',back_populates='user',cascade='all,delete-orphan')

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer,primary_key=True)
    name = Column(String(100),unique=True,nullable=True)
    products = relationship('Product',back_populates='category')

class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False,index=True)
    description = Column(Text,nullable=True)
    prise = Column(Numeric(10,2),nullable=False)
    stock = Column(Integer,nullable=False,default=0)
    category_id = Column(Integer,ForeignKey('categories.id'),nullable=False)


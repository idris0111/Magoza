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
    price = Column(Numeric(10,2),nullable=False)
    stock = Column(Integer,nullable=False,default=0)
    category_id = Column(Integer,ForeignKey('categories.id'),nullable=False)

    __table_args__ = (CheckConstraint('price > 0'),CheckConstraint("stock >= 0"))
    category = relationship('Category', back_populates='products')
    cart_items = relationship('CartItem', back_populates='product', cascade='all, delete-orphan')
    order_items = relationship('OrderItem', back_populates='product')
    reviews = relationship('Review', back_populates='product', cascade='all, delete-orphan')
    favorites = relationship('Favorite', back_populates='product', cascade='all, delete-orphan')

class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    __table_args__ = (UniqueConstraint('user_id', 'product_id'),CheckConstraint('quantity >= 1'),)
    user = relationship('User', back_populates='cart_items')
    product = relationship('Product', back_populates='cart_items')

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default='NEW')
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (CheckConstraint("status IN ('NEW', 'PAID', 'CANCELLED')"),CheckConstraint('total_price >= 0'),)
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')


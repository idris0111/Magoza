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

def get_products(db:Session,search:str=None,category_id:int=None,sort_price:str=None,page:int=1,size:int=10):
    if page<1 or size<1:
        raise HTTPException(status_code=400,detail='Invalid page or size')
    products = db.query(Product)
    if search:
        products = products.filter(Product.name.ilike(f'%{search}%'))
    if category_id is not None:
        products = products.filter(Product.category_id==category_id)
    if sort_price=='asc':
        products = products.order_by(Product.price.asc(),Product.id)
    elif sort_price=='desc':
        products = products.order_by(Product.price.desc(),Product.id)
    else:
        products = products.order_by(Product.id)
    total = products.count()
    items = products.offset((page-1)*size).limit(size).all()
    return {'total':total,'page':page,'size':size,'pages':(total+size-1)//size,'items':items}

def get_product(db:Session,pk:int):
    product = db.query(Product).filter(Product.id==pk).first()
    if not product:
        raise HTTPException(status_code=404,detail='Product not found')
    product.average_rating = db.query(func.avg(Review.rating)).filter(Review.product_id==pk).scalar()
    return product

def create_product(db:Session,product:ProductCreate):
    get_category(db,product.category_id)
    new_product = Product(name=product.name,description=product.description,price=product.price,stock=product.stock,category_id=product.category_id)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def update_product(db:Session,pk:int,product:ProductUpdate):
    old_product = get_product(db,pk)
    if product.name is not None:
        old_product.name = product.name
    if 'description' in product.model_fields_set:
        old_product.description = product.description
    if product.price is not None:
        old_product.price = product.price
    if product.stock is not None:
        old_product.stock = product.stock
    if product.category_id is not None:
        get_category(db,product.category_id)
        old_product.category_id = product.category_id
    db.commit()
    db.refresh(old_product)
    return old_product

def delete_product(db:Session,pk:int):
    product = get_product(db,pk)
    active_order = db.query(OrderItem).join(Order).filter(OrderItem.product_id==pk,Order.status=='NEW').first()
    if active_order:
        raise HTTPException(status_code=400,detail='Product has active order')
    db.delete(product)
    db.commit()
    return {'message':'Product deleted'}

def get_low_stock_products(db:Session):
    return db.query(Product).filter(Product.stock<5).all()


def get_cart(db:Session,user_id:int):
    get_user(db,user_id)
    items = db.query(CartItem).filter(CartItem.user_id==user_id).all()
    total = Decimal('0.00')
    for item in items:
        total += item.subtotal
    return {'user_id':user_id,'items':items,'total_price':total}

def add_to_cart(db:Session,cart:CartAdd):
    get_user(db,cart.user_id)
    product = get_product(db,cart.product_id)
    item = db.query(CartItem).filter(CartItem.user_id==cart.user_id,CartItem.product_id==cart.product_id).first()
    quantity = cart.quantity
    if item:
        quantity += item.quantity
    if quantity>product.stock:
        raise HTTPException(status_code=400,detail='Not enough stock')
    if item:
        item.quantity = quantity
    else:
        item = CartItem(user_id=cart.user_id,product_id=cart.product_id,quantity=cart.quantity)
        db.add(item)
    db.commit()
    db.refresh(item)
    return item

def update_cart_item(db:Session,pk:int,user_id:int,cart:CartQuantityUpdate):
    item = db.query(CartItem).filter(CartItem.id==pk,CartItem.user_id==user_id).first()
    if not item:
        raise HTTPException(status_code=404,detail='Cart item not found')
    if cart.quantity>item.product.stock:
        raise HTTPException(status_code=400,detail='Not enough stock')
    item.quantity = cart.quantity
    db.commit()
    db.refresh(item)
    return item

def delete_cart_item(db:Session,pk:int,user_id:int):
    item = db.query(CartItem).filter(CartItem.id==pk,CartItem.user_id==user_id).first()
    if not item:
        raise HTTPException(status_code=404,detail='Cart item not found')
    db.delete(item)
    db.commit()
    return {'message':'Cart item deleted'}

def clear_cart(db:Session,user_id:int):
    get_user(db,user_id)
    db.query(CartItem).filter(CartItem.user_id==user_id).delete()
    db.commit()
    return {'message':'Cart cleared'}

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
    if user.orders:
        raise HTTPException(status_code=400,detail='User has orders')
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


def get_products(db:Session,search:str=None,category_id:int=None,sort_price:str=None,page:int=1,size:int=10,min_price:Decimal=None,max_price:Decimal=None):
    if page<1 or size<1:
        raise HTTPException(status_code=400,detail='Invalid page or size')
    if min_price is not None and max_price is not None and min_price>max_price:
        raise HTTPException(status_code=400,detail='Minimum price cannot exceed maximum price')
    products = db.query(Product)
    if search:
        products = products.filter(Product.name.ilike(f'%{search}%'))
    if category_id is not None:
        products = products.filter(Product.category_id==category_id)
    if min_price is not None:
        products = products.filter(Product.price>=min_price)
    if max_price is not None:
        products = products.filter(Product.price<=max_price)
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
    rating = db.query(func.avg(Review.rating)).filter(Review.product_id==pk).scalar()
    product.average_rating = float(rating) if rating is not None else None
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


def create_order(db:Session,order:OrderCreate):
    get_user(db,order.user_id)
    items = db.query(CartItem).filter(CartItem.user_id==order.user_id).all()
    if not items:
        raise HTTPException(status_code=400,detail='Cart is empty')
    for item in items:
        if item.quantity>item.product.stock:
            raise HTTPException(status_code=400,detail='Not enough stock')
    try:
        new_order = Order(user_id=order.user_id,status='NEW',total_price=0)
        db.add(new_order)
        db.flush()
        total = Decimal('0.00')
        for item in items:
            product = item.product
            changed = db.query(Product).filter(Product.id==product.id,Product.stock>=item.quantity).update({Product.stock:Product.stock-item.quantity},synchronize_session=False)
            if changed==0:
                raise HTTPException(status_code=400,detail='Not enough stock')
            new_item = OrderItem(order_id=new_order.id,product_id=product.id,product_name=product.name,quantity=item.quantity,price=product.price)
            db.add(new_item)
            total += product.price*item.quantity
            db.delete(item)
        new_order.total_price = total
        db.commit()
        db.refresh(new_order)
        return new_order
    except Exception:
        db.rollback()
        raise

def get_orders(db:Session,status:str=None,page:int=1,size:int=10):
    if page<1 or size<1:
        raise HTTPException(status_code=400,detail='Invalid page or size')
    orders = db.query(Order)
    if status:
        orders = orders.filter(Order.status==status)
    total = orders.count()
    items = orders.order_by(Order.id.desc()).offset((page-1)*size).limit(size).all()
    return {'total':total,'page':page,'size':size,'pages':(total+size-1)//size,'items':items}

def get_order(db:Session,pk:int):
    order = db.query(Order).filter(Order.id==pk).first()
    if not order:
        raise HTTPException(status_code=404,detail='Order not found')
    return order

def get_user_orders(db:Session,user_id:int):
    get_user(db,user_id)
    return db.query(Order).filter(Order.user_id==user_id).order_by(Order.id.desc()).all()

def cancel_order(db:Session,pk:int):
    order = get_order(db,pk)
    if order.status!='NEW':
        raise HTTPException(status_code=400,detail='Only NEW order can be cancelled')
    try:
        changed = db.query(Order).filter(Order.id==pk,Order.status=='NEW').update({Order.status:'CANCELLED'},synchronize_session=False)
        if changed==0:
            raise HTTPException(status_code=400,detail='Order already processed')
        for item in order.items:
            if item.product_id is not None:
                db.query(Product).filter(Product.id==item.product_id).update({Product.stock:Product.stock+item.quantity},synchronize_session=False)
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise

def update_order_status(db:Session,pk:int,data:OrderStatusUpdate):
    order = get_order(db,pk)
    if data.status=='CANCELLED':
        return cancel_order(db,pk)
    if order.status!='NEW' or data.status!='PAID':
        raise HTTPException(status_code=400,detail='Only NEW order can become PAID')
    order.status = 'PAID'
    db.commit()
    db.refresh(order)
    return order


def get_purchase_history(db:Session,user_id:int):
    get_user(db,user_id)
    return db.query(Order).filter(Order.user_id==user_id,Order.status=='PAID').order_by(Order.id.desc()).all()

def get_purchased_products(db:Session,user_id:int):
    get_user(db,user_id)
    products = db.query(
        OrderItem.product_id,
        OrderItem.product_name,
        func.count(OrderItem.id).label('orders_count'),
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.price*OrderItem.quantity).label('total_spent')).join(Order).filter(Order.user_id==user_id,Order.status=='PAID').group_by(OrderItem.product_id,OrderItem.product_name).all()
    result = []
    for product in products:
        result.append({
            'product_id':product.product_id,
            'product_name':product.product_name,
            'orders_count':product.orders_count,
            'total_quantity':product.total_quantity,
            'total_spent':product.total_spent
        })
    return result

def get_user_statistics(db:Session,user_id:int):
    orders = get_purchase_history(db,user_id)
    total = Decimal('0.00')
    for order in orders:
        total += order.total_price
    last_order = orders[0] if orders else None
    most_expensive = db.query(Order).filter(Order.user_id==user_id,Order.status=='PAID').order_by(Order.total_price.desc()).first()
    products = get_purchased_products(db,user_id)
    return {
        'user_id':user_id,
        'orders_count':len(orders),
        'total_spent':total,
        'last_order':last_order,
        'most_expensive_order':most_expensive,
        'purchased_products':products
    }


def add_review(db:Session,product_id:int,review:ReviewCreate):
    get_user(db,review.user_id)
    get_product(db,product_id)
    new_review = Review(user_id=review.user_id,product_id=product_id,rating=review.rating,comment=review.comment)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

def get_product_reviews(db:Session,product_id:int):
    get_product(db,product_id)
    reviews = db.query(Review).filter(Review.product_id==product_id).all()
    rating = db.query(func.avg(Review.rating)).filter(Review.product_id==product_id).scalar()
    return {'product_id':product_id,'average_rating':float(rating) if rating is not None else None,'reviews_count':len(reviews),'reviews':reviews}

def delete_review(db:Session,pk:int,user_id:int):
    review = db.query(Review).filter(Review.id==pk,Review.user_id==user_id).first()
    if not review:
        raise HTTPException(status_code=404,detail='Review not found')
    db.delete(review)
    db.commit()
    return {'message':'Review deleted'}


def add_favorite(db:Session,favorite:FavoriteCreate):
    get_user(db,favorite.user_id)
    get_product(db,favorite.product_id)
    old = db.query(Favorite).filter(Favorite.user_id==favorite.user_id,Favorite.product_id==favorite.product_id).first()
    if old:
        raise HTTPException(status_code=400,detail='Already in favorites')
    new_favorite = Favorite(user_id=favorite.user_id,product_id=favorite.product_id)
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite

def get_favorites(db:Session,user_id:int):
    get_user(db,user_id)
    return db.query(Favorite).filter(Favorite.user_id==user_id).all()

def delete_favorite(db:Session,pk:int,user_id:int):
    favorite = db.query(Favorite).filter(Favorite.id==pk,Favorite.user_id==user_id).first()
    if not favorite:
        raise HTTPException(status_code=404,detail='Favorite not found')
    db.delete(favorite)
    db.commit()
    return {'message':'Favorite deleted'}


def get_shop_statistics(db:Session):
    orders = db.query(Order).filter(Order.status=='PAID')
    total = db.query(func.sum(Order.total_price)).filter(Order.status=='PAID').scalar() or Decimal('0.00')
    count = orders.count()

    best_selling = db.query(
        Product.id,
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).join(Order).filter(
        Order.status=='PAID'
    ).group_by(Product.id).order_by(
        func.sum(OrderItem.quantity).desc()
    ).first()

    best_product = None
    if best_selling:
        best_product = db.query(Product).filter(Product.id==best_selling.id).first()

    top_user = db.query(
        User.id,
        func.sum(Order.total_price).label('total_spent')
    ).join(Order).filter(
        Order.status=='PAID'
    ).group_by(User.id).order_by(
        func.sum(Order.total_price).desc()
    ).first()

    best_user = None
    if top_user:
        best_user = db.query(User).filter(User.id==top_user.id).first()

    return {
        'users_count':db.query(User).count(),
        'products_count':db.query(Product).count(),
        'categories_count':db.query(Category).count(),
        'orders_count':db.query(Order).count(),
        'orders_total':total,
        'average_order_total':total/count if count else Decimal('0.00'),
        'best_selling_product':best_product,
        'most_expensive_product':db.query(Product).order_by(Product.price.desc()).first(),
        'cheapest_product':db.query(Product).order_by(Product.price.asc()).first(),
        'low_stock_products':get_low_stock_products(db),
        'top_spending_user':best_user
    }

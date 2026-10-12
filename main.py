
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import *
import crud
import model

app = FastAPI(title='Internet Shop API')

Base.metadata.create_all(bind=engine)


# Users
@app.get('/users/',response_model=list[UserRead],tags=['Users'])
def users(db:Session=Depends(get_db)):
    return crud.get_users(db)

@app.get('/users/{pk}/',response_model=UserRead,tags=['Users'])
def user_detail(pk:int,db:Session=Depends(get_db)):
    return crud.get_user(db,pk)

@app.post('/users/',response_model=UserRead,tags=['Users'])
def user_create(user:UserCreate,db:Session=Depends(get_db)):
    return crud.create_user(db,user)

@app.put('/users/{pk}/',response_model=UserRead,tags=['Users'])
def user_update(pk:int,user:UserUpdate,db:Session=Depends(get_db)):
    return crud.update_user(db,pk,user)

@app.delete('/users/{pk}/',tags=['Users'])
def user_delete(pk:int,db:Session=Depends(get_db)):
    return crud.delete_user(db,pk)



@app.get('/categories/',response_model=list[CategoryRead],tags=['Categories'])
def categories(search:str=None,db:Session=Depends(get_db)):
    return crud.get_categories(db,search)

@app.get('/categories/{pk}/',response_model=CategoryDetail,tags=['Categories'])
def category_detail(pk:int,db:Session=Depends(get_db)):
    return crud.get_category(db,pk)

@app.post('/categories/',response_model=CategoryRead,tags=['Categories'])
def category_create(category:CategoryCreate,db:Session=Depends(get_db)):
    return crud.create_category(db,category)

@app.put('/categories/{pk}/',response_model=CategoryRead,tags=['Categories'])
def category_update(pk:int,category:CategoryUpdate,db:Session=Depends(get_db)):
    return crud.update_category(db,pk,category)

@app.delete('/categories/{pk}/',tags=['Categories'])
def category_delete(pk:int,db:Session=Depends(get_db)):
    return crud.delete_category(db,pk)

@app.get('/categories/{pk}/products/',response_model=list[ProductShort],tags=['Categories'])
def category_products(pk:int,db:Session=Depends(get_db)):
    return crud.get_category_products(db,pk)


@app.get('/products/',response_model=ProductPage,tags=['Products'])
def products(search:str=None,category_id:int=None,sort_price:str=None,page:int=Query(1,ge=1),size:int=Query(10,ge=1,le=100),db:Session=Depends(get_db)):
    return crud.get_products(db,search,category_id,sort_price,page,size)

@app.get('/products/low-stock/',response_model=list[ProductShort],tags=['Products'])
def low_stock_products(db:Session=Depends(get_db)):
    return crud.get_low_stock_products(db)

@app.get('/products/{pk}/',response_model=ProductRead,tags=['Products'])
def product_detail(pk:int,db:Session=Depends(get_db)):
    return crud.get_product(db,pk)

@app.post('/products/',response_model=ProductRead,tags=['Products'])
def product_create(product:ProductCreate,db:Session=Depends(get_db)):
    return crud.create_product(db,product)

@app.put('/products/{pk}/',response_model=ProductRead,tags=['Products'])
def product_update(pk:int,product:ProductUpdate,db:Session=Depends(get_db)):
    return crud.update_product(db,pk,product)

@app.delete('/products/{pk}/',tags=['Products'])
def product_delete(pk:int,db:Session=Depends(get_db)):
    return crud.delete_product(db,pk)


@app.post('/cart/add/',response_model=CartItemRead,tags=['Cart'])
def cart_add(cart:CartAdd,db:Session=Depends(get_db)):
    return crud.add_to_cart(db,cart)

@app.get('/cart/{user_id}/',response_model=CartRead,tags=['Cart'])
def cart_detail(user_id:int,db:Session=Depends(get_db)):
    return crud.get_cart(db,user_id)

@app.put('/cart/items/{pk}/',response_model=CartItemRead,tags=['Cart'])
def cart_item_update(pk:int,user_id:int,cart:CartQuantityUpdate,db:Session=Depends(get_db)):
    return crud.update_cart_item(db,pk,user_id,cart)

@app.delete('/cart/items/{pk}/',tags=['Cart'])
def cart_item_delete(pk:int,user_id:int,db:Session=Depends(get_db)):
    return crud.delete_cart_item(db,pk,user_id)

@app.delete('/cart/clear/{user_id}/',tags=['Cart'])
def cart_clear(user_id:int,db:Session=Depends(get_db)):
    return crud.clear_cart(db,user_id)


@app.post('/orders/create/',response_model=OrderRead,tags=['Orders'])
def order_create(order:OrderCreate,db:Session=Depends(get_db)):
    return crud.create_order(db,order)

@app.get('/orders/',response_model=OrderPage,tags=['Orders'])
def orders(status:str=None,page:int=Query(1,ge=1),size:int=Query(10,ge=1,le=100),db:Session=Depends(get_db)):
    return crud.get_orders(db,status,page,size)

@app.get('/orders/{pk}/',response_model=OrderRead,tags=['Orders'])
def order_detail(pk:int,db:Session=Depends(get_db)):
    return crud.get_order(db,pk)

@app.put('/orders/{pk}/status/',response_model=OrderRead,tags=['Orders'])
def order_status_update(pk:int,data:OrderStatusUpdate,db:Session=Depends(get_db)):
    return crud.update_order_status(db,pk,data)

@app.post('/orders/{pk}/cancel/',response_model=OrderRead,tags=['Orders'])
def order_cancel(pk:int,db:Session=Depends(get_db)):
    return crud.cancel_order(db,pk)




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



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

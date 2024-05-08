from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import app.crud as crud
from app.core.database import get_db
from app.schemas import User, UserCreate, UserFull
from app.routes.exception import *


user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.get("/")
async def get_users(skip: int = 0, limit: int = 100, db:Session=Depends(get_db)) -> list[User]:
    return crud.get_users(skip=skip, limit=limit, db=db)

@user_router.get("/{id:int}")
async def get_user_by_id(id:int, db:Session=Depends(get_db)) -> UserFull:
    user = crud.get_user_by_id(user_id=id, db=db)
    if not user:
        raise UserNotFoundException
    return UserFull.model_validate(user, from_attributes=True)

@user_router.post("/")
async def create_user(user:UserCreate, db: Session=Depends(get_db)) -> User:
    user_email = crud.get_user_by_email(email=user.email, db=db)
    user_username = crud.get_user_by_username(username=user.username, db=db)
    if user_email or user_username:
        raise UserExistedException
    user = crud.create_user(new_user=user,db=db)
    return user

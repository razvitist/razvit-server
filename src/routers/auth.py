from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette import status

from config import JWT_ALGORITHM, JWT_LIFETIME_MINUTES, JWT_SECRET_KEY
from database import db_session
from models import User
from utils import genapikey

router = APIRouter(prefix='/auth', tags=['auth'])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
  username: str
  email: str
  password: str


class Token(BaseModel):
  access_token: str
  token_type: str


@router.post('/')
async def create_user(db: db_session, user_request: CreateUserRequest):
  if db.query(User).filter(User.username == user_request.username).first() is None:
    apikey = genapikey()
    user = User(
      username=user_request.username.lower(),
      email=user_request.email,
      password=bcrypt.hashpw(
        user_request.password.encode('utf-8'), salt=bcrypt.gensalt()
      ).decode('utf-8'),
      apikey=apikey,
      # pins={}, oldpins={}, schedule=[], lasttime=int(time.time()), lastpin=0
    )
    db.add(user)
    db.commit()
    return {'created': user_request.username, 'apikey': apikey}
  return {'already exist': user_request.username}


@router.post('/token', response_model=Token)
async def login_for_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_session
):
  user = authenticate_user(form_data.username, form_data.password, db)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
  token = create_token(user.username, user.id, timedelta(minutes=JWT_LIFETIME_MINUTES))
  # response.set_cookie(
  #   key="Authorization",
  #   value=f"Bearer {token}",
  #   httponly=True,
  #   secure=False, # True
  #   samesite="lax",
  #   path="/",
  # )
  return {'access_token': token, 'token_type': 'bearer'}


def authenticate_user(username: str, password: str, db):
  user = db.query(User).filter(User.username == username).first()
  if not user:
    return False
  if not bcrypt.checkpw(
    password=password.encode('utf-8'), hashed_password=user.password.encode('utf-8')
  ):
    return False
  return user


def create_token(username: str, user_id: int, expires_delta: timedelta):
  encode = {'sub': username, 'id': user_id, 'exp': datetime.utcnow() + expires_delta}
  return jwt.encode(encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
  try:
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    username: str = payload.get('sub')
    user_id: int = payload.get('id')
    if username is None or user_id is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {'username': username, 'id': user_id}
  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


user_dependency = Annotated[dict, Depends(get_current_user)]


class ChangePasswordRequest(BaseModel):
  old_password: str
  new_password: str


@router.post('/change-password')
async def change_password(
  change_request: ChangePasswordRequest, user: user_dependency, db: db_session
):
  db_user = db.query(User).filter(User.id == user['id']).first()
  print(user, db_user)
  if not db_user:
    raise HTTPException(status_code=404, detail='User not found')
  if not bcrypt.checkpw(
    password=change_request.old_password.encode('utf-8'),
    hashed_password=db_user.password.encode('utf-8'),
  ):
    raise HTTPException(status_code=400, detail='Old password is incorrect')
  db_user.password = bcrypt.hashpw(
    change_request.new_password.encode('utf-8'), salt=bcrypt.gensalt()
  ).decode('utf-8')
  db.commit()
  return {'detail': 'Password changed successfully'}


@router.delete('/delete')
async def delete_user(user: user_dependency, db: db_session):
  db_user = db.query(User).filter(User.id == user['id']).first()
  if not db_user:
    raise HTTPException(status_code=404, detail='User not found')
  db.delete(db_user)
  db.commit()
  return {'detail': 'User account deleted successfully'}

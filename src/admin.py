from datetime import timedelta

from jose import jwt
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from wtforms import TextAreaField

import models
from config import JWT_ALGORITHM, JWT_LIFETIME_MINUTES, JWT_SECRET_KEY
from database import get_db
from routers.auth import authenticate_user, create_token


class AdminAuth(AuthenticationBackend):
  async def login(self, request: Request) -> bool:
    form = await request.form()
    username, password = form['username'], form['password']
    user = authenticate_user(username, password, next(get_db()))
    if not user:
      return False
    if not user.username == 'admin':
      return False
    token = create_token(
      user.username, user.id, timedelta(minutes=JWT_LIFETIME_MINUTES)
    )
    request.session.update({'token': token})
    return True

  async def logout(self, request: Request) -> bool:
    request.session.clear()
    return True

  async def authenticate(self, request: Request) -> bool:
    token = request.session.get('token')
    if not token:
      return False
    try:
      payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
      username: str = payload.get('sub')
      if username != 'admin':
        return False
    except:
      return False
    return True


class UserAdmin(ModelView, model=models.User):
  column_list = [models.User.id, models.User.username, models.User.email]
  column_details_exclude_list = [models.User.password]


class PostAdmin(ModelView, model=models.Post):
  column_list = [models.Post.id, models.Post.title]

  form_overrides = {'content': TextAreaField}

  form_widget_args = {'content': {'rows': 10, 'cols': 60}}


class TagAdmin(ModelView, model=models.Tag):
  column_list = [models.Tag.id, models.Tag.name]


class ChannelAdmin(ModelView, model=models.Channel):
  column_list = [models.Channel.id, models.Channel.title]


class VideoAdmin(ModelView, model=models.Video):
  column_list = [models.Video.id, models.Video.title]


def setup_admin(app, engine):
  authentication_backend = AdminAuth(secret_key=JWT_SECRET_KEY)
  admin = Admin(app, engine, authentication_backend=authentication_backend)
  admin.add_view(UserAdmin)
  admin.add_view(PostAdmin)
  admin.add_view(TagAdmin)
  admin.add_view(ChannelAdmin)
  admin.add_view(VideoAdmin)

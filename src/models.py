from slugify import slugify
from sqlalchemy import (
  JSON,
  BigInteger,
  Column,
  DateTime,
  ForeignKey,
  Integer,
  String,
  event,
  func,
)
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, Mapper, relationship

from database import Base


class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, index=True)
  username = Column(String, unique=True, nullable=False)
  email = Column(String)
  password = Column(String, nullable=False)
  about = Column(String)
  apikey = Column(String)
  created_at = Column(DateTime, server_default=func.now())
  pins = Column(JSON, default=dict)
  oldpins = Column(JSON, default=dict)
  schedule = Column(JSON, default=list)
  battery = Column(Integer)
  lasttime = Column(Integer)  # время последнего обновления
  lastpin = Column(Integer)  # кол-во баллов на последнем обновлении
  extension_settings = Column(JSON)
  # block get request
  # extension settings (каналы, слова в названии, active urls, audio urls и т.д.)
  posts = relationship('Post', back_populates='user')
  channels = relationship('Channel', back_populates='user')

  def __repr__(self):
    return self.username


class Post(Base):
  __tablename__ = 'posts'
  id = Column(Integer, primary_key=True, autoincrement=True)
  title = Column(String)
  slug = Column(String)
  content = Column(String)
  created_at = Column(DateTime, server_default=func.now())
  user_id = Column(Integer, ForeignKey('users.id'))
  user = relationship('User', back_populates='posts')
  tags: Mapped[list['Tag']] = relationship(secondary='post_tag', back_populates='posts')

  def __repr__(self):
    return self.title


@event.listens_for(Post, 'before_insert')
@event.listens_for(Post, 'before_update')
def post_slug(mapper: Mapper, connection: Connection, target: Post):
  if target.title:
    target.slug = slugify(target.title)


class Tag(Base):
  __tablename__ = 'tags'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String, nullable=False)
  posts: Mapped[list['Post']] = relationship(
    secondary='post_tag', back_populates='tags'
  )

  def __repr__(self):
    return self.name


class PostTag(Base):
  __tablename__ = 'post_tag'
  post_id = Column(ForeignKey('posts.id'), primary_key=True)
  tag_id = Column(ForeignKey('tags.id'), primary_key=True)


class Channel(Base):
  __tablename__ = 'channels'
  id = Column(String, primary_key=True)
  url = Column(String)
  title = Column(String)
  views = Column(BigInteger)
  subs = Column(Integer)
  video_count = Column(Integer)
  lang = Column(String(2))
  icon_default = Column(String)
  icon_medium = Column(String)
  icon_high = Column(String)
  tags = Column(JSON)
  created_at = Column(DateTime, server_default=func.now())
  user_id = Column(Integer, ForeignKey('users.id'))
  user = relationship('User', back_populates='channels')
  videos = relationship('Video', back_populates='channel')

  def __repr__(self):
    return self.title


class Video(Base):
  __tablename__ = 'videos'
  id = Column(Integer, primary_key=True, autoincrement=True)
  title = Column(String)
  video_id = Column(String, unique=True)
  published_at = Column(DateTime)
  thumbnail = Column(String)
  length = Column(Integer)
  views = Column(Integer)
  channel_id = Column(String, ForeignKey('channels.id'), nullable=False)
  channel = relationship('Channel', back_populates='videos')

  def __repr__(self):
    return self.title

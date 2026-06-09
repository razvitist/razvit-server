import json
import time
from datetime import datetime, timedelta

import matplotlib.dates
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import (
  FileResponse,
  HTMLResponse,
  PlainTextResponse,
  RedirectResponse,
)
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm.attributes import flag_modified

import models
from database import db_session
from page import page
from routers.auth import user_dependency

router = APIRouter(tags=['band'])

templates = Jinja2Templates(directory='templates')

# @router.get('/users')
# async def get_users(db: db_session):
#   users = db.query(models.User).all()
#   return [user.username for user in users]

gestapo_disable = {}


@router.get('/control/{apikey}')
async def control(apikey: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  print('get', gestapo_disable)

  df = pd.read_csv(
    'resources/stat.txt',
    sep=' ',
    header=None,
    names=['username', 'date', 'time', 'points'],
  )

  df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
  df = df[['username', 'datetime', 'points']]
  df = df[df['username'] == 'andrei']
  df = df[df['datetime'] > datetime.now() - timedelta(days=7)]

  fig = px.timeline(
    df,
    x_start='datetime',
    x_end=df['datetime'] + timedelta(minutes=2),
    y='username',
    color='points',
    title='Band Status Timeline',
    # template='plotly_dark',
    # template='simple_white',
    # color_continuous_scale='plasma',
    # color_continuous_scale='bluered',
    # color_continuous_scale='teal',
    color_continuous_scale='sunsetdark',
    height=300,
  )

  fig.update_traces(
    marker=dict(line=dict(width=0)),
  )

  fig.update_layout(
    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=40, b=5),
    xaxis=dict(
      #     rangeselector=dict(
      #         buttons=list([
      #             dict(count=1,
      #                   label="1h",
      #                   step="hour",
      #                   stepmode="backward"),
      #             dict(count=1,
      #                   label="1d",
      #                   step="day",
      #                   stepmode="backward"),
      #             dict(step="all")
      #         ])
      #     ),
      rangeslider=dict(visible=True),
      type='date',
      range=[datetime.now() - timedelta(days=1), datetime.now()],
    ),
  )

  content = f"""
  <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Control</title>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
    </head>
    <body>
      <h1>Control</h1>
      <h2>Gestapo Disable</h2>
      <p>{gestapo_disable.get(apikey, datetime(2020, 1, 1, 0, 0)).strftime('%H:%M:%S, %d-%m-%Y')}</p>
      <form action="/control-post/{apikey}" method="POST">
        <p>
          <label>Minutes</label>
          <br>
          <input type="number" required name="minutes" placeholder="Minutes" value="0" min="0" max="600">
        </p>
        <button type="submit">Submit</button>
      </form>
      {fig.to_html(full_html=False)}
    </body>
  </html>
  """
  # <p>
  #   <label>API Key</label>
  #   <br>
  #   <input type="text" required name="apikey" placeholder="API Key" value="{apikey}">
  # </p>
  return HTMLResponse(content)


@router.post('/control-post/{apikey}')
async def control_post(apikey: str, db: db_session, minutes: int = Form()):
  # user = db.query(models.User).filter(models.User.apikey == apikey).first()
  gestapo_disable[apikey] = datetime.now() + timedelta(minutes=min(600, int(minutes)))
  print(gestapo_disable)
  return RedirectResponse(f'/control/{apikey}', status_code=302)


@router.get('/get/{apikey}')
async def get_all(apikey: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  return user.pins


@router.get('/get/{apikey}/{pin}')
async def get_pin(apikey: str, pin: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  return user.pins[pin]


@router.get('/set/{apikey}/{pin}/{val}')
async def set_pin(apikey: str, pin: str, val: int, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  user.pins[pin] = val
  flag_modified(user, 'pins')
  db.commit()
  return {'pin': pin, 'val': val}


@router.get('/plus/{apikey}/{pin}/{val}')
async def plus_pin(apikey: str, pin: str, val: int, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  user.pins[pin] += val
  flag_modified(user, 'pins')
  db.commit()
  return {'pin': pin, 'plus': val}


@router.get('/del/{apikey}/{pin}')
async def del_pin(apikey: str, pin: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  del user.pins[pin]
  flag_modified(user, 'pins')
  db.commit()
  return {'deleted': pin}


@router.get('/time')
async def epoch():
  return PlainTextResponse(str(int(time.time())))


# Умный get
# https://fastapi.tiangolo.com/tutorial/query-params/
# https://fastapi.tiangolo.com/tutorial/body/
# Сделать такие же пины, но old
# http://0.0.0.0:8000/get2/andrei/pencil,heart
# ["pencil","heart"]
@router.get('/get2/{apikey}/{pins}')
async def getx(apikey: str, pins: str, db: db_session):
  pins = pins.split(',')
  print(pins)
  # t = 0
  return pins


def stat(*args):
  with open('resources/stat.txt', 'a') as f:
    print(*args, file=f)


@router.get('/stat/{username}.png')
async def stat_png(username: str, db: db_session):
  user = db.query(models.User).filter(models.User.username == username).first()
  if not user:
    return PlainTextResponse('Wrong username')
  with open('resources/stat.txt') as f:
    m = [i.strip().split() for i in f]
    x_values = matplotlib.dates.date2num(
      [datetime.fromisoformat(i[1] + ' ' + i[2]) for i in m]
    )
    y_values = [int(i[3]) for i in m]
    color = ['blue' if i else 'red' for i in y_values]
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(
      matplotlib.dates.DateFormatter('%H:%M')
    )  # %H:%M:%S\n%d.%m
    fig.set_size_inches(15, 5)
    # fig.figure(figsize=(20, 5))
    ax.scatter(x_values, y_values, color=color, s=1)
    ax.set_xlim(
      matplotlib.dates.date2num(datetime.now() - timedelta(days=1)),
      matplotlib.dates.date2num(datetime.now()),
    )
    plt.savefig('resources/stat.png', dpi=100)
    return FileResponse('resources/stat.png')


@router.get('/stat/{username}')
async def statistics(username: str, db: db_session):
  user = db.query(models.User).filter(models.User.username == username).first()
  if not user:
    return PlainTextResponse('Wrong username')
  with open('resources/stat.txt') as f:
    return page('Statistics', f.read().replace('\n', '<br>'))


class API(BaseModel):
  apikey: str
  content: list


# заменить на базу данных
@router.post('/constrain')
async def constrain_f(content: API, db: db_session):
  user = db.query(models.User).filter(models.User.username == content.apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  with open('json/constrain.json', 'w') as f:
    json.dump(content.content, f)
  return content.content


# http://0.0.0.0:8000/api/JOm1PwyUN5/?battery=85&version=12
# battery: int, version: int
@router.get('/api/{apikey}')
async def api(apikey: str, db: db_session):
  with open('json/constrain.json') as f:
    constrain = json.load(f)
  print(constrain)
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  # user.battery = battery
  now = datetime.now()  # .replace(tzinfo=timezone.utc)
  user.lasttime = int(time.time())
  t = 0
  minutes = now.hour * 60 + now.minute + 180
  weekday = now.weekday()
  for i in user.schedule:
    if i[1] < minutes < i[2] and i[3][weekday]:
      for j in i[0]:
        # if j == 'sleep':
        #   t = 120
        #   break
        if j not in constrain and constrain:
          continue
        if j not in user.oldpins:
          user.oldpins[j] = 0
        if user.pins[j] - user.oldpins[j] > 5:  # Против многозадачности и "кручения"
          t += (user.pins[j] - user.oldpins[j]) * 2
          user.oldpins[j] = user.pins[j]
        elif user.pins[j] < user.oldpins[j]:  # Для обнуляющихся значений
          user.oldpins[j] = user.pins[j]
      break
  user.lastpin = t
  if apikey in gestapo_disable and gestapo_disable[apikey] > now:
    t = (gestapo_disable[apikey] - now).total_seconds()
  t = 60 if t > 60 else t  # t = 120 if t > 120 else t
  if t == 0:
    user.oldpins['red'] += 1
  else:
    user.oldpins['red'] = 0
  # flag_modified(user, 'battery')
  # flag_modified(user, 'version')
  flag_modified(user, 'lasttime')
  flag_modified(user, 'lastpin')
  flag_modified(user, 'oldpins')
  db.commit()
  stat(user.username, now, t)
  return t


# # Вернуть информацию о пользователе
# @router.get('/user/{apikey}')
# async def user(apikey: str, db: db_session):
#   return


@router.get('/gestapo/{apikey}')
async def gestapo(apikey: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    user = db.query(models.User).filter(models.User.username == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  now = datetime.now()  # .replace(tzinfo=timezone.utc)
  if user.apikey in gestapo_disable and gestapo_disable[user.apikey] > now:
    return 0
  if (
    int(time.time()) - user.lasttime > user.lastpin + 20 or user.oldpins['red'] > 20
  ) and (
    10 * 60 < now.hour * 60 + now.minute + 180 < 24 * 60  # 23 * 60
    or (now.hour * 60 + now.minute + 180) % 1440 < 2 * 60  # 2 * 60
  ):
    return 1
  return 0


@router.post('/schedule')
async def schedule(content: API, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == content.apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  user.schedule = content.content
  flag_modified(user, 'schedule')
  db.commit()
  return content.content


@router.get('/apikey')
async def apikey():
  content = """
  <form action="/apikey" method="POST">
    <p>
      <label>Username</label>
      <br>
      <input type="text" required name="username" placeholder="Username">
    </p>
    <p>
      <label>Password</label>
      <br>
      <input type="password" required name="password" placeholder="Password">
    </p>
    <button type="submit">Обновить API ключ</button>
  </form>
  """
  return page('razvit.band get api key', content)
  # content = '''
  # <!doctype html>
  # <html lang="en">
  #   <head>
  #     <meta charset="utf-8">
  #     <meta name="viewport" content="width=device-width, initial-scale=1">
  #     <title>Bootstrap demo</title>
  #     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
  #   </head>
  #   <body>
  #     <div class="container">
  #       <br>
  #       <h1>Update API key</h5>
  #       <form action="/apikey" method="POST">
  #         <div class="mb-3">
  #           <label>Username</label>
  #           <input type="text" required class="form-control" name="username" placeholder="Username">
  #         </div>
  #         <div class="mb-3">
  #           <label>Password</label>
  #           <input type="password" required placeholder="Password" name="password" class="form-control">
  #         </div>
  #         <button type="submit" class="btn btn-primary">Submit</button>
  #       </form>
  #     </div>
  #     <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" crossorigin="anonymous"></script>
  #   </body>
  # </html>
  # '''
  # return HTMLResponse(content=content, status_code=200)


@router.post('/apikey')
async def apikey(user: user_dependency, db: db_session):
  db_user = db.query(models.User).filter(models.User.id == user['id']).first()
  if not db_user:
    raise HTTPException(status_code=404, detail='User not found')
  return {'apikey': db_user.apikey}


class Post(BaseModel):
  apikey: str
  content: dict


# Для отправки расписания
@router.post('/post')
async def post(content: Post, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == content.apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  user.extension_settings = content.content
  flag_modified(user, 'extension_settings')
  db.commit()
  return


def getTopExtension(db: db_session):
  channels = {}
  playlists = {}
  words = {}
  activeurl = {}
  videourl = {}
  audiourl = {}
  blackurl = {}
  for i in db.query(models.User):
    i = i.extension_settings
    for j in i.channels:
      channels[j] = channels.get(j) + 1
    for j in i.playlists:
      playlists[j] = playlists.get(j) + 1
    for j in i.words:
      words[j] = words.get(j) + 1
    for j in i.activeurl:
      activeurl[j] = activeurl.get(j) + 1
    for j in i.videourl:
      videourl[j] = videourl.get(j) + 1
    for j in i.audiourl:
      audiourl[j] = audiourl.get(j) + 1
    for j in i.blackurl:
      blackurl[j] = blackurl.get(j) + 1
  data = {
    'channels': sorted(channels.items(), key=lambda i: i[1])[:10],
    'playlists': sorted(channels.items(), key=lambda i: i[1])[:10],
    'words': sorted(channels.items(), key=lambda i: i[1])[:10],
    'activeurl': sorted(channels.items(), key=lambda i: i[1])[:10],
    'videourl': sorted(channels.items(), key=lambda i: i[1])[:10],
    'audiourl': sorted(channels.items(), key=lambda i: i[1])[:10],
    'blackurl': sorted(channels.items(), key=lambda i: i[1])[:10],
  }
  return data

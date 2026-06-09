import requests
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

import models
from config import YT_API_KEY
from database import db_session
from page import page
from routers.auth import user_dependency
from utils import amount

router = APIRouter(prefix='/youtube', tags=['youtube'])
templates = Jinja2Templates(directory='templates')


@router.get('')
async def channels_page(request: Request):
  return templates.TemplateResponse(
    request=request,
    name='youtube.html',
    context={'title': 'Educational YouTube Channels'},
  )


@router.get('/old')
async def channels(db: db_session):
  channels = db.query(models.Channel).all()

  m = [i.__dict__ for i in channels]
  m.sort(key=lambda i: i['subs'], reverse=True)

  x = f"""
  <form action="/youtube/add" method="POST">
    <input placeholder="Channel ID" name="channel" required>
    <select name="lang">
      <option value="ru">RU</option>
      <option value="en">EN</option>
      <option value="es">ES</option>
      <option value="de">DE</option>
      <option value="fr">FR</option>
      <option value="pt">PT</option>
    </select>
    <input placeholder="Tags" name="tags">
    <input type="submit">
  </form>
  <p>Список из {len(m)} образовательных и научно-популярных каналов. {len(list(filter(lambda i: i['lang'] == 'ru', m)))} русскоязычных, {len(list(filter(lambda i: i['lang'] == 'en', m)))} ангоязычных, {len(list(filter(lambda i: i['lang'] not in ['ru', 'en'], m)))} других.</p>
  <p><a href="/youtube/youtube.json">Скачать список каналов в формате JSON</a><p>
  """

  lang = {
    'ru': '🇷🇺',
    'en': '🇺🇸',  # 🇬🇧
    'es': '🇪🇸',
    'de': '🇩🇪',
    'fr': '🇫🇷',
    'pt': '🇧🇷',
  }

  colors = {
    'JavaScript': 'gold',
    'CSS': '#1cb0f6',
    'HTML': '#ff9600',
    'Python': '#2b70c9',
    'Photoshop': '#2b70c9',
    'Illustrator': '#ff9600',
    'Premiere': '#ce82ff',
    'ОГЭ': '#ff4b4b',
    'ЕГЭ': '#ff4b4b',
  }
  for i in m:
    x += f'''<tr>
      <th><a href="{i['url']}" target="_blank"><img src="{i['icon_medium']}" width="40" height="40" style="margin-bottom: 0 !important; border-radius: 50% !important;"></a></th>
      <th><a href="/youtube/{i['id']}" target="_blank">{i['title']}</a></th>
      <th>{amount(i['subs'])}</th>
      <th>{amount(i['views'])}</th>
      <th>{i['video_count']}</th>
      <th>{lang[i['lang']]}</th>
      <th style="max-width: 120px;">{' '.join(['<span class="badge" style="background-color: ' + colors.get(i, 'grey') + '";>' + i + '</span>' for i in i['tags']])}</th>
    </tr>'''

  content = f"""
  <h1>List of educational YouTube channels</h1>
  <table>
    <tr>
      <th></th>
      <th>Channel</th>
      <th>Subs</th>
      <th>Views</th>
      <th>Videos</th>
      <th>Lang</th>
      <th>Tags</th>
    </tr>
    {x}
  </table>
  """
  style = """<style>
  body{max-width:1200px !important}
  .badge {
    background-color: grey;
    color: white;
    padding: 2px 6px;
    text-align: center;
    border-radius: 5px;
    font-size: 10px;
    line-height: 20px;
  }
  </style>
  """
  return page('youtube.channels', content, style)


@router.post('/add')
async def channel_add(
  user: user_dependency, db: db_session, channel=Form(), lang=Form(), tags=Form('')
):
  print(user)
  if user is None:
    raise HTTPException(status_code=401)
  try:
    if '/channel/' in channel:
      ytid = channel[-24:]
      info = requests.get(
        f'https://youtube.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={ytid}&key={YT_API_KEY}'
      ).json()
    else:
      return RedirectResponse('/youtube', status_code=302)
    stat = info['items'][0]['statistics']
    icon = info['items'][0]['snippet']['thumbnails']
    ytid = info['items'][0]['id']

    channel = models.Channel(
      id=ytid,
      url='https://www.youtube.com/channel/' + ytid,
      title=info['items'][0]['snippet']['title'],
      views=int(stat['viewCount']),
      subs=int(stat['subscriberCount']),
      video_count=int(stat['videoCount']),
      lang=lang,
      icon_default=icon['default']['url'],
      icon_medium=icon['medium']['url'],
      icon_high=icon['high']['url'],
      tags=tags.split(',') if tags else [],
      user_id=user['id'],
    )
    db.add(channel)
    db.commit()
    return {'added_channel': info['items'][0]['snippet']['title']}
  except Exception as e:
    print(channel, e)
  return RedirectResponse('/youtube', status_code=302)


@router.get('/channels.json')
async def channels_json(db: db_session):
  return db.query(models.Channel).all()


@router.get('/{channel_id}')
async def channel_info(db: db_session, channel_id):
  channel_data = (
    db.query(models.Channel).filter(models.Channel.id == channel_id).first().__dict__
  )
  content = (
    f'''<table><tr>
        <th><a href="{channel_data['url']}" target="_blank"><img src="{channel_data['icon_medium']}" width="40" height="40" style="margin-bottom: 0 !important; border-radius: 50% !important;"></a></th>
        <th><a href="{channel_data['url']}" target="_blank">{channel_data['title']}</a></th>
        <th>{amount(channel_data['subs'])}</th>
        <th>{amount(channel_data['views'])}</th>
        <th>{channel_data['video_count']}</th>
        <th>{','.join(channel_data['tags'])}</th>
      </tr></table>'''
    + f'''<form action="/youtube/add" method="POST">
      <input placeholder="Channel ID" name="channel" required value="{channel_data['url']}">
      <select name="lang">
        <option value="ru" {'selected' if channel_data['lang'] == 'ru' else ''}>RU</option>
        <option value="en" {'selected' if channel_data['lang'] == 'en' else ''}>EN</option>
        <option value="es" {'selected' if channel_data['lang'] == 'es' else ''}>ES</option>
        <option value="de" {'selected' if channel_data['lang'] == 'de' else ''}>DE</option>
        <option value="fr" {'selected' if channel_data['lang'] == 'fr' else ''}>FR</option>
        <option value="pt" {'selected' if channel_data['lang'] == 'pt' else ''}>PT</option>
      </select>
      <input placeholder="Tags" name="tags" value="{','.join(channel_data['tags'])}">
      <input type="submit">
    </form>'''
  )
  return page(channel_id, content)

import datetime
import json
import time

import requests
from fastapi import APIRouter, BackgroundTasks, Form, HTTPException
from fastapi.responses import (
  FileResponse,
  HTMLResponse,
  PlainTextResponse,
  RedirectResponse,
)
from pytube import YouTube

import models
from config import YT_API_KEY
from database import db_session
from page import page
from routers.auth import user_dependency
from utils import amount

# from fastapi_utils.tasks import repeat_every

router = APIRouter(prefix='/youtube', tags=['youtube'])

# counter = 0
# @router.on_event("startup")
# @repeat_every(seconds=1, wait_first=True)
# def periodic():
#   global counter
#   print('counter is', counter)
#   counter += 1


@router.get('')
async def channels(db: db_session):
  with open('json/youtube-stats.json') as f:
    stats = json.load(f)
  with open('json/youtube.json') as f:
    m = json.load(f)
    # m.sort(key=lambda i: i['subs'], reverse=True)
  # m = [i | {'stats': stats[i['id']]['2024-02-19']['views'] - stats[i['id']]['2024-02-17']['views']} for i in m]
  # m = [i | {'stats': stats[i['id']]['2024-02-19']['views'] - stats[i['id']].get('2024-02-12', stats[i['id']]['2024-02-17'])['views']} for i in m]
  n_days = 7
  for i in range(len(m)):
    try:
      start = stats[m[i]['id']][
        str(datetime.date.today() - datetime.timedelta(days=1))
      ]['views']  # '2024-02-24'
      end = stats[m[i]['id']][
        str(datetime.date.today() - datetime.timedelta(days=(n_days + 1)))
      ]['views']  # '2024-02-12'
    except:
      start = 0
      end = 0
    m[i] = m[i] | {'stats': (start - end) // n_days}  # 12
  m.sort(key=lambda i: (i['stats'], i['subs']), reverse=True)

  # mas = set()
  # mm = []
  # for i in range(len(m)):
  #   if m[i]['id'] not in mas and m[i]['subs'] >= 1000:
  #     mm += [m[i]]
  #     mas.add(m[i]['id'])
  # m = mm

  # <select name="category">
  #   <optgroup label="Научпоп">
  #     <option value="popsci">Научпоп</option>
  #   </optgroup>
  #   <optgroup label="Образование">
  #     <option value="edu">Образование</option>
  #   </optgroup>
  # </select>

  # multiple

  x = f"""
  <form action="/youtube-add" method="POST">
    <input placeholder="Channel ID" name="channel" required>
    <select name="lang">
      <option value="ru">RU</option>
      <option value="en">EN</option>
      <option value="es">ES</option>
      <option value="de">DE</option>
      <option value="fr">FR</option>
      <option value="pt">PT</option>
    </select>
    <select name="category">
      <option value="popsci">Научпоп</option>
      <option value="edu">Образование</option>
    </select>
    <select name="theme">
      <option value="all">Разное</option>
      <option value="it">IT</option>
      <option value="programming">Программирование</option>
      <option value="physics">Физика</option>
      <option value="chemistry">Химия</option>
      <option value="space">Космос</option>
      <option value="math">Математика</option>
      <option value="history">История</option>
      <option value="biology">Биология</option>
      <option value="medicine">Медицина</option>
      <option value="geography">География</option>
      <option value="electronics">Электроника</option>
      <option value="social">Обществознание</option>
      <option value="economics">Экономика</option>
      <option value="english">Английский</option>
    </select>
    <input placeholder="Tags" name="tags">
    <input type="submit">
  </form>
  <p>Список из {len(m)} образовательных и научно-популярных каналов. {len(list(filter(lambda i: i['lang'] == 'ru', m)))} русскоязычных, {len(list(filter(lambda i: i['lang'] == 'en', m)))} ангоязычных, {len(list(filter(lambda i: i['lang'] not in ['ru', 'en'], m)))} других.</p>
  <p>В данном случае научпоп понимается в широком смыле, включающем в себя познавательно-развлекательный контент.<br>Образование означает, что нужно взять ручку и бумагу или ноутбук, чтобы полноценно освоить материал.</p>
  <p><a href="/youtube/youtube.json">Скачать список каналов в формате JSON</a><p>
  <p><a href="/youtube/youtube-stats.json">Скачать статистику каналов в формате JSON</a><p>
  <details>
    <summary>Возможные значения</summary>
    <p>
    lang:
      'ru': '🇷🇺',
      'en': '🇺🇸',
      'es': '🇪🇸',
      'de': '🇩🇪',
      'fr': '🇫🇷',
      'pt': '🇧🇷'
    </p>
    <p>
    category:
      'popsci': 'Научпоп',
      'edu': 'Образование'
    </p>
    <p>
    theme:
      'all': 'Разное',
      'it': 'IT',
      'programming': 'Программирование',
      'physics': 'Физика',
      'chemistry': 'Химия',
      'space': 'Космос',
      'math': 'Математика',
      'history': 'История',
      'biology': 'Биология',
      'medicine': 'Медицина',
      'geography': 'География',
      'electronics': 'Электроника',
      'social': 'Обществознание',
      'economics': 'Экономика',
      'english': 'Английский',
    </p>
  </details>
  """

  lang = {
    'ru': '🇷🇺',
    'en': '🇺🇸',  # 🇬🇧
    'es': '🇪🇸',
    'de': '🇩🇪',
    'fr': '🇫🇷',
    'pt': '🇧🇷',
  }
  category = {'popsci': 'Научпоп', 'edu': 'Образование'}
  theme = {
    'all': 'Разное',
    'it': 'IT',
    'programming': 'Программирование',
    'physics': 'Физика',
    'chemistry': 'Химия',
    'space': 'Космос',
    'math': 'Математика',
    'history': 'История',
    'biology': 'Биология',
    'medicine': 'Медицина',
    'geography': 'География',
    'electronics': 'Электроника',
    'social': 'Обществознание',
    'economics': 'Экономика',
    'english': 'Английский',
  }

  # <th><a href="{i['url']}" target="_blank">{i['title']}</a></th>
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
      <th><a href="{i['url']}" target="_blank"><img src="{i['icon']['medium']}" width="40" height="40" style="margin-bottom: 0 !important; border-radius: 50% !important;"></a></th>
      <th><a href="/youtube/{i['id']}" target="_blank">{i['title']}</a></th>
      <th>{amount(i['stats'])}</th>
      <th>{amount(i['subs'])}</th>
      <th>{amount(i['views'])}</th>
      <th>{i['videos']}</th>
      <th>{lang[i['lang']]}</th>
      <th>{category[i['category']]}</th>
      <th>{theme[i['theme']]}</th>
      <th style="max-width: 120px;">{' '.join(['<span class="badge" style="background-color: ' + colors.get(i, 'grey') + '";>' + i + '</span>' for i in i['tags']])}</th>
    </tr>'''
    # ','.join(i['tags'])

  # Subscribers -> Subs
  content = f"""
  <h1>List of educational YouTube channels</h1>
  <table>
    <tr>
      <th></th>
      <th>Channel</th>
      <th>7 days</th>
      <th>Subs</th>
      <th>Views</th>
      <th>Videos</th>
      <th>Lang</th>
      <th>Category</th>
      <th>Theme</th>
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
  return page('razvit.youtube.channels', content, style)  # 1100px


# Добавить кнопку в расширение для браузера
# <link rel="canonical" href="https://www.youtube.com/channel/UCHnyfMqiRRG1u-2MsSQLbXA">
# <meta property="og:url" content="https://www.youtube.com/channel/UCHnyfMqiRRG1u-2MsSQLbXA">
# <meta itemprop="identifier" content="UCHnyfMqiRRG1u-2MsSQLbXA">
# document.querySelector("meta[property='og:url']").getAttribute("content")
@router.post('/add')
async def yt_add(
  user: user_dependency, db: db_session, channel=Form(), lang=Form(), tags=Form('')
):  # channel : str
  # , category=Form(), theme=Form()

  # if '/c/' in url:
  #   username = url[url.find('/c/') + 3:]
  #   continue
  # if '/user/' in url:
  #   username = url[url.find('/user/') + 6:]
  #   continue
  print(user)
  if user is None:
    raise HTTPException(status_code=401)
  try:
    if '/channel/' in channel:
      ytid = channel[-24:]
      info = requests.get(
        f'https://youtube.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={ytid}&key={YT_API_KEY}'
      ).json()
    # if '@' in channel:
    #   channel = channel[channel.find('@') + 1:]
    #   info = requests.get(f'https://youtube.googleapis.com/youtube/v3/channels?part=statistics,snippet&forUsername={channel}&key={YT_API_KEY}').json()
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

    # m = {
    #   'id': ytid,
    #   'url': 'https://www.youtube.com/channel/' + ytid,
    #   'title': info['items'][0]['snippet']['title'],
    #   'views': int(stat["viewCount"]),
    #   'subs': int(stat["subscriberCount"]),
    #   'videos': int(stat["videoCount"]),
    #   'lang': lang,
    #   'category': category,
    #   'theme': theme,
    #   'icon': {
    #     'default': icon['default']['url'],
    #     'medium': icon['medium']['url'],
    #     'high': icon['high']['url']
    #   },
    #   'tags': tags.split(',') if tags else []
    # }
    # print(m)
    # with open('json/youtube.json') as f:
    #   mas = json.load(f)
    # if m['id'] not in [i['id'] for i in mas]:
    #   with open('json/youtube.json', 'w', encoding='utf-8') as f:
    #     json.dump(mas + [m], f, ensure_ascii=False, indent=2)
    # else: # Возможность редактировать
    #   with open('json/youtube.json', 'w', encoding='utf-8') as f:
    #     for i in range(len(mas)):
    #       if m['id'] == mas[i]['id']:
    #         mas[i] = m
    #         break
    #     json.dump(mas, f, ensure_ascii=False, indent=2)
  except Exception as e:
    print(channel, e)
  return RedirectResponse('/youtube', status_code=302)


@router.get('/{channel_id}')
async def channel_info(channel_id):
  with open('json/youtube-stats.json') as f, open('json/youtube.json') as data:
    m = json.load(f)
    views = ''
    subs = ''
    videos = ''
    # for i in m[channel_id]:
    #   views += f'["{i}", {m[channel_id][i]["views"]}],'
    #   subs += f'["{i}", {m[channel_id][i]["subs"]}],'
    #   videos += f'["{i}", {m[channel_id][i]["videos"]}],'
    x = m.get(channel_id, [])
    # for i in range(1, len(x)):
    #   views += f'["{x[i]}", {x[i - 1]["views"] - x[i]["views"]}],'
    #   subs += f'["{x[i]}", {x[i - 1]["subs"] - x[i]["subs"]}],'
    #   videos += f'["{x[i]}", {x[i - 1]["videos"] - x[i]["videos"]}],'
    last_views = None
    for i in x:
      if last_views is not None:
        views += f'["{i}", {x[i]["views"] - last_views}],'
        # subs += f'["{i}", {x[i]["subs"] - last_subs}],'
        # videos += f'["{i}", {x[i]["videos"] - last_videos}],'
        subs += f'["{i}", {x[i]["subs"]}],'
        videos += f'["{i}", {x[i]["videos"]}],'
      last_views = x[i]['views']
      # last_subs = x[i]["subs"]
      # last_videos = x[i]["videos"]
    # style="max-width:700px; height:400px"

    data = json.load(data)
    channel_data = None
    for i in data:
      if i['id'] == channel_id:
        channel_data = i
        break

    content = (
      f'''<table><tr>
          <th><a href="{channel_data['url']}" target="_blank"><img src="{channel_data['icon']['medium']}" width="40" height="40" style="margin-bottom: 0 !important; border-radius: 50% !important;"></a></th>
          <th><a href="{channel_data['url']}" target="_blank">{channel_data['title']}</a></th>
          <th>{amount(channel_data['subs'])}</th>
          <th>{amount(channel_data['views'])}</th>
          <th>{channel_data['videos']}</th>
          <th>{','.join(channel_data['tags'])}</th>
        </tr></table>'''
      + f'''<form action="/youtube-add" method="POST">
        <input placeholder="Channel ID" name="channel" required value="{channel_data['url']}">
        <select name="lang">
          <option value="ru" {'selected' if channel_data['lang'] == 'ru' else ''}>RU</option>
          <option value="en" {'selected' if channel_data['lang'] == 'en' else ''}>EN</option>
          <option value="es" {'selected' if channel_data['lang'] == 'es' else ''}>ES</option>
          <option value="de" {'selected' if channel_data['lang'] == 'de' else ''}>DE</option>
          <option value="fr" {'selected' if channel_data['lang'] == 'fr' else ''}>FR</option>
          <option value="pt" {'selected' if channel_data['lang'] == 'pt' else ''}>PT</option>
        </select>
        <select name="category">
          <option value="popsci" {'selected' if channel_data['category'] == 'popsci' else ''}>Научпоп</option>
          <option value="edu" {'selected' if channel_data['category'] == 'edu' else ''}>Образование</option>
        </select>
        <select name="theme">
          <option value="all" {'selected' if channel_data['theme'] == 'popsci' else ''}>Разное</option>
          <option value="it" {'selected' if channel_data['theme'] == 'it' else ''}>IT</option>
          <option value="programming" {'selected' if channel_data['theme'] == 'programming' else ''}>Программирование</option>
          <option value="physics" {'selected' if channel_data['theme'] == 'physics' else ''}>Физика</option>
          <option value="chemistry" {'selected' if channel_data['theme'] == 'chemistry' else ''}>Химия</option>
          <option value="space" {'selected' if channel_data['theme'] == 'space' else ''}>Космос</option>
          <option value="math" {'selected' if channel_data['theme'] == 'math' else ''}>Математика</option>
          <option value="history" {'selected' if channel_data['theme'] == 'history' else ''}>История</option>
          <option value="biology" {'selected' if channel_data['theme'] == 'biology' else ''}>Биология</option>
          <option value="medicine" {'selected' if channel_data['theme'] == 'medicine' else ''}>Медицина</option>
          <option value="geography" {'selected' if channel_data['theme'] == 'geography' else ''}>География</option>
          <option value="electronics" {'selected' if channel_data['theme'] == 'electronics' else ''}>Электроника</option>
          <option value="social" {'selected' if channel_data['theme'] == 'social' else ''}>Обществознание</option>
          <option value="economics" {'selected' if channel_data['theme'] == 'economics' else ''}>Экономика</option>
          <option value="english" {'selected' if channel_data['theme'] == 'english' else ''}>Английский</option>
        </select>
        <input placeholder="Tags" name="tags" value="{','.join(channel_data['tags'])}">
        <input type="submit">
      </form>'''
    )
    if last_views is not None:
      content += (
        """
      <div id="myChartViews" style="height:400px"></div>
      <div id="myChartSubs" style="height:400px"></div>
      <div id="myChartVideos" style="height:400px"></div>
      <script src="https://www.gstatic.com/charts/loader.js"></script>

      <script>
      google.charts.load('current',{packages:['corechart']});

      google.charts.setOnLoadCallback(drawChartViews);
      google.charts.setOnLoadCallback(drawChartSubs);
      google.charts.setOnLoadCallback(drawChartVideos);

      function drawChartViews() {
        const data = google.visualization.arrayToDataTable([
          ['Date', 'Views'],"""
        + views
        + """
          ]);
        const options = {
          title: 'Views Info',
          hAxis: {title: 'Views'},
          vAxis: {title: 'Date'},
          legend: 'none'
        };
        const chart = new google.visualization.LineChart(document.getElementById('myChartViews'));
        chart.draw(data, options);
      }

      function drawChartSubs() {
        const data = google.visualization.arrayToDataTable([
          ['Date', 'Subs'],"""
        + subs
        + """
          ]);
        const options = {
          title: 'Subs Info',
          hAxis: {title: 'Subs'},
          vAxis: {title: 'Date'},
          legend: 'none'
        };
        const chart = new google.visualization.LineChart(document.getElementById('myChartSubs'));
        chart.draw(data, options);
      }

      function drawChartVideos() {
        const data = google.visualization.arrayToDataTable([
          ['Date', 'Videos'],"""
        + videos
        + """
          ]);
        const options = {
          title: 'Videos Info',
          hAxis: {title: 'Videos'},
          vAxis: {title: 'Date'},
          legend: 'none'
        };
        const chart = new google.visualization.LineChart(document.getElementById('myChartVideos'));
        chart.draw(data, options);
      }
      </script>
    """
      )
    # LineChart -> ColumnChart, AreaChart, curveType: 'function',
    return page(channel_id, content)


@router.get('/full/{date}')
async def channel_info(date):
  with open('json/youtube-stats.json') as f, open('json/youtube.json') as channels_file:
    m = json.load(f)
    channels = json.load(channels_file)
    views = ''
    subs = ''
    videos = ''

    # m_views = {}
    # m_subs = {}
    # m_videos = {}
    # for x in m:
    #   x = m[x]
    #   if date in x:
    #     for i in x:
    #       if i >= date:
    #         m_views[i] = x[i]["views"] + m_views.get(i, 0)
    #         m_subs[i] = x[i]["views"] + m_subs.get(i, 0)
    #         m_videos[i] = x[i]["views"] + m_videos.get(i, 0)

    channels_data = {
      i['id']: {'lang': i['lang'], 'category': i['category'], 'theme': i['theme']}
      for i in channels
    }

    r = {}
    for x in m:
      if channels_data[x]['lang'] == 'ru':
        x = m[x]
        if date in x:
          for i in x:
            if i >= date:
              r[i] = r.get(i, {})
              r[i]['views'] = x[i]['views'] + r[i].get('views', 0)
              r[i]['subs'] = x[i]['subs'] + r[i].get('subs', 0)
              r[i]['videos'] = x[i]['videos'] + r[i].get('videos', 0)

    last_views = None
    last_subs = None
    last_videos = None
    x = r
    for i in x:
      if last_views is not None:
        views += f'["{i}", {x[i]["views"] - last_views}],'
        subs += f'["{i}", {x[i]["subs"] - last_subs}],'
        videos += f'["{i}", {x[i]["videos"] - last_videos}],'
      last_views = x[i]['views']
      last_subs = x[i]['subs']
      last_videos = x[i]['videos']

    # last_views = None
    # for i in x:
    #   if last_views is not None:
    #     views += f'["{i}", {m_views[i] - last_views}],'
    #     subs += f'["{i}", {m_subs[i] - last_subs}],'
    #     videos += f'["{i}", {m_videos[i] - last_videos}],'
    #   last_views = m_views[i]
    #   last_subs = m_subs[i]
    #   last_videos = m_videos[i]

    content = (
      """
      <div id="myChartViews" style="height:400px"></div>
      <div id="myChartSubs" style="height:400px"></div>
      <div id="myChartVideos" style="height:400px"></div>
      <script src="https://www.gstatic.com/charts/loader.js"></script>

      <script>
      google.charts.load('current',{packages:['corechart']});

      google.charts.setOnLoadCallback(drawChartViews);
      google.charts.setOnLoadCallback(drawChartSubs);
      google.charts.setOnLoadCallback(drawChartVideos);

      function drawChartViews() {
        const data = google.visualization.arrayToDataTable([
          ['Date', 'Views'],"""
      + views
      + """
          ]);
        const options = {
          title: 'Views Info',
          hAxis: {title: 'Views'},
          vAxis: {title: 'Date'},
          legend: 'none'
        };
        const chart = new google.visualization.LineChart(document.getElementById('myChartViews'));
        chart.draw(data, options);
      }

      function drawChartSubs() {
        const data = google.visualization.arrayToDataTable([
          ['Date', 'Subs'],"""
      + subs
      + """
          ]);
        const options = {
          title: 'Subs Info',
          hAxis: {title: 'Subs'},
          vAxis: {title: 'Date'},
          legend: 'none'
        };
        const chart = new google.visualization.LineChart(document.getElementById('myChartSubs'));
        chart.draw(data, options);
      }

      function drawChartVideos() {
        const data = google.visualization.arrayToDataTable([
          ['Date', 'Videos'],"""
      + videos
      + """
          ]);
        const options = {
          title: 'Videos Info',
          hAxis: {title: 'Videos'},
          vAxis: {title: 'Date'},
          legend: 'none'
        };
        const chart = new google.visualization.LineChart(document.getElementById('myChartVideos'));
        chart.draw(data, options);
      }
      </script>
    """
    )
    # LineChart -> ColumnChart, AreaChart, curveType: 'function',
    return page('Full Stats', content)


@router.get('/youtube.json')
async def youtube_json():
  return FileResponse('json/youtube.json')


@router.get('/youtube-stats.json')
async def youtube_stats_json():
  return FileResponse('youtube-stats.json')


@router.get('/allvideos.json')
async def allvideos_json():
  return FileResponse('json/allvideos.json')


def watch_update_func():
  with open('json/youtube.json') as f:
    m_id = [
      i['id'] for i in sorted(json.load(f), key=lambda i: i['subs'], reverse=True)
    ]
    # m_id = [i['id'] for i in sorted(filter(lambda i: i['category'] == 'popsci' and i['lang'] == 'ru', json.load(f)), key=lambda i: i['subs'])]
    # m_id = m_id[:5]
  r = []
  for channel_id in m_id:
    maxResults = 50  # 10
    channel = requests.get(
      f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={YT_API_KEY}'
    ).json()
    uploads = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    videos = requests.get(
      f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults={maxResults}&playlistId={uploads}&key={YT_API_KEY}'
    ).json()
    # with open('allvideosfull.json', 'w') as f:
    #   json.dump(videos, f, indent=2)
    for m in videos['items']:
      try:
        m = m['snippet']

        yt = YouTube('https://www.youtube.com/watch?v=' + m['resourceId']['videoId'])

        if m['resourceId']['kind'] == 'youtube#video' and yt.length > 120:
          r += [
            {
              'title': m['title'],
              'videoId': m['resourceId']['videoId'],
              'channelTitle': m['channelTitle'],
              'channelId': m['channelId'],
              'publishedAt': m['publishedAt'],
              'thumbnail': m['thumbnails'][
                'maxres' if 'maxres' in m['thumbnails'] else 'medium'
              ]['url'],  # в остальных чёрные полосы
              'length': yt.length,
              'views': yt.views,
            }
          ]
      except:
        ...
    # Дозапись в файл вместо одной записи в конце
    with open('json/allvideos.json', 'w') as f:
      r.sort(
        key=lambda i: datetime.datetime.fromisoformat(i['publishedAt'][:-1]),
        reverse=True,
      )
      json.dump(r, f, indent=2)


@router.get('/watch-update')
async def watch_update(background_tasks: BackgroundTasks):
  background_tasks.add_task(watch_update_func)
  return PlainTextResponse('Watch update...')


@router.get('/watch')
async def watch(
  lang: str = None,
  category: str = None,
  theme: str = None,
  days: int = 90,
  views: int = 10000,
  videos: int = 1000,
):
  content = """<form action="/watch" method="GET">
    <select name="lang">
      <option value="every">Все</option>
      <option value="ru">RU</option>
      <option value="en">EN</option>
      <option value="es">ES</option>
      <option value="de">DE</option>
      <option value="fr">FR</option>
      <option value="pt">PT</option>
    </select>
    <select name="category">
      <option value="every">Все</option>
      <option value="popsci">Научпоп</option>
      <option value="edu">Образование</option>
    </select>
    <select name="theme">
      <option value="every">Все</option>
      <option value="all">Разное</option>
      <option value="it">IT</option>
      <option value="programming">Программирование</option>
      <option value="physics">Физика</option>
      <option value="chemistry">Химия</option>
      <option value="space">Космос</option>
      <option value="math">Математика</option>
      <option value="history">История</option>
      <option value="biology">Биология</option>
      <option value="medicine">Медицина</option>
      <option value="geography">География</option>
      <option value="electronics">Электроника</option>
      <option value="social">Обществознание</option>
      <option value="economics">Экономика</option>
      <option value="english">Английский</option>
    </select>
    <input name="days" type="number" value=90>
    <input name="views" type="number" value=10000>
    <input name="videos" type="number" value=1000>
    <input type="submit">
  </form>
  <p><a href="/watch-update">Обновить данные</a></p>
  <p><a href="/json/allvideos.json">Скачать список видео в формате JSON</a><p>
  <div style="display: flex; flex-wrap: wrap; justify-content: space-between;">"""
  with open('json/allvideos.json') as f, open('json/youtube.json') as channels:
    channels = json.load(channels)
    channels = {
      i['id']: {'lang': i['lang'], 'category': i['category'], 'theme': i['theme']}
      for i in channels
    }

    m = json.load(f)
    m = list(filter(lambda i: i['views'] > views, m))
    m.sort(key=lambda i: i['views'], reverse=True)
    # m.sort(key=lambda i: i['views'] / ((datetime.datetime.now() - datetime.datetime.fromisoformat(i['publishedAt'][:-1])).days + 5), reverse=True) # просмотры с поправкой на время
    n = 0
    for i in m:
      diff = datetime.datetime.now() - datetime.datetime.fromisoformat(
        i['publishedAt'][:-1]
      )
      channel = channels[i['channelId']]
      if diff.days <= days and (
        (lang is None or lang == channel['lang'] or lang == 'every')
        and (category is None or category == channel['category'] or category == 'every')
        and (theme is None or theme == channel['theme'] or theme == 'every')
        and n < videos
      ):  # 30 90 180 365
        # width="500px"
        # content += f'''
        # <hr>
        # <p>
        #   <iframe src="https://www.youtube.com/embed/{i['videoId']}"></iframe>
        #   <a href="https://www.youtube.com/watch?v={i['videoId']}" target="_blank"><p>{i['title']}</p></a>
        #   <a href="https://www.youtube.com/channel/{i['channelId']}" target="_blank"><p>{i['channelTitle']}</p></a>
        #   <p>{diff}</p>
        # </p>
        # '''

        # 32%
        content += f"""
        <div style="width: 24%;">
        <a href="https://www.youtube.com/watch?v={i['videoId']}" target="_blank">
          <div style="position: relative">
            <img src={i['thumbnail']} style="margin-bottom: 0 !important; border-radius: 10px; width: 100%;">
            <span style="position: absolute; margin: 3px; padding: 0 4px; background-color: rgba(0, 0, 0, 0.8); border-radius: 3px; right: 0; bottom: 0; color: white;">
              {time.strftime(('%H:%M:%S' if i['length'] >= 3600 else '%M:%S'), time.gmtime(i['length'])).lstrip('0')}
            </span>
          </div>
          <b style="color: white;">{i['title']}</b>
        </a>
        <br>
        <a href="https://www.youtube.com/channel/{i['channelId']}" target="_blank" style="color: grey;">{i['channelTitle']}</a>
        <br>
        <p style="color: grey;">{amount(i['views'])} views • {diff.days} days ago</p>
        </div>
        """
        n += 1
  content += '</div>'
  return page('razvit.watch', content, '<style>body {max-width: 1200px;}</style>')


@router.get('/channels.txt')
async def channels():
  with open('json/youtube.json') as f:
    return PlainTextResponse('\n'.join([i['title'] for i in json.load(f)]))


@router.get('/player')
def youtube_player():
  content = """<video data-yt2html5="https://www.youtube.com/watch?v=ScMzIvxBSi4" controls></video>
  <script src="https://cdn.jsdelivr.net/gh/thelevicole/youtube-to-html5-loader@4.0.1/dist/YouTubeToHtml5.js"></script>
  <script>new YouTubeToHtml5();</script>"""
  return HTMLResponse(content)

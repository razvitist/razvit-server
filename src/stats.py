import datetime
import json
import time

import requests
import schedule
from pytz import timezone

from config import YT_API_KEY


def job():
  with open('json/youtube.json') as f:
    m = json.load(f)
  with open('json/youtube-stats.json') as f:
    x = {i['id']: {} for i in m} | json.load(f)
  # x = {i['id']: {} for i in m}
  # for i in x:
  #   print(i, end=' ')
  #   info = requests.get(f'https://youtube.googleapis.com/youtube/v3/channels?part=statistics&id={i}&key={YT_API_KEY}').json()
  #   stats = info['items'][0]['statistics']
  #   x[i][str(datetime.date.today())] = {'views': int(stats["viewCount"]), 'subs': int(stats["subscriberCount"]), 'videos': int(stats["videoCount"])}
  for j in range(len(m)):
    i = m[j]['id']
    print(i, end=' ')
    # f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={YT_API_KEY}'
    info = requests.get(
      f'https://youtube.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={i}&key={YT_API_KEY}'
    ).json()
    stats = info['items'][0]['statistics']
    x[i][str(datetime.date.today())] = {
      'views': int(stats['viewCount']),
      'subs': int(stats['subscriberCount']),
      'videos': int(stats['videoCount']),
    }
    icon = info['items'][0]['snippet']['thumbnails']
    m[j]['views'] = int(stats['viewCount'])
    m[j]['subs'] = int(stats['subscriberCount'])
    m[j]['videos'] = int(stats['videoCount'])
    m[j]['icon']['default'] = icon['default']['url']
    m[j]['icon']['medium'] = icon['medium']['url']
    m[j]['icon']['high'] = icon['high']['url']
  print()
  with open('json/youtube-stats.json', 'w') as f:
    json.dump(x, f, indent=2)
  with open('json/youtube.json', 'w') as f:
    json.dump(m, f, indent=2)


schedule.every().day.at('03:00', timezone('Europe/Moscow')).do(job)

while True:
  schedule.run_pending()
  time.sleep(1)

# @router.on_event("startup")
# @repeat_every(seconds=60*60*24, wait_first=True)
# def youtube_stats():
#   with open('json/youtube.json') as f:
#     m = json.load(f)
#   with open('json/youtube-stats.json') as f:
#     x = {i['id']: {} for i in m} | json.load(f)
#   # x = {i['id']: {} for i in m}
#   for i in x:
#     print(i, end=' ')
#     info = requests.get(f'https://youtube.googleapis.com/youtube/v3/channels?part=statistics&id={i}&key={YT_API_KEY}').json()
#     stats = info['items'][0]['statistics']
#     x[i][str(datetime.date.today())] = {'views': int(stats["viewCount"]), 'subs': int(stats["subscriberCount"]), 'videos': int(stats["videoCount"])}
#   print()
#   with open('json/youtube-stats.json', 'w') as f:
#     json.dump(x, f, indent=2)

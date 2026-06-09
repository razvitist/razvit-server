import requests
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import (
  FileResponse,
  HTMLResponse,
  PlainTextResponse,
  RedirectResponse,
)
from fastapi.templating import Jinja2Templates

import markdown
import models
from database import db_session
from page import page
from routers.auth import user_dependency

router = APIRouter(tags=['web'])

templates = Jinja2Templates(directory='templates')


@router.get('/')
async def home(request: Request):
  return templates.TemplateResponse(
    request=request, name='home.html', context={'title': 'band'}
  )


@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
  return FileResponse('resources/favicon.ico')


@router.get('/pages/{page_name}')
async def pages(db: db_session, request: Request, page_name: str):
  try:
    post = db.query(models.Post).filter(models.Post.slug == page_name.lower()).first()
    return templates.TemplateResponse(
      request=request,
      name='page.html',
      context={
        'content': markdown.markdown(
          post.content, extensions=['tables', 'toc', 'fenced_code']
        ),
        'head': '<style>img{max-height: 500px !important;}</style>',
        'title': post.title,
      },
    )
  except Exception as e:
    print(e)
    return page('Page not found', 'Page not found')


@router.get('/profile-data')
async def profile_data(user: user_dependency, db: db_session):
  if not user:
    raise HTTPException(status_code=401)
  user_db = (
    db.query(models.User).filter(models.User.username == user['username']).first()
  )
  user_db.password = None
  return user_db


@router.get('/profile')
async def profile(request: Request):
  return templates.TemplateResponse(
    request=request, name='profile.html', context={'title': 'Profile'}
  )


@router.get('/privacy')
async def privacy():
  with open('resources/privacy.txt') as f:
    return PlainTextResponse(f.read())


# with open('index.html') as f:
#   return page('razvit.band', f.read())
# '<style>img{max-height: 500px !important;}</style>'
# content = '''
#   <p><a href="/tutorial">Инструкция по использованию браслета</a></p>
#   <p><a href="/me">Личный кабинет</a></p>
#   <p><a href="/register">Регистрация</a></p>
#   <p><a href="/apikey">Обновить API ключ</a></p>
#   <p><a href="/docs">Документация</a></p>
# '''
# return page('razvit.band', content)

# @router.get('/tutorial')
# async def tutorial():
#   with open('markdown/tutorial.md') as f:
#     return page('razvit.band tutorial', markdown.markdown(f.read()), '<style>img{max-height: 500px !important;}</style>')

# @router.get('/pages/{page_name}')
# async def pages(request: Request, page_name: str):
#   try:
#     with open(f'markdown/{page_name}.md') as f:
#       return templates.TemplateResponse(
#         request=request, name='page.html', context={
#           'content': markdown.markdown(f.read(), extensions=['markdown.extensions.tables', 'toc']),
#           'head': '<style>img{max-height: 500px !important;}</style>',
#           'title': page_name
#         }
#       )
#       # return page(f'razvit.band {page_name}', markdown.markdown(f.read(), extensions=['markdown.extensions.tables']), '<style>img{max-height: 500px !important;}</style>')
#   except:
#     return page(f'Page not found', 'Page not found')

# @router.post('/profile')
# async def profile(db: db_session, username=Form(), password=Form()):
#   username = username.lower()
#   user = db.query(models.User).filter(models.User.username == username).first()
#   if user.username == username and user.password == password:
#     user.apikey = 'XXXXXXXXXX'
#     return user
#   return PlainTextResponse('Wrong password')


@router.post('/website-add')
async def website_add(website=Form()):
  with open('resources/websites.txt', 'a') as f:
    f.write('\n' + website)
  return RedirectResponse('/websites', status_code=302)


@router.get('/websites')
async def websites():
  with open('resources/websites.txt') as f:
    m = f.read().split('\n')
  content = """
  <form action="/website-add" method="POST">
    <input placeholder="Website URL" name="website" required>
    <input type="submit">
  </form>"""
  for i in m:
    if i.startswith('=') or not i:
      continue
    content += f"""
    <p>
      <a href="https://{i}" target="_blank" style="text-decoration: none"><img src="http://www.google.com/s2/favicons?domain={i}" style="margin-bottom: 0 !important"> {i}</a>
    </p>
    """
    # content += f'''<tr>
    #   <th><a href="{i['url']}" target="_blank"><img src="{i['icon']['medium']}" width="40" height="40" style="margin-bottom: 0 !important; border-radius: 50% !important;"></a></th>
    #   <th><a href="{i['url']}" target="_blank">{i['title']}</a></th>
    #   <th>{amount(i['subs'])}</th>
    #   <th>{amount(i['views'])}</th>
    #   <th>{i['videos']}</th>
    #   <th>{lang[i['lang']]}</th>
    #   <th>{category[i['category']]}</th>
    #   <th>{theme[i['theme']]}</th>
    # </tr>'''
  return page('razvit.websites', content)


@router.get('/websites.txt')
async def websites():
  return FileResponse('resources/websites.txt')


@router.get('/words')
async def words():
  return FileResponse('resources/words.txt')


# mini apps
@router.get('/text-editor')
async def texteditor():
  content = ''
  return HTMLResponse(content=content, status_code=200)


@router.get('/code-editor')
async def codeeditor():
  content = ''
  return HTMLResponse(content=content, status_code=200)


@router.get('/iframe')
async def iframe():
  content = requests.get('https://www.w3schools.com/html/html_colors.asp').content
  #   content = '''<!DOCTYPE html>
  # <html lang="en">
  # <head>
  #   <meta charset="UTF-8">
  #   <meta name="viewport" content="width=device-width, initial-scale=1.0">
  #   <title>Document</title>
  #   <style>
  #     body {
  #       margin: 0;
  #       padding: 0;
  #     }
  #     iframe{
  #       display: block;  /* iframes are inline by default */
  #       height: 80vh;  /* Set height to 100% of the viewport height */
  #       width: 100vw;  /* Set width to 100% of the viewport width */
  #       border: none; /* Remove default border */
  #     }
  #   </style>
  # </head>
  # <body>
  #   <center>
  #     <iframe src="https://razvit.org" frameborder="0"></iframe>
  #   </center>
  #   <script>
  #     addEventListener("mousemove", (event) => {console.log('move')})
  #     var iframe = document.querySelector('iframe')
  #     // iframe.contentDocument.body.addEventListener("mousemove", (event) => {alert('works')})
  #     // iframe.contentDocument.body.remove()
  #     setInterval(() => {
  #       var elmnt = iframe.contentWindow.document.querySelector("h1");
  #       elmnt.style.display = "none";
  #     }, 1000)
  #   </script>
  # </body>
  # </html>
  #   '''
  return HTMLResponse(content=content, status_code=200)


@router.get('/register')
async def register(request: Request):
  return templates.TemplateResponse(
    request=request, name='register.html', context={'title': 'Register'}
  )


@router.get('/login')
async def login(request: Request):
  return templates.TemplateResponse(
    request=request, name='login.html', context={'title': 'Login'}
  )

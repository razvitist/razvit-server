from fastapi.responses import HTMLResponse


def page(title, content, head=''):
  # <a href="https://band.razvit.org/youtube">channels</a> /
  # <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
  # <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/dark.css">
  # <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/light.css">
  # <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@exampledev/new.css@1/new.min.css">
  # <nav>
  #         <a href="https://razvit.org">razvit.org</a> /
  #         <a href="https://band.razvit.org">razvit.band</a> /
  #         <a href="https://band.razvit.org/tutorial">tutorial</a> /
  #         <a href="https://t.me/razvit" target="_blank">telegram</a>
  #       </nav>

  # <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@exampledev/new.css@1/new.min.css">
  # <article class="markdown-body"> </article>
  return HTMLResponse(
    content=f"""<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  {head}
</head>
<body>
  <div class="container">

  <header class="d-flex flex-wrap justify-content-center py-3 mb-4 border-bottom">
    <a href="/" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto link-body-emphasis text-decoration-none">
      <img class="bi me-2" width="40" height="32" src="/static/img/logo.svg">
      <!-- <svg class="bi me-2" width="40" height="32"><use xlink:href="/static/img/logo.svg"></use></svg> -->
      <span class="fs-4">band.razvit</span>
    </a>
    <ul class="nav nav-pills">
      <li class="nav-item"><a href="/" class="nav-link link-body-emphasis" aria-current="page">Главная</a></li>
      <li class="nav-item"><a href="#" class="nav-link link-body-emphasis">Купить</a></li>
      <li class="nav-item"><a href="/pages/tutorial" class="nav-link link-body-emphasis">Инструкция</a></li>
      <li class="nav-item"><a href="#" class="nav-link link-body-emphasis">Применения</a></li>
      <!-- <li class="nav-item"><a href="#" class="nav-link link-body-emphasis">Статьи</a></li> -->
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle link-body-emphasis" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
          Статьи
        </a>
        <ul class="dropdown-menu">
          <li><a class="dropdown-item" href="#">Ошибки</a></li>
          <li><a class="dropdown-item" href="#">Ремешок</a></li>
        </ul>
      </li>
      <li class="nav-item"><a href="#" class="nav-link link-body-emphasis">Войти</a></li>
    </ul>
  </header>
  {content}
  <footer class="d-flex flex-wrap justify-content-center align-items-center py-5 mb-2 mt-5 border-top">
    <a href="/"><img class="bi me-2" width="40" height="32" src="/static/img/logo.svg"></a>
    <p class="mb-0 text-body-secondary">© 2025 band.razvit</p>
  </footer>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
</body>
</html>
  """
  )
  return HTMLResponse(
    content=f"""
  <html lang="ru">
    <head>
      <title>{title}</title>
      <link rel="stylesheet" href="/static/style.css">
      {head}
    </head>
    <body>
      <header>
        <h1>{title}</h1>
      </header>
      {content}
    </body>
  </html>
  """,
    status_code=200,
  )

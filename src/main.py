import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import models
from admin import setup_admin
from database import engine
from routers import router

models.Base.metadata.create_all(bind=engine)

# app = FastAPI(docs_url=None, redoc_url=None)
app = FastAPI(redoc_url=None)

# app.add_middleware(
#   CORSMiddleware,
#   allow_origins=['http://localhost:5173'],
#   allow_credentials=True,
#   allow_methods=["*"],
#   allow_headers=["*"],
# )

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(router)

setup_admin(app, engine)

if __name__ == '__main__':
  uvicorn.run(app, host='0.0.0.0', port=8000)

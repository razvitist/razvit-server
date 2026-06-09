from fastapi import APIRouter

import routers.auth
import routers.band
import routers.web
import routers.youtube

router = APIRouter()

router.include_router(routers.web.router)
router.include_router(routers.auth.router)
router.include_router(routers.band.router)
router.include_router(routers.youtube.router)

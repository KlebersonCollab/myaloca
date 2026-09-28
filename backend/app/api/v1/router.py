from fastapi import APIRouter

from app.api.v1.endpoints import auth, desks, zones

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(zones.router, prefix="/zones", tags=["Zones"])
api_router.include_router(desks.router, prefix="/desks", tags=["Desks"])

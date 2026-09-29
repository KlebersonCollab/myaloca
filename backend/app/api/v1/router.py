from fastapi import APIRouter

from app.api.v1.endpoints import auth, bookings, buildings, departments, desks, users, zones

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Roles"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(buildings.router, prefix="", tags=["Buildings & Companies"])
api_router.include_router(zones.router, prefix="/zones", tags=["Zones"])
api_router.include_router(desks.router, prefix="/desks", tags=["Desks"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

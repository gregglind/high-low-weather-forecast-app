from fastapi import APIRouter

from app.api.routes import weather, weatherUtils

api_router = APIRouter()
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(
    weatherUtils.router, prefix="/weather-utils", tags=["weather-utils"]
)

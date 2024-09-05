import uuid
from datetime import date, datetime
from typing import Any
from pydantic import conint

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep

from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
from app.models import WeatherItem, WeatherResponse

router = APIRouter()


@router.get("/{lat}/{long}/{date}/{hour}")
def read_forecasts(
    session: SessionDep,
    lat: float = 37.2,
    long: float = 28.1,
    date: date = "2024-07-13",
    hour: int = 15,
) -> WeatherResponse:
    return dict(lat=lat, long=long, date=date, hour=hour, high=13, low=13)

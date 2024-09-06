import uuid
from datetime import date, datetime, time, timedelta
from typing import Any
from pydantic import conint

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select, col

from app.api.deps import SessionDep

from app.models import HourlyWeather, HourlyWeatherResponse

router = APIRouter()


@router.get("/{lat}/{long}/{date}/{hour}")
def max_min_temp(
    session: SessionDep,
    lat: float = 37.2,
    long: float = 28.1,
    date: date = "2024-07-13",
    hour: int = 15,
) -> HourlyWeatherResponse:
    """Returns the max and min forecast at the lat long in the next 72 hours."""

    # TODO, sqlmodel is pretty frustating here.  Getting to sqlAlchemy would be much better, but outside the scope of this assignment

    starttime = datetime.combine(date, time(hour, 0, 0))

    def augment(statement):
        return (
            statement.where(HourlyWeather.lat == lat)
            .where(HourlyWeather.long == long)
            .where(HourlyWeather.startTime == starttime)
        )

    max_stmt = augment(select(func.max(col(HourlyWeather.temperature))))
    min_stmt = augment(select(func.min(col(HourlyWeather.temperature))))

    max_temp = session.exec(max_stmt).one()
    min_temp = session.exec(min_stmt).one()

    return dict(lat=lat, long=long, date=date, hour=hour, high=max_temp, low=min_temp)

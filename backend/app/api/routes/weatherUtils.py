import uuid
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep

from app.models import HourlyWeather

router = APIRouter()

from typing import TypeAlias

lat_type: TypeAlias = int
long_type: TypeAlias = int
from pydantic import HttpUrl

from requests import get

# get the right grid station
# https://api.weather.gov/points/42.7456,-97.0892 -> https://api.weather.gov/gridpoints/OAX/44,129/forecast/hourly


# TODO async this, make it robust to errors
@router.get("/forcast_url/{lat}/{long}")
def get_forecast_url_from_latlong(lat: lat_type, long: long_type) -> HttpUrl:
    url = f"https://api.weather.gov/points/{lat},{long}"
    print(url)
    payload = get(url).json()
    forecastHourlyUrl = payload["properties"]["forecastHourly"]
    return forecastHourlyUrl


@router.get("/fetch-forecasts/{lat}/{long}")
def fetch_forecasts(lat: lat_type, long: long_type) -> list[HourlyWeather]:
    forecast_url: HttpUrl = get_forecast_url_from_latlong(lat, long)
    data = get(forecast_url).json()

    def to_HourlyWeather(d):
        return HourlyWeather(
            startTime=d["startTime"], temperature=d["temperature"], lat=lat, long=long
        )

    return [to_HourlyWeather(d) for d in data["properties"]["periods"]]


@router.get("/update-forecasts/{lat}/{long}")
def update_forecasts(session: SessionDep, lat: lat_type, long: long_type):
    # TODO:  pure insert, no upsert
    # See https://github.com/pcorbel/scitizen/blob/main/api/app/app.py#L33
    instances = fetch_forecasts(lat, long)
    for forecast in instances:
        session.add(forecast)

    session.commit()
    return {"added": len(instances)}

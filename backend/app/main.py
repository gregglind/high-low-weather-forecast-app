from contextlib import asynccontextmanager
import datetime as dt

import asyncio
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings

# batch processes
from apscheduler.schedulers.background import BackgroundScheduler
from app.api.routes.weatherUtils import update_forecasts
from app.api.deps import get_db

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


def job_weather_fetch():
    print(f"BACKGROUND: fetching weather {dt.datetime.now()}")
    # get_db is a generator of sessions.  `next` gives as a specific session
    with next(get_db()) as session:
        try:
            update_forecasts(session, settings.LATITUDE_INT, settings.LONGITUDE_INT)
        except:  # TODO, yes this is terrible!  Handle re-insertion, etc.
            print("WEATHER FETCH JOB ERROR: probably duplicate keys")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # "Startup"
    scheduler = BackgroundScheduler()
    # once
    job_weather_fetch()
    # scheduled
    scheduler.add_job(
        job_weather_fetch, "interval", minutes=settings.WEATHER_FETCH_INTERVAL_MINUTES
    )
    scheduler.start()

    yield
    # "Cleanup"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

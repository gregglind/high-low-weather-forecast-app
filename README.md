# High Low Weather Forecast Service

## Build Instructions

1. `docker compose up`
2. Intital weather data pull will happen automatically, then on a batch cadence (default=60 minutes) thereafter. 
3. Api will be aviable at `localhost/api`.  

## Important urls:

- Weather data [PG Adminer](http://localhost:8080/?pgsql=db&username=postgres&db=app&ns=public&select=hourlyweather)
- API documentation
[http://localhost/docs](http://localhost/docs)
- API example: [`http://localhost/api/v1/weather/39/-93/2024-09-07/15`](http://localhost/api/v1/weather/39/-93/2024-09-07/15)
- DB UI (Adminer) [http://localhost:8080/](http://localhost:8080/)
- DB (PG) [http://localhost:15432/](http://localhost:15432/)

## Additional documentation:

See [./README.orig.md](./README.orig.md) for all features.

### Backend Development: 

Backend: [backend/README.md](./backend/README.md).
###  Deployment 

Deployment docs: [deployment.md](./deployment.md).

### Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.


## Project Specification

1. As an input, the application must accept a configurable location for which to track weather
2. At a configurable interval, defaulting to 60 minutes, the application must query the API described
at https://www.weather.gov/documentation/services-web-api to retrieve forecast data forthe
specified latitude and longitude

Answer: 

Geography for automatic retrieval  in  [.env](.env)
```
    LATITUDE_INT=39
    LONGITUDE_INT=-93
    WEATHER_FETCH_INTERVAL_MINUTES=60 
```

Force a batch insert:
[`http://localhost/api/v1/weather-utils/update-forecasts/38/-93`](http://localhost/api/v1/weather-utils/update-forecasts/38/-93)

Design Trade-offs:  
* \+ All variables are in a consistent, obvious place, consistent with `settings` pattern.
* \- Changing the values requires a full commit and redeploy of the code base.


3. The application must store the set of hourly temperature forecasts forthe next 72 hours, as
predicted at the time ofretrieval, in a local datastore.

Answer:  

* Rows are stored in Postgres `hourlyWeather` table. 
* model code: [./backend/app/models.py](./backend/app/models.py)


4. The application must expose an API or endpoint that accepts as inputs: a latitude, longitude, date,
and UTC hour of day (0-23)
5. The API or endpoint mustreturn the highest and lowestrecorded forecast in the database forthe
specified location, day and hour of day

Answer:

Example usage:  [`http://localhost/api/v1/weather/37/-93/2024-09-05/15`](http://localhost/api/v1/weather/37/-93/2024-09-05/15)

See full api at [http://localhost/docs](http://localhost/docs)

Code:
* [./backend/app/routes/weather.py](./backend/app/routes/weather.py)
* [./backend/app/routes/weatherUtils.py](./backend/app/routes/weatherUtils.py)

6. The application must contain an appropriate Dockerfile and otherresources to containerize the
application

Answer:  see 
* [docker-compose.yml](./docker-compose.yml)
* [backend/Dockerfile](./backend/Dockerfile)

7. The application must include a README with instructions for building the Docker container and
running the application

Answer:  This document.

8. Clearly state all of the assumptions you made in completing the application.

Answer:  See following section.

## Assumptions and design decisions

### Overall project structure

The project derives from the well-known  [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template).  That template is well supported by the author of FastAPI, offers a Dockerfile for FastAPI and Postgres integration.

Starting with an existing project layout has many benefits:
* Re-using supported existing work.
* Removing executive burden about deciding project structure.
* Pre-built patterns for load balancing (Traefik), Security (jwt), Auth / login flows, and email communications with users.
* Patterns for db access, linting, testing.
* Existing dockerfile with pg, fastapi, frontend, Traefik, and Adminer.
 
And these drawbacks:
* No connection to AWS or cloud tools.
* Unneccessary code and models for frontend code.
* Reliance on sqlmodel, rather than pure sqlalchemy.   
* Uses Poetry (I prefer PDM).  

In a production system, I would create a new copier template the more closely matches our exact patterns.  

Templates save time and ease on-boarding.

### Error Hanlding and Testing (and Lack thereof)

In this toy application, there are no additonal tests, and poor bounds checking and error handling.  

In productions, the Lat + Long values should clear bounded types that propagate through the system for consistent handling.

### Data Model

*  Force interger rounding of all Latitudes and Longitudes to simplify error handling and API access inconsistencies the Weather.gov api varies in decimal handling.  
* "Negative longitudes" are a bad UX for the user.  A production system should make some better informed decision about ux here.
* Hourly Weather table has no versioning, low metadata, no upsert handling or other errors handling.

### Database and Migrations

Postgres is a fine choice.  In production this could be RDS or other cloud shared infrastructure.

Migrations: this template supports Alembic.  For this toy app it was simpler to avoid it.


### Batch Process

Decision:  Batch process (weather retrieval) is handled in server app [`./backend/app/main.py`](./backend/app/main.py)

Good (enough):
- re-uses the existing model code.
- re-uses logging and build infrastructure from the app.
- exposes running the weather updater on-demand via (unsecured) http endpoint.

Bad: 
- combines computation and resources 
- observability.  Web service health and batch health are combined.

In a production app I would instead:
- have a shared "models" and 'db access' library used by all services.
- run the batch retrieval job as Kubernetes scheduled task, or use Airflow.

### API

Using FastAPI is a reasonable choice for a standalone application. 

In a production system, I would consider serverless (FastAPI) + RDS as an alternative.

### Other nits and annoyances

1.  Adding new packages:  `docker compose up` doesn't rebuild!  This matters when doing `poetry add`.  
2.  `Sqlmodel` is great for simple operations, but not actively developed.  (See upsert comments above).

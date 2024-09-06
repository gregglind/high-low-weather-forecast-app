Local dev

`docker compose up -d` 


Choices made:

Starting from fastapi/full-stack-fastapi-template. 
We are a tiny team.  The more we can re-use the work of others, the better it will be.

Trade-offs.
- the template is maybe... overkill for this app.  
- but includes alember, sqlmodel, and a file setup.

Lat long issues:
- ?? negatives - ui friction
- bounds for valid values
- handling invalid


What things to drop vs keep?


scheduled job: / I.e, a crontab
- Decided to use an endpoint in the microservice app.
- because it has access to the db and models already.
- in-neworki


Decided to drop alembic for now.  
Dropped all front-end.  Get the url is the through a localhost client.
Dropped (don't use) all users, jwt, etc.  

TODO 
- [ ] conint for hour

Rounding of lat long

No tests!


Nits and annoyances:
1.  Docker compose up doesn't rebuild!  This matters when doing `poetry add`

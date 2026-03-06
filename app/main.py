from fastapi import FastAPI

from app.api.activities import router as activities_router
from app.api.buildings import router as buildings_router
from app.api.organizations import router as organizations_router

app = FastAPI(title="Luna — Directory API", version="0.1.0")

app.include_router(organizations_router)
app.include_router(buildings_router)
app.include_router(activities_router)

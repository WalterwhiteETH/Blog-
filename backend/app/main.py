from fastapi import FastAPI

from app.api.routers import (
    admin_holidays_router,
    audio_analysis_router,
    calendar_router,
    core_router,
    marketplace_router,
    payments_router,
    recommendations_router,
)
from app.core.settings import get_settings
from app.db import Base, engine

settings = get_settings()

app = FastAPI(title=settings.app_title, version=settings.app_version)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Music Platform Backend Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(core_router)
app.include_router(marketplace_router)
app.include_router(payments_router)
app.include_router(calendar_router)
app.include_router(recommendations_router)
app.include_router(admin_holidays_router)
app.include_router(audio_analysis_router)

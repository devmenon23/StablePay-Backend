"""Main FastAPI application."""

from fastapi import FastAPI

from app.routers.currency import router

app = FastAPI(
    title="StablePay API",
    description="Currency conversion and optimization API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "StablePay API - Currency conversion and optimization",
        "version": "1.0.0",
    }


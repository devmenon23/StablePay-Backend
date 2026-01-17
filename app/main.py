"""Main FastAPI application."""

from fastapi import FastAPI

from app.routers.currency import router
from app.services.exchange_fiat import init_bitso_data, BitsoAPIError

app = FastAPI(
    title="StableLiving API",
    description="Currency conversion and optimization API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "StableLiving API - Currency conversion and optimization",
        "version": "1.0.0",
    }


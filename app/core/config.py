import os

from dotenv import load_dotenv

load_dotenv()

BITSO_BASE_URL = os.getenv("BITSO_BASE_URL")
BITSO_API_KEY = os.getenv("BITSO_API_KEY")
BITSO_API_SECRET = os.getenv("BITSO_API_SECRET")

SWAPZONE_API_SECRET = os.getenv("SWAPZONE_API_SECRET")

# Treat these as fiat for routing / fee API selection
FIAT_CURRENCIES = {"USD", "ARS", "MXN"}

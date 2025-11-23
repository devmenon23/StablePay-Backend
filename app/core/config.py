import os

from dotenv import load_dotenv

load_dotenv()

BITSO_BASE_URL = os.getenv("BITSO_BASE_URL", "https://stage.bitso.com")
BITSO_API_KEY = os.getenv("BITSO_API_KEY")
BITSO_API_SECRET = os.getenv("BITSO_API_SECRET")

# Treat these as fiat for routing / fee API selection
FIAT_CURRENCIES = {"USD", "ARS", "MXN"}

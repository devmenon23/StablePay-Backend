import hashlib
import hmac
import time

import requests

from app.core.config import BITSO_API_KEY, BITSO_API_SECRET, BITSO_BASE_URL

SYMBOL_TO_NODE = {
    "ars": "ARS",
    "usd": "USDC",
    "btc": "BTC",
    "sol": "SOL",
    "mxn": "MXN",
}

NODE_TO_SYMBOL = {v: k for k, v in SYMBOL_TO_NODE.items()}

BOOK_FEES = {}


def _bitso_request(method: str, path: str, auth: bool = False, params=None):
    """
    Minimal Bitso request wrapper.
    For GET + no body, the signed message is: nonce + method + path + ""
    Query params are NOT included in the signature.
    """
    url = BITSO_BASE_URL + path
    headers = {"Content-Type": "application/json"}

    if auth:
        if not BITSO_API_KEY or not BITSO_API_SECRET:
            raise RuntimeError("BITSO_API_KEY and BITSO_API_SECRET must be set in environment.")

        nonce = str(int(time.time() * 1000))
        message = nonce + method.upper() + path

        signature = hmac.new(
            BITSO_API_SECRET.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers["Authorization"] = f"Bitso {BITSO_API_KEY}:{nonce}:{signature}"

    resp = requests.request(method, url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    if not data.get("success", True):
        raise RuntimeError(f"Bitso API error: {data}")

    return data["payload"]


def init_bitso_data():
    """
    Populate BOOK_FEES from Bitso.
    Call this once at startup.
    """

    global BOOK_FEES

    fees_payload = _bitso_request("GET", "/api/v3/fees/", auth=True)
    fees_list = fees_payload["fees"]

    BOOK_FEES = {
        fee["book"]: {
            "maker": float(fee["maker_fee_percent"]),
            "taker": float(fee["taker_fee_percent"]),
        }
        for fee in fees_list
    }


def get_trade_fee_for_pair(from_currency: str, to_currency: str):
    """
    Given two node names (e.g. "ARS", "USDC"), return taker_fee_percent as a float.

    Example: if Bitso says "0.6500" (0.65%), we store 0.65 and return 0.65.

    If there is no direct Bitso book, returns float('inf').
    """

    from_sym = NODE_TO_SYMBOL.get(from_currency)
    to_sym = NODE_TO_SYMBOL.get(to_currency)

    if not from_sym or not to_sym:
        return float("inf")

    book1 = f"{from_sym}_{to_sym}"
    book2 = f"{to_sym}_{from_sym}"

    if book1 in BOOK_FEES:
        book = book1
    elif book2 in BOOK_FEES:
        book = book2
    else:
        return float("inf")

    fee_percent = BOOK_FEES[book]["taker"]
    return fee_percent


def Get_cost(from_currency, to_currency, amount):
    """
    Return the absolute fee for trading `amount` of from_currency into to_currency,
    using Bitso's taker fee percentage.

    Example:
      BOOK_FEES["usd_ars"]["taker"] == 0.65
      amount = 1000 ARS
      cost = 1000 * (0.65 / 100) = 6.5 ARS
    """

    if from_currency == to_currency:
        return 0.0, "bitso"

    fee_percent = get_trade_fee_for_pair(from_currency, to_currency)

    if fee_percent == float("inf"):
        return float("inf"), "bitso"

    fee_fraction = fee_percent / 100.0
    cost = amount * fee_fraction

    return cost, "bitso"

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

NODE_TO_SYMBOL = {node: sym for sym, node in SYMBOL_TO_NODE.items()}

BOOK_FEES = {}

class BitsoAPIError(RuntimeError):
    """Raised when Bitso returns an error payload or an unexpected schema."""

def _require_credentials():
    if not BITSO_API_KEY or not BITSO_API_SECRET:
        raise BitsoAPIError("BITSO_API_KEY and BITSO_API_SECRET must be set.")
    return BITSO_API_KEY, BITSO_API_SECRET

def _sign_request(nonce, method, path, body=""):
    """
    Bitso signature:
        message = nonce + METHOD + path + body

    For GET with no body, body="".
    """
    _, secret = _require_credentials()
    message = f"{nonce}{method.upper()}{path}{body}"
    return hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def _bitso_request(method, path, auth, params=None, timeout_s=10.0):
    """
    Bitso request wrapper.

    - Signs nonce+METHOD+path(+body) when auth=True
    - Returns `data["payload"]`
    """
    if not path.startswith("/"):
        path = "/" + path

    base_url = BITSO_BASE_URL.rstrip("/")
    url = f"{base_url}{path}"

    headers = {"Content-Type": "application/json"}

    if auth:
        api_key, _ = _require_credentials()
        nonce = str(int(time.time() * 1000))
        signature = _sign_request(nonce, method, path)
        headers["Authorization"] = f"Bitso {api_key}:{nonce}:{signature}"

    resp = requests.request(
        method=method.upper(),
        url=url,
        params=params,
        headers=headers,
        timeout=timeout_s,
    ) 
    resp.raise_for_status()

    data = resp.json()
    if not isinstance(data, dict):
        raise BitsoAPIError(f"Unexpected response type: {type(data)}")

    if data.get("success", True) is not True:
        raise BitsoAPIError(f"Bitso API error: {data}")

    if "payload" not in data:
        raise BitsoAPIError(f"Missing payload in response: {data}")

    return data["payload"]


def update_book_fees():
    """
    Update BOOK_FEES from Bitso fees endpoint.

    Call this once at startup (or whenever you want to refresh fees).
    """ 
    global BOOK_FEES

    payload = _bitso_request("GET", "/api/v3/fees/", auth=True)
    fees_list = payload.get("fees")

    BOOK_FEES = {
        item["book"]: float(item["fee_decimal"]) for item in fees_list
    }

def get_trade_fee_for_pair(from_currency: str, to_currency: str):
    """
    Given two node names (e.g. "ARS", "USDC"), return fee percent as a float.

    Example: if Bitso says "0.6500" (0.65%), we store 0.65 and return 0.65.

    If there is no direct Bitso book, returns float('inf').
    """
    update_book_fees()

    from_sym = NODE_TO_SYMBOL.get(from_currency)
    to_sym = NODE_TO_SYMBOL.get(to_currency)

    if not from_sym or not to_sym:
        return float("inf"), "bitso"

    book1 = f"{from_sym}_{to_sym}".lower()
    book2 = f"{to_sym}_{from_sym}".lower()

    if book1 in BOOK_FEES:
        book = book1
    elif book2 in BOOK_FEES:
        book = book2
    else:
        return float("inf")

    return BOOK_FEES[book], "bitso"


def get_cost(from_currency, to_currency, amount):
    """
    Return the absolute fee for trading `amount` of from_currency into to_currency,
    using Bitso's fee percent.

    Returns:
        (cost, "bitso")
        cost=float('inf') if no book exists
    """

    fee_fraction = get_trade_fee_for_pair(from_currency, to_currency)

    if fee_fraction == float("inf"):
        return float("inf"), "bitso"

    cost = amount * fee_fraction
    return cost, "bitso"

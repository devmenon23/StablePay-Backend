# exchange_fiat.py
import os
import time
import hmac
import hashlib
import requests

BITSO_BASE_URL = "https://api.bitso.com"

API_KEY = os.getenv("BITSO_API_KEY")
API_SECRET = os.getenv("BITSO_API_SECRET")

SYMBOL_TO_NODE = {
    "ars": "ARS",
    "usd": "USDC",
    "btc": "BTC",
}

NODE_TO_SYMBOL = {v: k for k, v in SYMBOL_TO_NODE.items()}

BOOK_FEES = {}          # book -> {"maker": float, "taker": float}
CURRENCY_NEIGHBORS = {} # "USDC" -> ["ARS", "SOL", ...]

def _bitso_request(method: str, path: str, auth: bool = False, params=None):
    """
    Minimal Bitso request wrapper.
    For GET + no body, the signed message is: nonce + method + path + ""
    Query params are NOT included in the signature.
    """

    url = BITSO_BASE_URL + path
    headers = {"Content-Type": "application/json"}

    if auth:
        if not API_KEY or not API_SECRET:
            raise RuntimeError(
                "BITSO_API_KEY and BITSO_API_SECRET must be set in environment."
            )

        nonce = str(int(time.time() * 1000))
        message = nonce + method.upper() + path
        signature = hmac.new(
            API_SECRET.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        headers["Authorization"] = f"Bitso {API_KEY}:{nonce}:{signature}"

    resp = requests.request(method, url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success", True):
        raise RuntimeError(f"Bitso API error: {data}")
    return data["payload"]

def init_bitso_data():
    """
    Populate BOOK_FEES and CURRENCY_NEIGHBORS from Bitso.
    Call this once at startup.
    """

    global BOOK_FEES, CURRENCY_NEIGHBORS

    fees_payload = _bitso_request("GET", "/api/v3/fees/", auth=True)
    fees_list = fees_payload["fees"]

    BOOK_FEES = {
        fee["book"]: {
            "maker": float(fee["maker_fee_percent"]),
            "taker": float(fee["taker_fee_percent"]),
        }
        for fee in fees_list
    }

    books_payload = _bitso_request("GET", "/api/v3/available_books/", auth=False)

    neighbors = {name: set() for name in SYMBOL_TO_NODE.values()}
    
    for book in books_payload:
        book_name = book["book"]  # e.g. "btc_ars", "usd_ars", "sol_usd"
        try:
            base, quote = book_name.split("_")
        except ValueError:
            continue
        
        if base not in SYMBOL_TO_NODE or quote not in SYMBOL_TO_NODE:
            # ignore books we don't care about
            continue

        c1 = SYMBOL_TO_NODE[base]
        c2 = SYMBOL_TO_NODE[quote]

        neighbors[c1].add(c2)
        neighbors[c2].add(c1)

    CURRENCY_NEIGHBORS = {k: sorted(list(v)) for k, v in neighbors.items()}

def get_neighbors_for(currency_name: str):
    """
    Return list of neighbor currencies for a given node name,
    based on Bitso books.
    """
    return CURRENCY_NEIGHBORS.get(currency_name, [])

def get_trade_fee_for_pair(from_currency: str, to_currency: str):
    """
    Given two node names (e.g. "ARS", "USDC"), return:
        (cost, exchange_name)

    cost = taker_fee_percent (e.g. 0.65 for 0.65%)
    exchange_name = human-readable label, e.g. "bitso:usd_ars"

    If there is no direct Bitso book, returns (float('inf'), 'unavailable').
    """

    from_sym = NODE_TO_SYMBOL.get(from_currency)
    to_sym = NODE_TO_SYMBOL.get(to_currency)

    if not from_sym or not to_sym:
        return float("inf"), "unavailable"

    # Books are unordered conceptually; Bitso uses base_quote.
    book1 = f"{from_sym}_{to_sym}"
    book2 = f"{to_sym}_{from_sym}"

    book = None
    if book1 in BOOK_FEES:
        book = book1
    elif book2 in BOOK_FEES:
        book = book2
    else:
        return float("inf"), "no-direct-book"

    fee_percent = BOOK_FEES[book]["taker"]  # use taker fee as "transaction fee"
    return fee_percent

def Get_cost(from_currency, to_currency, amount):
    """
    Wrapper around get_trade_fee_for_pair to match graph.py's get_cost signature.
    """
    amount * get_trade_fee_for_pair(from_currency, to_currency), "bitso"

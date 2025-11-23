# exchange_fiat.py
import os
import time
import hmac
import hashlib
import requests
import convert

def p2p_quote(from_currency: str, to_currency: str, amount: float):
    """
    Very simple P2P estimator based on mid‑market prices.
    Plug in your P2P marketplace (Binance P2P, OKX P2P, etc.)
    """

    P2P_RATES = {
        ("BTC", "ARS"): 90000000,      # ARS per BTC (example)
        ("USDT", "ARS"): 1500,         # ARS per USDT
        ("ARS", "USDT"): 1 / 1500,
        ("ARS", "BTC"): 1 / 90000000,
    }

    key = (from_currency, to_currency)
    if key not in P2P_RATES:
        return None, None

    rate = P2P_RATES[key]
    final_amount = amount * rate
    return final_amount, "p2p"


def Get_cost(from_currency: str, to_currency: str, amount: float):

    # ---------- 2. Try P2P aggregator ----------
    try:
        final_amount, ex = p2p_quote(from_currency, to_currency, amount)
        if final_amount is not None:
            fee_percent = 1 - (final_amount / amount)
            return fee_percent, ex
    except:
        pass

import requests

def binance_p2p_avg_price(asset="USDT", fiat="ARS", trade_type="BUY", limit=10):
    """
    Fetch average P2P price for USDT/ARS using Binance public endpoints.

    trade_type = "BUY"  → users buying crypto (you SELL crypto)
    trade_type = "SELL" → users selling crypto (you BUY crypto)
    """

    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "page": 1,
        "rows": limit,
        "asset": asset,
        "fiat": fiat,
        "tradeType": trade_type,  
        "publisherType": None
    }

    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    if "data" not in data:
        raise Exception("Unexpected Binance response")

    prices = []
    for offer in data["data"]:
        price = float(offer["adv"]["price"])
        prices.append(price)
    
    if len(prices) == 0:
        return 0
    return sum(prices) / len(prices)

FIAT = ["ARS"]

def Get_cost(src, dest, amount):
    to_amount = 0.0
    if src in FIAT:
        to_amount = binance_p2p_avg_price(dest, src, trade_type="SELL")
    else:
        to_amount = binance_p2p_avg_price(src, dest, trade_type="BUY")
    before_usd = convert.convert_currency(src, "USD", 1)
    print(before_usd)
    after_usd = convert.convert_currency(dest, "USD", to_amount)
    print(after_usd)
    fees = (before_usd - after_usd) / before_usd
    if fees < 0:
        fees = 0
    return fees, "p2p"
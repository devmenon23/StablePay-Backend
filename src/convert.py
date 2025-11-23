import requests

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "USDE": "ethena-usde",
    "ETH": "ethereum",
    "USDT": "tether",
    "USDC": "usd-coin",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "SOL": "solana",
    "DOT": "polkadot",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "DAI": "dai",
    "TRX": "tron",
    "LINK": "chainlink",
    "WBTC": "wrapped-bitcoin",
    "ATOM": "cosmos",
    "XMR": "monero",
    "LTC": "litecoin",
    "ETC": "ethereum-classic",
    "ARB": "arbitrum",
    "OP": "optimism",
    "AAVE": "aave",
    "UNI": "uniswap",
    "FIL": "filecoin",
    "NEAR": "near",
    "XTZ": "tezos",
    "BCH": "bitcoin-cash",
    "EGLD": "multiversx",
    "APE": "apecoin",
    "SAND": "the-sandbox",
    "MANA": "decentraland",
}

# -------------------------
#   HELPER FUNCTIONS
# -------------------------

def cryptotofiat(fromcrypto, tofiat, amount):
    fromcrypto = COINGECKO_IDS[fromcrypto]
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": fromcrypto.lower(),
        "vs_currencies": tofiat.lower(),
    }
    headers = {
        "x-cg-demo-api-key": "CG-Sv6NRNkmpPbkU27jeWGaNrbR",
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise ValueError("Failed to fetch price data from CoinGecko")

    data = response.json()
    if fromcrypto.lower() not in data:
        raise ValueError(f"Unknown currency: {fromcrypto}")

    price = data[fromcrypto.lower()][tofiat.lower()]
    return amount * price


def fiattofiat(fromfiat, tofiat, amount):
    url = f"https://open.er-api.com/v6/latest/{fromfiat}"
    data = requests.get(url).json()
    rate = data["rates"][tofiat]
    return amount * rate


def fiattocrypto(fromfiat, tocrypto, amount):
    """
    Convert fiat → crypto using:
        (fiat amount) → (USD) → (crypto)
    """

    # Step 1: Convert fiat to USD
    if fromfiat.upper() != "USD":
        intermediate_usd = fiattofiat(fromfiat.upper(), "USD", amount)
    else:
        intermediate_usd = amount

    # Step 2: USD → crypto using coingecko price
    coingecko_id = COINGECKO_IDS[tocrypto]

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coingecko_id.lower(),
        "vs_currencies": "usd",
    }
    headers = {
        "x-cg-demo-api-key": "CG-Sv6NRNkmpPbkU27jeWGaNrbR",
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise ValueError("Failed to fetch crypto price")

    data = response.json()
    crypto_price_usd = data[coingecko_id]["usd"]

    return intermediate_usd / crypto_price_usd


# -------------------------
#   MAIN WRAPPER
# -------------------------

def convert_currency(from_ccy, to_ccy, amount):
    from_ccy = from_ccy.upper()
    to_ccy = to_ccy.upper()

    is_crypto_from = from_ccy in COINGECKO_IDS
    is_crypto_to = to_ccy in COINGECKO_IDS

    if not is_crypto_from and not is_crypto_to:
        return fiattofiat(from_ccy, to_ccy, amount)

    if is_crypto_from and not is_crypto_to:
        return cryptotofiat(from_ccy, to_ccy, amount)

    if not is_crypto_from and is_crypto_to:
        return fiattocrypto(from_ccy, to_ccy, amount)

    # crypto → crypto: convert through USD automatically
    usd_value = cryptotofiat(from_ccy, "USD", amount)
    return fiattocrypto("USD", to_ccy, usd_value)
import requests

def convert_currency(from_ccy, to_ccy, amount):
    url = f"https://open.er-api.com/v6/latest/{from_ccy}"
    data = requests.get(url).json()
    rate = data["rates"][to_ccy]
    return amount * rate
def crpytotofiat(fromcrypto, tofiat, amount):
    return
def fiattocrypto(fromfiat, tocrypto, amount):
    url = "https://api.coingecko.com/api/v3/simple/price"
    #print(currency_symbol.lower())
    params = {
        "ids": tocrypto.lower(),
        "vs_currencies": fromfiat.lower(),
    }
    headers = {
        "x-cg-demo-api-key": "CG-Sv6NRNkmpPbkU27jeWGaNrbR",
    }

    response = requests.get(url, params=params, headers=headers)

    #print(response)
    if response.status_code != 200:
        raise ValueError("Failed to fetch price data from CoinGecko")

    data = response.json()

    if tocrypto.lower() not in data:
        raise ValueError(f"Unknown currency: {tocrypto}")

    price_usd = data[tocrypto.lower()][fromfiat.lower()]
    return amount * price_usd

def fiattofiat(fromfiat, tofiat, amount):
    url = f"https://open.er-api.com/v6/latest/{fromfiat}"
    data = requests.get(url).json()
    rate = data["rates"][tofiat]
    return amount * rate
print(fiattofiat("MXN", "USD", 20))
print(fiattocrypto("MXN", "bitcoin", 20))
import requests
import time

COINGECKO_IDS = {
    "BTC": "bitcoin",
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

def convert_to_usd(currency_symbol, amount):
    """
    Convert `amount` of crypto `currency_symbol` to USD using CoinGecko.
    Example: convert_to_usd("btc", 0.05)
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    #print(currency_symbol.lower())
    params = {
        "ids": currency_symbol.lower(),
        "vs_currencies": "usd",
    }
    headers = {
        "x-cg-demo-api-key": "CG-Sv6NRNkmpPbkU27jeWGaNrbR",
    }

    response = requests.get(url, params=params, headers=headers)

    #print(response)
    if response.status_code != 200:
        raise ValueError("Failed to fetch price data from CoinGecko")

    data = response.json()

    if currency_symbol.lower() not in data:
        raise ValueError(f"Unknown currency: {currency_symbol}")

    price_usd = data[currency_symbol.lower()]["usd"]
    return amount * price_usd

def Get_cost(src, dest, amount): # amount is in src
    # curl --location 'https://api.swapzone.io/v1/exchange/get-rate?from=btc&to=doge&amount=0.1&rateType=all&availableInUSA=false&chooseRate=best&noRefundAddress=false&ofcAdapter=true' --header 'x-api-key: w7vDUCFZQ'
    url = "https://api.swapzone.io/v1/exchange/get-rate"

    params = {
        "from": src.lower(),
        "to": dest.lower(),
        "amount": amount,
        "rateType": "all",
        "availableInUSA": "false",
        "chooseRate": "best",
        "noRefundAddress": "false",
        "ofcAdapter": "true"
    }

    headers = {
        "x-api-key": "w7vDUCFZQ"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise ValueError("Failed to fetch cost from swapzone")
    resp = response.json()
    before_usd = convert_to_usd(COINGECKO_IDS[src], resp['amountFrom'])
    after_usd = convert_to_usd(COINGECKO_IDS[dest], resp['amountTo'])
    return before_usd - after_usd, "swapzone"

#print(Get_cost("SOL", "WBTC", 20))

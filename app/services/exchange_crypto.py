import requests

from app.services import convert

def Get_cost(src, dest, amount):
    url = "https://api.swapzone.io/v1/exchange/get-rate"

    params = {
        "from": src.lower(),
        "to": dest.lower(),
        "amount": amount,
        "rateType": "all",
        "availableInUSA": "false",
        "chooseRate": "best",
        "noRefundAddress": "false",
        "ofcAdapter": "true",
    }

    headers = {"x-api-key": "w7vDUCFZQ"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise ValueError("Failed to fetch cost from swapzone")

    resp = response.json()

    before_usd = convert.convert_currency(src, "USD", resp["amountFrom"])
    after_usd = convert.convert_currency(dest, "USD", resp["amountTo"])

    return before_usd - after_usd, (before_usd - after_usd) / before_usd, "swapzone"

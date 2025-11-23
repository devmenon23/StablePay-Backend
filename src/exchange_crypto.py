import requests
import time
import convert

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
    before_usd = convert.convert_currency(src, "USD", resp['amountFrom'])
    print(before_usd)
    after_usd = convert.convert_currency(dest, "USD", resp['amountTo'])
    print(after_usd)
    return before_usd - after_usd, "swapzone"

print(Get_cost("BTC", "XMR", convert.convert_currency("USD", "BTC", 50)))
print(Get_cost("LTC", "XMR", convert.convert_currency("USD", "LTC", 50)))
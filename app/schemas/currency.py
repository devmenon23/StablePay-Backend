"""Currency conversion schemas."""
from typing import List

from pydantic import BaseModel

class ConvertCurrencyRequest(BaseModel):
    from_ccy: str
    to_ccy: str
    amount: float

class ConvertCurrencyResponse(BaseModel):
    converted_amount: float

class GetCostRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

class GetCostResponse(BaseModel):
    cost: float
    exchange: str

class Hop(BaseModel):
    from_currency: str
    to_currency: str
    fee: float
    fee_percent: float
    amount_before: float
    amount_after: float
    exchange: str

class FindOptimizedPathRequest(BaseModel):
    start_currency: str
    target_currency: str
    amount: float = 100.0

class FindOptimizedPathResponse(BaseModel):
    path: List[str]
    final_amount: float
    total_fee: float
    hops: List[Hop]


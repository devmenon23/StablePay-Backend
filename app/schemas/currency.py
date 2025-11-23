"""Currency conversion schemas."""
from typing import Dict, Optional

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


class DijkstraRequest(BaseModel):
    start_currency: str
    amount: Optional[float] = 100.0


class DijkstraResponse(BaseModel):
    costs: Dict[str, Optional[float]]
    previous: Dict[str, Optional[str]]

from fastapi import APIRouter, HTTPException

from app.core.config import FIAT_CURRENCIES
from app.models.graph import Graph
from app.schemas.currency import (
    ConvertCurrencyRequest,
    ConvertCurrencyResponse,
    DijkstraRequest,
    DijkstraResponse,
    GetCostRequest,
    GetCostResponse,
)
from app.services import convert, exchange_crypto, exchange_fiat
from app.services.conversion_optimizer import dijkstra

router = APIRouter(tags=["currency"])

@router.post("/convert", response_model=ConvertCurrencyResponse)
async def convert_currency_endpoint(request: ConvertCurrencyRequest):
    """
    Convert currency using exchange rates.
    """
    try:
        converted_amount = convert.convert_currency(
            request.from_ccy, request.to_ccy, request.amount
        )
        return ConvertCurrencyResponse(converted_amount=converted_amount)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cost", response_model=GetCostResponse)
async def get_cost_endpoint(request: GetCostRequest):
    """
    Get the cost (fee) for converting from one currency to another.
    Handles both crypto-to-crypto and fiat conversions.
    """
    try:
        if request.from_currency in FIAT_CURRENCIES or request.to_currency in FIAT_CURRENCIES:
            cost, exchange = exchange_fiat.get_cost(
                request.from_currency, request.to_currency, request.amount
            )
        else:
            cost, exchange = exchange_crypto.get_cost(
                request.from_currency, request.to_currency, request.amount
            )

        return GetCostResponse(cost=cost, exchange=exchange)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dijkstra", response_model=DijkstraResponse)
async def dijkstra_endpoint(request: DijkstraRequest):
    """
    Run Dijkstra's algorithm to find shortest path costs from a starting currency.
    Returns costs to all reachable currencies and previous node information.
    """
    try:
        g = Graph()
        g.update_costs()

        start_node = None
        for node in g.nodes:
            if node.name == request.start_currency:
                start_node = node
                break

        if start_node is None:
            raise HTTPException(
                status_code=404, detail=f"Currency '{request.start_currency}' not found in graph"
            )

        costs, prev = dijkstra(g, start_node)

        costs_dict = {
            node.name: costs[node] if costs[node] != float("inf") else None for node in costs
        }

        previous_dict = {
            node.name: prev[node].name if prev[node] is not None else None for node in prev
        }

        return DijkstraResponse(costs=costs_dict, previous=previous_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

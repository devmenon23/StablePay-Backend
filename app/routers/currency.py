from fastapi import APIRouter, HTTPException
import math

from app.core.config import FIAT_CURRENCIES
from app.models.graph import Graph
from app.schemas.currency import (
    ConvertCurrencyRequest,
    ConvertCurrencyResponse,
    GetCostRequest,
    GetCostResponse,
    FindOptimizedPathRequest,
    FindOptimizedPathResponse,
)
from app.services import convert, exchange_crypto, exchange_fiat
from app.services.conversion_optimizer import dijkstra, reconstruct_path, evaluate_path

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


@router.post("/find_optimized_path", response_model=FindOptimizedPathResponse)
async def find_optimized_path_endpoint(request: FindOptimizedPathRequest):
    """
    Find the lowest-fee conversion route from start_currency -> target_currency.
    Returns the hop-by-hop fees and final amount.
    """
    try:
        g = Graph()
        g.update_fees()

        start_node = None
        for node in g.nodes:
            if node.name == request.start_currency:
                start_node = node
                break
        
        target_node = None
        for node in g.nodes:
            if node.name == request.target_currency:
                target_node = node
                break

        if start_node is None:
            raise HTTPException(status_code=404, detail=f"Start currency '{request.start_currency}' not in graph")
        if target_node is None:
            raise HTTPException(status_code=404, detail=f"Target currency '{request.target_currency}' not in graph")

        costs, prev = dijkstra(g, start_node)

        if (costs[target_node] == float("inf") or prev.get(target_node) is None) and start_node != target_node:
            raise HTTPException(status_code=404, detail="No route found")
        
        path_nodes = reconstruct_path(prev, start_node, target_node)
        if not path_nodes:
            raise HTTPException(status_code=404, detail="No route found")

        eval_result = evaluate_path(path_nodes, request.amount)

        # adapt hop keys to schema
        hops = [
            {
                "from_currency": h["from"],
                "to_currency": h["to"],
                "fee": h["fee"],
                "fee_percent": h["fee_percent"],
                "amount_before": h["amount_before"],
                "amount_after": h["amount_after"],
                "exchange": h["exchange"],
            }
            for h in eval_result["hops"]
        ]

        return FindOptimizedPathResponse(
            path=[n.name for n in path_nodes],
            final_amount=eval_result["final_amount"],
            total_fee=eval_result["total_fee"],
            hops=hops,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

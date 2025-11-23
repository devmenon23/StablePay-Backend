from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List, Tuple
import sys

# Import the functions
from conversion_optimizer import dijkstra
from convert import convert_currency
from exchange_crypto import Get_cost as Get_cost_crypto
from exchange_fiat import Get_cost as Get_cost_fiat
import graph

app = FastAPI(title="StableLiving API", description="Currency conversion and optimization API")


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
    amount: Optional[float] = 100.0  # Default amount for cost calculation


class DijkstraResponse(BaseModel):
    costs: Dict[str, float]
    previous: Dict[str, Optional[str]]


@app.get("/")
async def root():
    return {"message": "StableLiving API - Currency conversion and optimization"}


@app.post("/convert_currency", response_model=ConvertCurrencyResponse)
async def convert_currency_endpoint(request: ConvertCurrencyRequest):
    """
    Convert currency using exchange rates.
    """
    try:
        converted_amount = convert_currency(
            request.from_ccy, 
            request.to_ccy, 
            request.amount
        )
        return ConvertCurrencyResponse(converted_amount=converted_amount)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/get_cost", response_model=GetCostResponse)
async def get_cost_endpoint(request: GetCostRequest):
    """
    Get the cost (fee) for converting from one currency to another.
    Handles both crypto-to-crypto and fiat conversions.
    """
    try:
        FIAT = {"USD", "ARS", "MXN"}
        
        # Determine if it's a fiat or crypto conversion
        if request.from_currency in FIAT or request.to_currency in FIAT:
            cost, exchange = Get_cost_fiat(
                request.from_currency,
                request.to_currency,
                request.amount
            )
        else:
            cost, exchange = Get_cost_crypto(
                request.from_currency,
                request.to_currency,
                request.amount
            )
        
        return GetCostResponse(cost=cost, exchange=exchange)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/dijkstra", response_model=DijkstraResponse)
async def dijkstra_endpoint(request: DijkstraRequest):
    """
    Run Dijkstra's algorithm to find shortest path costs from a starting currency.
    Returns costs to all reachable currencies and previous node information.
    """
    try:
        # Create a graph instance
        g = graph.Graph()
        
        # Update edge fees and log-space costs
        g.update_costs()  # <-- removed request.amount
        
        # Find the start node by currency name
        start_node = None
        for node in g.nodes:
            if node.name == request.start_currency:
                start_node = node
                break
        
        if start_node is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Currency '{request.start_currency}' not found in graph"
            )
        
        # Run dijkstra
        costs, prev = dijkstra(g, start_node)
        
        # Convert node objects to currency names for response
        costs_dict = {
            node.name: costs[node] if costs[node] != float('inf') else None
            for node in costs
        }
        
        previous_dict = {
            node.name: prev[node].name if prev[node] is not None else None
            for node in prev
        }
        
        return DijkstraResponse(costs=costs_dict, previous=previous_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


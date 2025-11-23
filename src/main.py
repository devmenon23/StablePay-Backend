# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List

# Import the functions
from conversion_optimizer import dijkstra, evaluate_path
from convert import convert_currency
from exchange_crypto import Get_cost as Get_cost_crypto
from exchange_fiat import Get_cost as Get_cost_fiat
import graph

app = FastAPI(
    title="StableLiving API",
    description="Currency conversion and optimization API",
)

# =========================
#       REQUEST MODELS
# =========================

class ConvertCurrencyRequest(BaseModel):
    from_ccy: str
    to_ccy: str
    amount: float


class GetCostRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float


class DijkstraRequest(BaseModel):
    start_currency: str
    amount: Optional[float] = 100.0  # currently unused, but kept for future use


class EvaluatePathRequest(BaseModel):
    # Sequence of currency symbols representing the path, e.g. ["ARS", "USDE", "SOL", "MXN"]
    path: List[str]
    amount: float  # initial amount in path[0] currency


# =========================
#      RESPONSE MODELS
# =========================

class ConvertCurrencyResponse(BaseModel):
    converted_amount: float


class GetCostResponse(BaseModel):
    cost: float
    exchange: str


class DijkstraResponse(BaseModel):
    costs: Dict[str, Optional[float]]     # None if unreachable
    previous: Dict[str, Optional[str]]    # previous node name or None


class HopBreakdown(BaseModel):
    from_ccy: str
    to_ccy: str
    fee_percent: float
    fee_local: float
    fee_ars: Optional[float]
    amount_before: float
    amount_after_fee: float
    amount_next: float
    exchange: str


class EvaluatePathResponse(BaseModel):
    final_amount: float                 # in last currency of the path
    final_amount_ars: Optional[float]   # same amount converted to ARS (if possible)
    total_fee_local: float              # sum of fees in each hop's local currency
    total_fee_ars: float                # sum of fees expressed in ARS
    hops: List[HopBreakdown]


# =========================
#          ROUTES
# =========================

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
            request.amount,
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
                request.amount,
            )
        else:
            cost, exchange = Get_cost_crypto(
                request.from_currency,
                request.to_currency,
                request.amount,
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
        # Create a graph instance and populate fees / log-space costs
        g = graph.Graph()
        g.update_costs()

        # Find the start node by currency name
        start_node = None
        for node in g.nodes:
            if node.name == request.start_currency:
                start_node = node
                break

        if start_node is None:
            raise HTTPException(
                status_code=404,
                detail=f"Currency '{request.start_currency}' not found in graph",
            )

        # Run Dijkstra
        costs, prev = dijkstra(g, start_node)

        # Convert node objects to currency names for response
        costs_dict: Dict[str, Optional[float]] = {
            node.name: (costs[node] if costs[node] != float("inf") else None)
            for node in costs
        }

        previous_dict: Dict[str, Optional[str]] = {
            node.name: (prev[node].name if prev[node] is not None else None)
            for node in prev
        }

        return DijkstraResponse(costs=costs_dict, previous=previous_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate_path", response_model=EvaluatePathResponse)
async def evaluate_path_endpoint(request: EvaluatePathRequest):
    """
    Evaluate a specific path of currencies with chained fees.

    - `path`: list of currency symbols, e.g. ["ARS", "USDE", "SOL", "MXN"]
    - `amount`: initial amount in the first currency in `path`

    Uses the same Graph + edge fees/log-costs as the /dijkstra endpoint.
    """
    try:
        if not request.path:
            raise HTTPException(status_code=400, detail="Path cannot be empty")

        # Build graph and costs
        g = graph.Graph()
        g.update_costs()

        # Map currency codes in the path to Node objects
        path_nodes = []
        for ccy in request.path:
            if ccy not in g.nametoindex:
                raise HTTPException(
                    status_code=400,
                    detail=f"Currency '{ccy}' not found in graph",
                )
            idx = g.nametoindex[ccy]
            path_nodes.append(g.nodes[idx])

        # Call the core evaluate_path logic
        eval_result = evaluate_path(path_nodes, request.amount)

        # Transform hop dicts into HopBreakdown models
        hops_models: List[HopBreakdown] = []
        for hop in eval_result["hops"]:
            hops_models.append(
                HopBreakdown(
                    from_ccy=hop["from"],
                    to_ccy=hop["to"],
                    fee_percent=hop["fee_percent"],
                    fee_local=hop["fee_local"],
                    fee_ars=hop["fee_ars"],
                    amount_before=hop["amount_before"],
                    amount_after_fee=hop["amount_after_fee"],
                    amount_next=hop["amount_next"],
                    exchange=hop["exchange"],
                )
            )

        return EvaluatePathResponse(
            final_amount=eval_result["final_amount"],
            final_amount_ars=eval_result["final_amount_ars"],
            total_fee_local=eval_result["total_fee_local"],
            total_fee_ars=eval_result["total_fee_ars"],
            hops=hops_models,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# conversion_optimizer.py
import heapq
import graph
from convert import convert_currency


def dijkstra(graph, start):
    costs = {node: float('inf') for node in graph.nodes}
    prev = {node: None for node in costs}
    
    costs[start] = 0
    pq = [(0, start.name, start)]
    
    while pq:
        currCost, name, u = heapq.heappop(pq)

        if currCost > costs[u]:
            continue

        for edge in u.edges:
            v = edge.to_node
            c = edge.cost
            newCost = currCost + c
            if newCost < costs[v]:
                costs[v] = newCost
                prev[v] = u
                heapq.heappush(pq, (newCost, v.name, v))

    return costs, prev

def reconstruct_path(prev, start, target):
    if prev.get(target) is None and start != target:
        return None
    
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    path.reverse()
    return path

def _evaluate_path_nodes(path_nodes, initial_amount: float):
    """
    Internal helper: given a list of Node objects [n0, n1, ..., nk]
    and an initial_amount in n0.name, simulate chained fees and
    convert fees to ARS along the way.
    """
    if not path_nodes or len(path_nodes) == 1:
        # trivial path or no path
        start_ccy = path_nodes[0].name if path_nodes else None
        final_amount_ars = (
            convert_currency(start_ccy, "ARS", initial_amount)
            if start_ccy is not None
            else None
        )
        return {
            "final_amount": initial_amount,
            "final_amount_ars": final_amount_ars,
            "total_fee_local": 0.0,
            "total_fee_ars": 0.0,
            "hops": [],
        }

    amount = initial_amount  # always in currency of current node u
    total_fee_local = 0.0
    total_fee_ars = 0.0
    hops = []

    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i + 1]

        # Find the actual edge u -> v
        edge = next(e for e in u.edges if e.to_node is v)

        # 1) fee in u's currency, applied to *current* amount
        fee_local = amount * edge.fee_percent
        amount_after_fee = amount - fee_local  # base shrinks here

        # 2) translate that fee into ARS (for reporting)
        try:
            fee_ars = convert_currency(u.name, "ARS", fee_local)
        except Exception:
            fee_ars = None

        # 3) convert remaining amount to next currency for the next hop
        amount_next = convert_currency(u.name, v.name, amount_after_fee)

        hops.append({
            "from": u.name,
            "to": v.name,
            "fee_percent": edge.fee_percent,
            "fee_local": fee_local,
            "fee_ars": fee_ars,
            "amount_before": amount,
            "amount_after_fee": amount_after_fee,
            "amount_next": amount_next,
            "exchange": edge.exchange,
        })

        total_fee_local += fee_local
        if fee_ars is not None:
            total_fee_ars += fee_ars

        # move to next hop
        amount = amount_next

    # Final amount is in currency of last node
    final_ccy = path_nodes[-1].name
    try:
        final_amount_ars = convert_currency(final_ccy, "ARS", amount)
    except Exception:
        final_amount_ars = None

    return {
        "final_amount": amount,           # in final_ccy
        "final_amount_ars": final_amount_ars,
        "total_fee_local": total_fee_local,
        "total_fee_ars": total_fee_ars,
        "hops": hops,
    }


def evaluate_path(start_currency: str, target_currency: str, initial_amount: float):
    """
    High-level API:

    1. Build the graph
    2. Populate edge fees + log-space costs (update_costs)
    3. Run Dijkstra from start_currency
    4. Reconstruct the optimal path to target_currency
    5. Simulate chained fees and FX via _evaluate_path_nodes

    Returns the same structure as _evaluate_path_nodes plus the path:
        {
          "final_amount": ...,
          "final_amount_ars": ...,
          "total_fee_local": ...,
          "total_fee_ars": ...,
          "hops": [...],
          "path": ["ARS", "USDE", "SOL", "MXN"]
        }
    """
    # Build graph
    g = graph.Graph()
    g.update_costs()

    # Find start and target nodes
    start_node = None
    target_node = None

    for node in g.nodes:
        if node.name == start_currency:
            start_node = node
        if node.name == target_currency:
            target_node = node

    if start_node is None:
        raise ValueError(f"Start currency '{start_currency}' not found in graph")
    if target_node is None:
        raise ValueError(f"Target currency '{target_currency}' not found in graph")

    # Run Dijkstra
    costs, prev = dijkstra(g, start_node)

    # Reconstruct path
    path_nodes = reconstruct_path(prev, start_node, target_node)
    if path_nodes is None:
        # No path exists between these currencies in this graph
        return {
            "path": None,
            "final_amount": None,
            "final_amount_ars": None,
            "total_fee_local": None,
            "total_fee_ars": None,
            "hops": [],
        }

    # Evaluate path as before
    base_result = _evaluate_path_nodes(path_nodes, initial_amount)

    # Add the path as currency codes for convenience
    base_result["path"] = [node.name for node in path_nodes]

    return base_result
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

def evaluate_path(path_nodes, initial_amount: float):
    """
    Simulate chained fees along [n0, n1, ..., nk].

    - initial_amount is in currency path_nodes[0].name
    - Each hop applies fee_percent to the *current* amount
    - We track:
        * fee in local hop currency
        * fee converted to ARS
        * updated amount in next node's currency
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
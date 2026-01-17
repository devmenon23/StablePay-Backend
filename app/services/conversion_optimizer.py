import heapq

from app.models.graph import Graph

def dijkstra(graph: Graph, start):
    costs = {node: float("inf") for node in graph.nodes}
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
    Given a list of nodes [n0, n1, ..., nk] and initial_amount,
    compute final amount and total fee using the edge.fee_percent.
    """
    amount = initial_amount
    total_fee = 0.0
    hops = []

    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i + 1]

        edge = next(e for e in u.edges if e.to_node is v)

        fee = amount * edge.fee_percent
        amount_after = amount - fee

        hops.append(
            {
                "from": u.name,
                "to": v.name,
                "fee": fee,
                "fee_percent": edge.fee_percent,
                "amount_before": amount,
                "amount_after": amount_after,
                "exchange": edge.exchange,
            }
        )

        total_fee += fee
        amount = amount_after

    return {
        "final_amount": amount,
        "total_fee": total_fee,
        "hops": hops,
    }

# conversion_optimizer.py
import heapq
import graph

def dijkstra(graph, start):
    costs = {node: float('inf') for node in graph.nodes}
    
    costs[start] = 0
    pq = [(0, start.name, start)]
    prev = {node: None for node in costs}
    
    while pq:
        currCost, name,u = heapq.heappop(pq)

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

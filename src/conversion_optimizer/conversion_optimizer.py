import heapq
from math import inf

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph.nodes}
    
    dist[start] = 0
    pq = [(0, start)]
    prev = {node: None for node in dist}  # for path reconstruction

    while pq:
        currCost, u = heapq.heappop(pq)

        # Skip if we already found a better path
        if currCost > dist[u]:
            continue

        for v, c in graph[u]:
            newCost = currCost + c
            if newCost < dist[v]:
                dist[v] = newCost
                prev[v] = u
                heapq.heappush(pq, (newCost, v))

    return dist, prev

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

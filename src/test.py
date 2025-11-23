#test.py
from graph import Graph
from conversion_optimizer import dijkstra, reconstruct_path, evaluate_path

g = Graph()
g.update_costs()
for n in g.nodes:
    for e in n.edges:
        print(n.name, "->", e.to_node.name, "cost:", e.cost, "fee%", e.fee_percent)

print("updated costs")
start_name = "USDE"
target_name = "ARS"
initial_amount = 1000.0  # 1000 USDC, for example

start_node = g.nodes[g.nametoindex[start_name]]
target_node = g.nodes[g.nametoindex[target_name]]

costs, prev = dijkstra(g, start_node)
print(costs)
path_nodes = reconstruct_path(prev, start_node, target_node)
result = evaluate_path(path_nodes, initial_amount)

print("Best path:", " -> ".join(n.name for n in path_nodes))
print("Final amount:", result["final_amount"])
print("Total fee:", result["total_fee"])
for hop in result["hops"]:
    print(hop)


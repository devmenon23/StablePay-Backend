from graph import Graph
from conversion_optimizer import dijkstra, reconstruct_path, evaluate_path

g = Graph()
g.update_costs()

start_name = "USDC"
target_name = "MXN"
initial_amount = 1000.0  # 1000 USDC, for example

start_node = next(n for n in g.nodes if n.name == start_name)
target_node = next(n for n in g.nodes if n.name == target_name)

costs, prev = dijkstra(g, start_node)
path_nodes = reconstruct_path(prev, start_node, target_node)

result = evaluate_path(path_nodes, initial_amount)

print("Best path:", " -> ".join(n.name for n in path_nodes))
print("Final amount:", result["final_amount"])
print("Total fee:", result["total_fee"])
for hop in result["hops"]:
    print(hop)


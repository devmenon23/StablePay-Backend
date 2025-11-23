# test.py
from graph import Graph
from conversion_optimizer import dijkstra, reconstruct_path, evaluate_path

# Build graph and update edge costs/fees
g = Graph()
g.update_costs()

print("=== Edges with costs and fee percents ===")
for n in g.nodes:
    for e in n.edges:
        print(
            f"{n.name} -> {e.to_node.name} | "
            f"cost (log-weight): {e.cost:.6f} | "
            f"fee%: {e.fee_percent:.6f}"
        )

print("\nupdated costs\n")

start_name = "USDE"
target_name = "ARS"
initial_amount = 1000.0  # 1000 USDE, for example

# (Optional) still run dijkstra directly if you want to inspect raw costs
start_node = g.nodes[g.nametoindex[start_name]]
costs, prev = dijkstra(g, start_node)
print("=== Dijkstra raw log-space costs from", start_name, "===")
for node, c in costs.items():
    print(f"{node.name}: {c}")

# Use the high-level evaluate_path which:
# - rebuilds its own Graph internally
# - runs dijkstra
# - reconstructs the optimal path
# - simulates chained fees and FX
result = evaluate_path(start_name, target_name, initial_amount)

print("\n=== Optimal Path Evaluation ===")

if result["path"] is None:
    print(f"No path found from {start_name} to {target_name}")
else:
    print("Best path:", " -> ".join(result["path"]))
    print(f"Initial amount: {initial_amount} {start_name}")
    print(f"Final amount: {result['final_amount']} {target_name}")
    print(f"Final amount in ARS: {result['final_amount_ars']}")
    print(f"Total fee (local currencies sum): {result['total_fee_local']}")
    print(f"Total fee in ARS: {result['total_fee_ars']}\n")

    print("=== Hop-by-hop breakdown ===")
    for hop in result["hops"]:
        print(
            f"{hop['from']} -> {hop['to']} | "
            f"fee%: {hop['fee_percent']:.6f} | "
            f"fee_local: {hop['fee_local']:.6f} {hop['from']} | "
            f"fee_ars: {hop['fee_ars']} ARS | "
            f"amount_before: {hop['amount_before']} {hop['from']} | "
            f"amount_after_fee: {hop['amount_after_fee']} {hop['from']} | "
            f"amount_next: {hop['amount_next']} {hop['to']} | "
            f"exchange: {hop['exchange']}"
        )

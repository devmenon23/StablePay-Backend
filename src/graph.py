# graph.py
import convert
import exchange_crypto
import exchange_fiat
import math

class Edge:
    def __init__(self, to_node, cost, exchange):
        self.to_node = to_node   # Node instance
        self.cost = cost         # numeric fee
        self.exchange = exchange # e.g. "moonpay", "bitso", etc.
    
    def __str__(self):
        return "edge: exchange [%s] to [%s] cost [%s]" % (
            self.exchange, self.to_node.name, self.cost
        )


class Node:
    def __init__(self, name: str):
        self.name = name
        self.edges = []  # list[Edge]

    def __str__(self):
        return "node: name %s edges: [%s]" % (
            self.name, ", ".join([str(edge) for edge in self.edges])
        )


# Treat these as fiat for routing / fee API selection
FIAT = {"USD", "ARS", "MXN"}

def get_fee_percent(from_currency: str, to_currency: str) -> tuple[float, str]:
    """
    Compute fee percentage p for the edge (from_currency -> to_currency).
    For FIAT edges, Bitso returns an absolute fee which we turn into a fraction.
    For crypto ↔ crypto edges, Swapzone gives us the fee fraction directly.
    Returns (p, exchange_name) where p is in [0, 1) if valid.
    """
    amount = convert.convert_currency("USD", from_currency, 1000)  # arbitrary notional; percent shouldn't depend on it
    # Case 1: at least one side is fiat → use Bitso
    if from_currency in FIAT or to_currency in FIAT:
        fee_percent, exchange = exchange_fiat.Get_cost(from_currency, to_currency, amount)
        return fee_percent, exchange

    # Case 2: crypto ↔ crypto → use Swapzone
    fee_percent, exchange = exchange_crypto.Get_cost(from_currency, to_currency, amount)

    return fee_percent, exchange


def get_neighbors(currency: str):
    """
    Hard-coded neighbor map for now.
    Replace with MoonPay/Bitso topology later.
    """
    neighbors = {
        "USDE": ["MXN", "SOL", "BTC"],
        "MXN":  ["USDE", "SOL", "BTC"],
        "ARS":  ["BTC", "SOL"],
        "SOL":  ["USDE", "BTC", "MXN", "ARS"],
        "BTC":  ["USDE", "SOL", "ARS", "MXN"],
    }
    return neighbors.get(currency, [])


class Graph:
    def __init__(self):
        # Define nodes
        self.nodes = [
            Node("USDE"),
            Node("ARS"),
            Node("MXN"),
            Node("SOL"),
            Node("BTC"),
        ]

        # Map from currency name to index in self.nodes
        self.nametoindex = {
            "USDE": 0,
            "ARS": 1,
            "MXN": 2,
            "SOL": 3,
            "BTC": 4,
        }

        # Build adjacency structure (edges with zero cost initially)
        self.setup_links()

    def add_edge(self, from_index: int, edge: Edge):
        self.nodes[from_index].edges.append(edge)

    def update_costs(self):
        """
        For each edge, fill in:
          - fee_percent (p)  as a fraction of value lost [0, 1)
          - cost = -log(1 - p)  # Dijkstra weight in log-space
        """
        for node in self.nodes:
            for edge in node.edges:
                p, exchange = get_fee_percent(node.name, edge.to_node.name)

                # Invalid or too expensive edge
                if (not math.isfinite(p)) or p <= 0.0 or p >= 1.0:
                    edge.cost = float("inf")
                    edge.fee_percent = p
                    edge.exchange = exchange
                    continue

                edge.fee_percent = p
                edge.exchange = exchange
                print(p, node.name, edge.to_node.name)
                # In log-space: multiplicative losses become additive weights.
                # If each edge keeps (1 - p_i) of value, total retention along path is
                #   Π(1 - p_i)
                # and we minimize sum(-log(1 - p_i)) instead.
                edge.cost = -math.log(1.0 - p)

    def setup_links(self):
        """
        Build edges between nodes based on get_neighbors().
        Costs and exchange names will be filled in later by update_costs().
        """
        for node in self.nodes:
            currencies = get_neighbors(node.name)
            from_index = self.nametoindex[node.name]

            for currency in currencies:
                if currency not in self.nametoindex:
                    continue

                to_index = self.nametoindex[currency]
                to_node = self.nodes[to_index]

                # Initial cost 0, exchange "", will be updated later
                self.add_edge(
                    from_index,
                    Edge(to_node, 0, "")
                )
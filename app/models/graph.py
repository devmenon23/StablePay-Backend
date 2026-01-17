import math

from app.core.config import FIAT_CURRENCIES

class Edge:
    def __init__(self, to_node, cost, exchange):
        self.to_node = to_node
        self.cost = cost
        self.exchange = exchange

    def __str__(self):
        return "edge: exchange [%s] to [%s] cost [%s]" % (
            self.exchange,
            self.to_node.name,
            self.cost,
        )


class Node:
    def __init__(self, name: str):
        self.name = name
        self.edges = []

    def __str__(self):
        return "node: name %s edges: [%s]" % (
            self.name,
            ", ".join([str(edge) for edge in self.edges]),
        )


def get_fee_percent(from_currency: str, to_currency: str) -> tuple[float, str]:
    """
    Compute fee percentage p for the edge (from_currency -> to_currency).
    For FIAT edges, Bitso returns an absolute fee which we turn into a fraction.
    For crypto to crypto edges, Swapzone gives us the fee fraction directly.
    """
    # Import here to avoid circular imports
    from app.services import exchange_crypto, exchange_fiat

    # Case 1: at least one side is fiat then use Bitso
    if from_currency in FIAT_CURRENCIES or to_currency in FIAT_CURRENCIES:
        fee_percent, exchange = exchange_fiat.get_trade_fee_for_pair(from_currency, to_currency)

        # No direct market or invalid pair
        if fee_percent == float("inf"):
            return float("inf"), exchange
    else:
        fee_percent, exchange = exchange_crypto.get_trade_fee_for_pair(from_currency, to_currency)

        # No direct market or invalid pair
        if fee_percent == float("inf"):
            return float("inf"), exchange
        
    return fee_percent, exchange


def get_neighbors(currency: str):
    """
    Hardcoded neighbor map for minimum viable product.
    """
    neighbors = {
        "USDC": ["MXN", "ARS", "SOL", "BTC"],
        "MXN": ["USDC", "SOL", "BTC"],
        "ARS": ["USDC", "BTC"],
        "SOL": ["USDC", "BTC", "MXN"],
        "BTC": ["USDC", "SOL", "ARS", "MXN"],
    }
    return neighbors.get(currency, [])

class Graph:
    def __init__(self):
        self.nodes = [
            Node("USDC"),
            Node("ARS"),
            Node("MXN"),
            Node("SOL"),
            Node("BTC"),
        ]

        self.nametoindex = {
            "USDC": 0,
            "ARS": 1,
            "MXN": 2,
            "SOL": 3,
            "BTC": 4,
        }

        self.setup_links()

    def add_edge(self, from_index: int, edge: Edge):
        self.nodes[from_index].edges.append(edge)

    def update_fees(self):
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

                self.add_edge(from_index, Edge(to_node, 0, ""))

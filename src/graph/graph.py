# graph.py
class Edge:
    def __init__(self, to_node, cost, exchange):
        self.to_node = to_node
        self.cost = cost
        self.exchange = exchange
    
    def __str__(self):
        return "edge: exchange [%s] to [%s] cost [%s]" % (
            self.exchange, self.to_node.name, self.cost
        )


class Node:
    def __init__(self, name):
        self.name = name
        self.edges = []

    def __str__(self):
        return "node: name %s edges: [%s]" % (
            self.name, ', '.join([str(edge) for edge in self.edges])
        )


def get_cost(from_node, to_node):
    fromcurency = from_node.name
    tocurrency = to_node
    
    # placeholder
    return 67, "transact"


def get_neighbors(currency):
    # placeholder – replace with API-based neighbors later
    neighbors = {
        "USDC": ["USD", "ARS", "SOL", "BTC"],
        "USD":  ["USDC", "ARS"],
        "ARS":  ["USDC", "USD"],
        "SOL":  ["USDC"],
        "BTC":  ["USDC"],
    }
    return neighbors.get(currency, [])


class Graph:
    def __init__(self):
        self.nodes = [
            Node("USDC"),
            Node("ARS"),
            Node("USD"),
            Node("SOL"),
            Node("BTC"),
        ]

        self.nametoindex = {
            "USDC": 0,
            "ARS": 1,
            "USD": 2,
            "SOL": 3,
            "BTC": 4,
        }

    def add_edge(self, from_index, edge):
        self.nodes[from_index].edges.append(edge)

    def update_costs(self):
        for node in self.nodes:
            for edge in node.edges:
                edge.cost, edge.exchange = get_cost(node, edge.to_node)

    def setup_links(self):
        for node in self.nodes:
            currencies = get_neighbors(node.name)

            # current node index
            from_index = self.nametoindex[node.name]

            for currency in currencies:
                if currency not in self.nametoindex:
                    continue

                to_index = self.nametoindex[currency]
                to_node = self.nodes[to_index]

                # cost initially 0, exchange empty
                self.add_edge(
                    from_index,
                    Edge(to_node, 0, "")
                )

g = Graph()
print(g.nodes[1])
g.setup_links()
#g.add_edge(1, Edge(g.nodes[2], 2, "moonpay"))
#g.add_edge(1, Edge(g.nodes[3], 2, "moonpay"))
print(g.nodes[1])
g.update_costs()
print(g.nodes[1])
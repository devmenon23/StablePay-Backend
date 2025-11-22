# graph.py
class Edge:
    def __init__(self, to_node, cost, exchange):
        self.to_node = to_node
        self.cost = cost
        self.exchange = exchange
    def __str__(self):
        return "edge: exchange [%s] to [%s] cost [%s]" % (self.exchange, self.to_node.name, self.cost)

class Node:
    def __init__(self, name):
        self.name = name
        self.edges = []
    def __str__(self):
        return "node: name %s edges: [%s]" % (self.name, ', '.join([str(edge) for edge in self.edges]))

def get_cost(from_node, to_node):
    # returns cost, exchange
    # not yet implemented
    return 67, "transact"

def get_neighbors(currency):
    # returns list of currencies this currency can be converted to

class Graph:
    def __init__(self):
        self.nodes = [
            Node("USDC"),
            Node("ARS"),
            Node("USD"),
            Node("SOL"),
            Node("BTC"),
            ]
            self.nametonode = {
            Node("USDC"):0,
            Node("ARS"):1,
            Node("USD"):2,
            Node("SOL"):3,
            Node("BTC"):4,
            }
    def add_edge(self, from_node, edge):
        self.nodes[from_node].edges.append(edge)
    def update_costs(self):
        for node in self.nodes:
            for edge in node.edges:
                edge.cost, edge.exchange = get_cost(node, edge.to_node)
    def links(self, node):
        # returns list of nodes this node should be connected to
        currencies = get_neighbors(currency)
        for currency in currencies:
            if not 
        

def link(graph):
    for node in self.nodes:
        
        graph.add_edge(node, )


g = Graph()
print(g.nodes[1])
g.add_edge(1, Edge(g.nodes[2], 2, "moonpay"))
g.add_edge(1, Edge(g.nodes[3], 2, "moonpay"))
print(g.nodes[1])
g.update_costs()
print(g.nodes[1])
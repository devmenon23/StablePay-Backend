# graph.py
class Edge:
    def __init__(self, to_node, cost):
        self.to_node = to_node
        self.cost = cost
    def __str__(self):
        return "edge: to [%s] cost [%d]" % (self.to_node.name, self.cost)

class Node:
    def __init__(self, name):
        self.name = name
        self.edges = []
    def __str__(self):
        return "node: name %s edges: [%s]" % (self.name, ', '.join([str(edge) for edge in self.edges]))

class Graph:
    def __init__(self):
        self.nodes = [
            Node("USDC"),
            Node("ARS"),
            Node("USD"),
            Node("SOL"),
            Node("BTC"),
            ]

    def add_edge(self, from_node, edge):
        self.nodes[from_node].edges.append(edge)
    def update_edge


g = Graph()
g.add_edge(1, Edge(g.nodes[2], 2))
g.add_edge(1, Edge(g.nodes[3], 2))
print(g.nodes[1])
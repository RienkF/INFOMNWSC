# From the main graph, randomly sample n nodes and their edges from the graph

from random import sample

import networkx as nx


def generate_random_graph(
    G: nx.DiGraph,
    n: int,
) -> nx.DiGraph:
    random_nodes = sample(list(G.nodes), n)
    return nx.subgraph(G, random_nodes)

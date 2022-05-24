import networkx

from networkx import subgraph_view, edge_boundary


# TODO: Type partition
def global_edge_ratio(G: networkx.DiGraph, partitions):
    score_sum = 0
    for partition in partitions:
        internal_edges = len(G.subgraph(partition).edges)
        out_edges = len(list(edge_boundary(G, partition, G.nodes - partition)))
        score_sum += internal_edges / (internal_edges + out_edges)
    return score_sum

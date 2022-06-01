# Normalized mutual information score for community detection
from collections import defaultdict

import networkx as nx
from sklearn.metrics import normalized_mutual_info_score

from algorithm.edge_ratio import local_edge_ratio, global_edge_ratio

Partitions = list[set[str]]


def nmi_score(labels_true: Partitions, labels_pred: Partitions) -> float:
    return normalized_mutual_info_score(labels_true, labels_pred)


def get_ground_truth_partitions(G: nx.DiGraph) -> Partitions:
    # Use 'court' labels on nodes to get partitions corresponding to each court
    partitions = defaultdict(set)
    for node in G.nodes:
        court = G.nodes[node]["court"]
        partitions[court].add(node)
    return partitions


COMMUNITY_MEASURES = {
    "edge_ratio": {
        "name": "Edge Ratio",
        "local_score": local_edge_ratio,
        "global_score": global_edge_ratio,
    }
}

# Get edge probabilities between different communities of the graph to feed into the stochastic block model
from collections import defaultdict

import networkx as nx
import csv
from pathlib import Path

from main import load_network


def main():
    G = load_network()
    # "court" field contains ground truth community labels
    nodes_by_community = defaultdict(set)
    for node in G.nodes:
        court = G.nodes[node].get("court", None)
        # Ignore nodes without a ground truth community label
        if court is not None:
            nodes_by_community[court].add(node)
    # Count number of edges between each pair of communities
    edges_by_community_pair = defaultdict(int)
    for u, v in G.edges:
        u_court = G.nodes[u].get("court", None)
        v_court = G.nodes[v].get("court", None)
        if u_court is not None and v_court is not None:
            edges_by_community_pair[(u_court, v_court)] += 1
    # Normalize edge probabilities out of number of possible edges between each pair of communities
    edge_probabilities = {}
    for (u_court, v_court), count in edges_by_community_pair.items():
        edge_probabilities[(u_court, v_court)] = count / (len(nodes_by_community[u_court]) * len(nodes_by_community[v_court]))
    # Write edge probabilities to file
    with open(Path("data", "edge_probabilities.csv"), "w") as f:
        writer = csv.writer(f)
        for (u_court, v_court), probability in edge_probabilities.items():
            writer.writerow([u_court, v_court, probability])


if __name__ == "__main__":
    main()

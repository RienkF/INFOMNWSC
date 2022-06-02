# Generate stochastic block model graphs from edge probability CSV
from collections import defaultdict

import networkx as nx
import csv
from pathlib import Path

from algorithm.edge_ratio import global_edge_ratio


def get_sbm_graph(
    n: int, community_sizes: list[float], edge_prob_mat: list[list[float]], seed=None
) -> nx.DiGraph:
    community_sizes = [int(round(n * s)) for s in community_sizes]
    G = nx.stochastic_block_model(
        community_sizes, edge_prob_mat, seed=seed, directed=True
    )
    # Add weight=1 to each edge
    for u, v in G.edges:
        G[u][v]["weight"] = 1
    return G


def get_edge_probabilities(edge_prob_csv: Path) -> list[list[float]]:
    # Outer key: citing community, inner key: cited community, value: probability of edges
    edge_prob_dict: dict[str, dict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    communities = set()
    with open(edge_prob_csv, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            communities.add(row[0])
            communities.add(row[1])
            edge_prob_dict[row[0]][row[1]] = float(row[2])
    communities = sorted(communities)
    edge_prob_mat: list[list[float]] = []
    for comm in communities:
        edge_prob_mat.append([edge_prob_dict[comm][c] for c in communities])
    return edge_prob_mat


def get_community_sizes(community_size_csv: Path) -> list[float]:
    # Returns fractions, not absolute sizes
    community_sizes: list[float] = []
    with open(community_size_csv, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            community_sizes.append(float(row[1]))
    return community_sizes


def main():
    edge_prob_mat = get_edge_probabilities(Path("data", "edge_probabilities.csv"))
    community_sizes = get_community_sizes(Path("data", "community_sizes.csv"))
    # print(edge_prob_mat)
    G = get_sbm_graph(
        n=5000,
        community_sizes=community_sizes,
        edge_prob_mat=edge_prob_mat,
        seed=2022_1,
    )
    print(f"Edge ratio: {global_edge_ratio(G, G.graph['partition'])}")
    print(f"Modularity: {nx.community.modularity(G, G.graph['partition'])}")


if __name__ == "__main__":
    main()

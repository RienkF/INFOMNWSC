# Generate stochastic block model graphs from edge probability CSV
from collections import defaultdict

import networkx as nx
import csv
from pathlib import Path

from algorithm.edge_ratio import global_edge_ratio

AVG_DEGREE = 6.78366


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


EDGE_PROBS = get_edge_probabilities(Path("data", "edge_probabilities.csv"))
COMMUNITY_SIZES = get_community_sizes(Path("data", "community_sizes.csv"))


def generate_sbm_graph(
    n: int,
    community_sizes=None,
    edge_prob_mat=None,
    seed=None,
) -> nx.DiGraph:
    if edge_prob_mat is None:
        edge_prob_mat = EDGE_PROBS
    if community_sizes is None:
        community_sizes = COMMUNITY_SIZES
    community_sizes = [int(round(n * s)) for s in community_sizes]
    # Preserve the average degree of the original graph
    edge_prob_mat = get_scaled_edge_probs(AVG_DEGREE, edge_prob_mat, community_sizes)
    G = nx.stochastic_block_model(
        community_sizes, edge_prob_mat, seed=seed, directed=True
    )
    # Add weight=1 to each edge
    for u, v in G.edges:
        G[u][v]["weight"] = 1
    return G


def get_scaled_edge_probs(
    desired_avg_degree: float,
    edge_prob_mat: list[list[float]],
    community_sizes: list[int],
) -> list[list[float]]:
    desired_num_edges = sum(community_sizes) * desired_avg_degree
    num_edges_before_scaling = 0
    for i in range(len(edge_prob_mat)):
        for j in range(len(edge_prob_mat[i])):
            curr_possible_edges = community_sizes[i] * community_sizes[j]
            num_edges_before_scaling += curr_possible_edges * edge_prob_mat[i][j]
    scaling_factor = desired_num_edges / num_edges_before_scaling
    return [[p * scaling_factor for p in row] for row in edge_prob_mat]


def main():
    G = generate_sbm_graph(1000)
    print(f"Edge ratio: {global_edge_ratio(G, G.graph['partition'])}")
    print(f"Modularity: {nx.community.modularity(G, G.graph['partition'])}")


if __name__ == "__main__":
    main()

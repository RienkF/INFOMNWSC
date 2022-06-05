# Get edge probabilities between different communities of the graph to feed into the stochastic block model
from collections import defaultdict

import networkx as nx
import csv
from pathlib import Path
import powerlaw

from main import load_network


def main():
    G = load_network()
    # "court" field contains ground truth community labels
    # nodes_by_community = defaultdict(set)
    # for node in G.nodes:
    #     court = G.nodes[node].get("court", None)
    #     # Ignore nodes without a ground truth community label
    #     if court is not None:
    #         nodes_by_community[court].add(node)
    # create_edge_prob_csv(G, nodes_by_community)
    # create_community_size_csv(nodes_by_community)
    print(estimate_power_law_degree_exponent(G))


def create_edge_prob_csv(G, nodes_by_community):
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
        denom = len(nodes_by_community[u_court]) * len(nodes_by_community[v_court])
        if u_court == v_court:
            # Within the same community, # of possible edges is n(n-1)
            denom -= len(nodes_by_community[u_court])
        edge_probabilities[(u_court, v_court)] = count / denom
    # Write edge probabilities to file
    with open(Path("data", "edge_probabilities.csv"), "w") as f:
        writer = csv.writer(f)
        for (u_court, v_court), probability in edge_probabilities.items():
            writer.writerow([u_court, v_court, probability])


def create_community_size_csv(nodes_by_community: dict[set]):
    # Relative size of each community
    total_nodes = sum(len(nodes) for nodes in nodes_by_community.values())
    with open(Path("data", "community_sizes.csv"), "w") as f:
        writer = csv.writer(f)
        for community, nodes in nodes_by_community.items():
            writer.writerow([community, len(nodes) / total_nodes])


def estimate_power_law_degree_exponent(G):
    degrees = [d for n, d in G.degree()]
    fit = powerlaw.Fit(degrees)
    # Now do a powerlaw fit for the community sizes
    nodes_by_community = defaultdict(set)
    for node in G.nodes:
        court = G.nodes[node].get("court", None)
        if court is not None:
            nodes_by_community[court].add(node)
    community_sizes = [len(nodes) for nodes in nodes_by_community.values()]
    print(community_sizes)
    fit2 = powerlaw.Fit(community_sizes)
    return fit.power_law.alpha, fit2.power_law.alpha


if __name__ == "__main__":
    main()

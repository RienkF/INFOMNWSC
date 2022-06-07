# Normalized mutual information score for community detection
import csv
from pathlib import Path

from sklearn.metrics import normalized_mutual_info_score

import networkx as nx

from algorithm.modularity_density import (
    local_modularity_density,
    global_modularity_density,
)
from graph_generation_sbm import generate_sbm_graph

# from louvain import louvain_communities
from algorithm.louvain import louvain_communities
from utils.types import Partition, Labels

GRAPH_SIZE = 5000

RANDOM_GRAPH_SEEDS = (
    2022_0,
    2022_1,
    2022_2,
    2022_3,
    2022_4,
    2022_5,
    2022_6,
    2022_7,
    2022_8,
    2022_9,
)

COMMUNITY_MEASURES = {
    # "edge_ratio": {
    #     "name": "Edge Ratio",
    #     "partition_func": lambda G: louvain_communities(
    #         G,
    #         global_edge_ratio,
    #         local_edge_ratio,
    #     ),
    # },
    # "modularity": {
    #     "name": "Modularity",
    #     # "partition_func": lambda G: louvain_communities(G),
    #     "partition_func": lambda G: louvain_communities(
    #         G,
    #         global_modularity,
    #         local_modularity,
    #     ),
    # },
    "modularity_density": {
        "name": "Modularity Density",
        "partition_func": lambda G: louvain_communities(
            G,
            global_modularity_density,
            local_modularity_density,
        ),
    },
}


def nmi_format_partition(partition: Partition) -> Labels:
    node_comm_dict = {
        node: comm for comm, nodes in enumerate(partition) for node in nodes
    }
    return [node_comm_dict[node] for node in sorted(list(node_comm_dict.keys()))]


def nmi_score(labels_true: Partition, labels_pred: Partition) -> float:
    partition = nmi_format_partition(labels_true)
    format_partition = nmi_format_partition(labels_pred)
    return normalized_mutual_info_score(partition, format_partition)


def run_benchmarks(
    graph_seeds=RANDOM_GRAPH_SEEDS,
    measures=tuple(COMMUNITY_MEASURES.keys()),
    graph_size=GRAPH_SIZE,
    output_file=Path("data", "benchmark_results.csv"),
):
    """
    Testing procedure: for each SBM graph (created from seed), run the louvain algorithm with each measure.
    Then, compare the resulting partitions with the ground truth partition using NMI.
    """
    nmi_results: dict[str, dict] = {}
    for measure in measures:
        print(f"Running benchmark for measure {measure}...")
        nmi_scores = []
        for seed in graph_seeds:
            G = generate_sbm_graph(graph_size, seed=seed)
            partition = COMMUNITY_MEASURES[measure]["partition_func"](G)
            ground_truth_partition = G.graph["partition"]
            print(
                f"Modularity for ground truth: {nx.algorithms.community.modularity(G, ground_truth_partition)}"
            )
            print(
                f"Modularity for algorithm: {nx.algorithms.community.modularity(G, partition)}"
            )
            nmi_scores.append(nmi_score(ground_truth_partition, partition))
            print(
                f"Measure {measure}, Seed {seed}: NMI"
                f" {nmi_score(ground_truth_partition, partition)}"
            )
        nmi_results[measure] = {
            "mean_nmi": sum(nmi_scores) / len(nmi_scores),
        }
        nmi_results[measure]["variance_nmi"] = sum(
            [(x - nmi_results[measure]["mean_nmi"]) ** 2 for x in nmi_scores]
        ) / len(nmi_scores)
    save_benchmark_results(nmi_results, output_file)


def save_benchmark_results(nmi_results, output_file):
    with open(output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Measure", "Mean NMI", "Variance NMI"])
        for measure, results in nmi_results.items():
            writer.writerow([measure, results["mean_nmi"], results["variance_nmi"]])


def main():
    run_benchmarks()


if __name__ == "__main__":
    main()

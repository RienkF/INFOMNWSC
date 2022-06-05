# Normalized mutual information score for community detection
import csv

import networkx as nx
from sklearn.metrics import normalized_mutual_info_score

from algorithm.edge_ratio import local_edge_ratio, global_edge_ratio
from graph_generation import generate_sbm_graph
from louvain import louvain_communities

Parttion = list[set[str]]

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
    "edge_ratio": {
        "name": "Edge Ratio",
        "partition_func": lambda G: louvain_communities(
            G,
            global_edge_ratio,
            local_edge_ratio,
        ),
    },
    "modularity": {
        "name": "Modularity",
        "partition_func": lambda G: nx.community.louvain_communities(G),
    },
}


def nmi_score(labels_true: Parttion, labels_pred: Parttion) -> float:
    return normalized_mutual_info_score(labels_true, labels_pred)


def run_benchmarks(
    graph_seeds=RANDOM_GRAPH_SEEDS,
    measures=tuple(COMMUNITY_MEASURES.keys()),
    graph_size=5000,
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


def save_benchmark_results(nmi_results, output_file):
    with open(output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Measure", "Mean NMI", "Variance NMI"])
        for measure, results in nmi_results.items():
            writer.writerow([measure, results["mean_nmi"], results["variance_nmi"]])

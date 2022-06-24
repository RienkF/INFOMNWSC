"""
The script that tests the performance of the different community measures on the synthetic graphs
and records the results in CSV files.
"""

import csv
from pathlib import Path

from sklearn.metrics import normalized_mutual_info_score

from algorithm.edge_ratio import (
    local_edge_ratio,
    global_edge_ratio,
)
from algorithm.intensity_ratio import (
    local_intensity_ratio,
    global_intensity_ratio,
)
from algorithm.modularity import (
    local_modularity,
    global_modularity,
)
from algorithm.modularity_density import (
    local_modularity_density,
    global_modularity_density,
)
from graph_generation_fs import generate_fs_graph

from algorithm.louvain import louvain_communities
from utils.types import Partition, Labels

GRAPH_SIZE = 5_000

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

# For each community measure, we provide a name and a function that
# runs our Louvain algorithm with the given measure.
COMMUNITY_MEASURES = {
    "edge_ratio": {
        "name": "Edge Ratio",
        "partition_func": lambda G: louvain_communities(
            G,
            global_edge_ratio,
            local_edge_ratio,
        ),
    },
    "intensity_ratio": {
        "name": "Intensity Ratio",
        "partition_func": lambda G: louvain_communities(
            G,
            global_intensity_ratio,
            local_intensity_ratio,
        ),
    },
    "modularity": {
        "name": "Modularity",
        "partition_func": lambda G: louvain_communities(
            G,
            global_modularity,
            local_modularity,
        ),
    },
    "modularity_density": {
        "name": "Modularity Density",
        "partition_func": lambda G: louvain_communities(
            G,
            global_modularity_density,
            local_modularity_density,
        ),
    },
}

NAME_TO_GLOBAL_FUNC = {
    "edge_ratio": global_edge_ratio,
    "intensity_ratio": global_intensity_ratio,
    "modularity": global_modularity,
    "modularity_density": global_modularity_density,
}


def nmi_format_partition(partition: Partition) -> Labels:
    """
    Convert a partition to a format that can be used by NMI.
    :param partition: A list of sets of nodes where each set represents a community/label.
    :return: A single list of labels where labels[i] is the label of the i-th node.
    """
    node_comm_dict = {
        node: comm for comm, nodes in enumerate(partition) for node in nodes
    }
    # Sort the list so that the labels correspond to the nodes in the same order.
    return [node_comm_dict[node] for node in sorted(list(node_comm_dict.keys()))]


def nmi_score(labels_true: Partition, labels_pred: Partition) -> float:
    return normalized_mutual_info_score(
        nmi_format_partition(labels_true), nmi_format_partition(labels_pred)
    )


def run_benchmarks(
    graph_seeds=RANDOM_GRAPH_SEEDS,
    measures=tuple(COMMUNITY_MEASURES.keys()),
    graph_size=GRAPH_SIZE,
    summary_output_file=Path("data", "benchmark_results.csv"),
    full_output_file=Path("data", "benchmark_results_full.csv"),
):
    """
    Testing procedure: for each synthetic graph (created from seed), run the louvain algorithm with each measure.
    Then, compare the resulting partitions with the ground truth partition using NMI.
    """
    nmi_results: dict[str, dict] = {}
    for measure in measures:
        print(f"Running benchmark for measure {measure}...")
        nmi_scores = []
        for seed in graph_seeds:
            G = generate_fs_graph(graph_size, seed=seed)
            # Run the louvain algorithm with the given measure. and get the resulting partition.
            partition = COMMUNITY_MEASURES[measure]["partition_func"](G)
            ground_truth_partition = G.graph["partition"]
            # Log the measure scores for both the partition and the ground truth partition.
            print(
                f"{measure} for ground truth:"
                f" {NAME_TO_GLOBAL_FUNC[measure](G, ground_truth_partition, G.size())}"
            )
            print(
                f"{measure} for algorithm:"
                f" {NAME_TO_GLOBAL_FUNC[measure](G, partition, G.size())}"
            )
            print(f"Ground truth partition size: {len(ground_truth_partition)}")
            print(f"Algorithm partition size: {len(partition)}")
            # Compute the NMI score between the partition and the ground truth partition.
            nmi_scores.append(nmi_score(ground_truth_partition, partition))
            print(
                f"Measure {measure}, Seed {seed}: NMI"
                f" {nmi_score(ground_truth_partition, partition)}"
            )
        nmi_results[measure] = {
            "full_results": nmi_scores,
            "mean_nmi": sum(nmi_scores) / len(nmi_scores),
        }
        nmi_results[measure]["variance_nmi"] = sum(
            [(x - nmi_results[measure]["mean_nmi"]) ** 2 for x in nmi_scores]
        ) / len(nmi_scores)
    save_benchmark_results(nmi_results, summary_output_file, full_output_file)


def save_benchmark_results(nmi_results, summary_output_file, full_output_file):
    """
    Save the benchmark results to two CSV files. One file contains a statistical
    summary of the results, and the other contains the results on a granular level.
    :param nmi_results: A dictionary of the form {measure: {full_results: list[float], mean_nmi: float, variance_nmi: float}}
    :param summary_output_file: The path to the summary CSV file.
    :param full_output_file: The path to the full results CSV file.
    """
    with open(summary_output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Measure", "Mean NMI", "Variance NMI"])
        for measure, results in nmi_results.items():
            writer.writerow([measure, results["mean_nmi"], results["variance_nmi"]])
    with open(full_output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Measure", "Seed", "NMI"])
        for measure, results in nmi_results.items():
            for seed, nmi in zip(RANDOM_GRAPH_SEEDS, results["full_results"]):
                writer.writerow([measure, seed, nmi])


def main():
    run_benchmarks()


if __name__ == "__main__":
    main()

import networkx

from algorithm.modularity import global_modularity, local_modularity
from utils.types import Partition


def global_modularity_density(G: networkx.DiGraph, partitions: Partition, m: int):
    """
    Calculates the modularity density score.
    :param G: Total graph
    :param partitions: Partitions on te graph
    :param m: size of the graph.
    :return: Edge ratio score
    """
    modularity_score = global_modularity(G, partitions, m)

    split_penalty = 0

    for partition in partitions:
        for u in partition:
            for (
                _,
                n,
                wt,
            ) in G.out_edges(u, "weight"):
                if n not in partition:
                    split_penalty += wt

    return modularity_score - (split_penalty / m)


def local_modularity_density(
    G: networkx.DiGraph,
    u: int,
    neighbour: int,
    node_to_community: dict,
    inner_partition: Partition,
    m: int,
):
    """
    Calculates the change in modularity score if u is moved to the community of the given neighbour.
    :param G: Total graph
    :param u: node that will be moved
    :param neighbour: Neighbour partition to which the node will be moved.
    :param node_to_community: Dictionary that maps nodes to communities.
    :param inner_partition: Partition in the current stage of louvain.
    :param m: Total amount of edges.
    :return: Change in local score
    """
    local_modularity_gain = local_modularity(
        G,
        u,
        neighbour,
        node_to_community,
        inner_partition,
        m,
    )

    u_partition = inner_partition[node_to_community[u]]
    neighbour_partition = inner_partition[node_to_community[neighbour]]

    # Calculate the old split penalty
    split_penalty_decrease = 0
    for _, n, wt in G.out_edges(u, "weight"):
        if n in neighbour_partition:
            split_penalty_decrease += wt
    for n, u, wt in G.in_edges(u, "weight"):
        if n in neighbour_partition:
            split_penalty_decrease += wt

    # Calculate the new split penalty
    split_penalty_increase = 0
    for _, n, wt in G.out_edges(u, "weight"):
        if n in u_partition and n != u:
            split_penalty_increase += wt
    for n, _, wt in G.in_edges(u, "weight"):
        if n in u_partition and n != u:
            split_penalty_increase += wt

    # Return modularity gain with the split penalty gain
    return local_modularity_gain + (
        (split_penalty_decrease - split_penalty_increase) / m
    )

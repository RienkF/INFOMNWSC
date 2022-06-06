import networkx

from itertools import chain


# TODO: Type partition
from networkx.algorithms.community import modularity

from algorithm.modularity import global_modularity, local_modularity


def global_modularity_density(G: networkx.DiGraph, partitions):
    m = G.size()
    modularity_score = global_modularity(G, partitions)

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
    u,
    neighbour,
    node_to_community,
    inner_partition,
    partition,
    original_graph: networkx.DiGraph,
    m: int,
):
    """
    Calculates the change in modularity score if u is moved to the community of the given neighbour.
    :param G: Total graph
    :param u: node that will be moved
    :param neighbour: Neighbour partition to which the node will be moved.
    :param node_to_community: Dictionary that maps nodes to communities.
    :param inner_partition: Partition in the current stage of louvain.
    :param partition: Total partition of the complete graph.
    :param original_graph: The original graph used at the start of the algorithm.
    :param m: Total amount of edges.
    :return: Change in local score
    """

    m = G.size()

    local_modularity_gain = local_modularity(
        G,
        u,
        neighbour,
        node_to_community,
        inner_partition,
        partition,
        original_graph,
        m,
    )

    u_partition = inner_partition[node_to_community[u]]
    neighbour_partition = inner_partition[node_to_community[neighbour]]

    split_penalty_decrease = 0
    for _, n, wt in G.out_edges(u, "weight"):
        if n in neighbour_partition:
            split_penalty_decrease += wt
    for n, u, wt in G.in_edges(u, "weight"):
        if n in neighbour_partition:
            split_penalty_decrease += wt

    split_penalty_increase = 0
    for _, n, wt in G.out_edges(u, "weight"):
        if n in u_partition and n != u:
            split_penalty_increase += wt
    for n, _, wt in G.in_edges(u, "weight"):
        if n in u_partition and n != u:
            split_penalty_increase += wt

    return local_modularity_gain + (
        (split_penalty_decrease - split_penalty_increase) / m
    )

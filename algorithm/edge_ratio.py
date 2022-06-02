import networkx

from itertools import chain


# TODO: Type partition
def global_edge_ratio(G: networkx.DiGraph, partitions):
    return sum(map(lambda partition: edge_boundary_ratio(G, partition), partitions))


def local_edge_ratio(
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
    Calculates the change in score if u is moved to the community of the given neighbour.
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
    u_partition = inner_partition[node_to_community[u]]
    old_score_u = edge_boundary_ratio(G, u_partition)

    neighbour_partition = inner_partition[node_to_community[neighbour]]
    old_score_neighbour = edge_boundary_ratio(G, neighbour_partition)

    neighbour_partition_with_u = [u, *neighbour_partition]
    new_score_u_and_neighbour = edge_boundary_ratio(G, neighbour_partition_with_u)

    u_partition_without_u = u_partition - {u}
    new_score_u_partition_without_u = edge_boundary_ratio(G, u_partition_without_u)

    return (
        new_score_u_and_neighbour
        + new_score_u_partition_without_u
        - old_score_u
        - old_score_neighbour
    )


def edge_boundary_ratio(G: networkx.DiGraph, partition):
    """
    Calculates the the edge boundary ratio efficiently by checking each edge
    """
    edge_boundary_size = 0
    in_edge_size = 0
    partition = set(partition)
    for node in partition:
        for edge in G.out_edges(node, "weight"):
            if edge[1] not in partition:
                edge_boundary_size += edge[2]
            else:
                in_edge_size += edge[2]
        for edge in G.in_edges(node, "weight"):
            if edge[0] not in partition:
                edge_boundary_size += edge[2]
            else:
                in_edge_size += edge[2]
    in_edge_size = in_edge_size / 2
    if in_edge_size == 0:
        return 0
    return in_edge_size / (edge_boundary_size + in_edge_size)

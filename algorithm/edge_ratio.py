import networkx

from networkx import subgraph_view, edge_boundary
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
):
    """
    Calculates the change in score if u is moved to the community of the given neighbour.
    :param G: Total graph
    :param u: node that will be moved
    :param neighbour: Neighbour partition to which the node will be moved.
    :param node_to_community: Dictionary that maps nodes to communities.
    :param inner_partition: Partition in the current stage of louvain.
    :param partition: Total partition of the complete graph.
    :return: Change in local score
    """
    nodes_in_u = G.nodes[u].get("nodes", {u})

    old_score_u = edge_boundary_ratio(original_graph, nodes_in_u)

    nodes_in_neighbour = G.nodes[neighbour].get("nodes", {neighbour})
    old_score_neighbour = edge_boundary_ratio(original_graph, nodes_in_neighbour)

    nodes_in_u_and_neighbour = [*nodes_in_u, *nodes_in_neighbour]
    new_score = edge_boundary_ratio(original_graph, nodes_in_u_and_neighbour)

    return new_score - old_score_u - old_score_neighbour


def edge_boundary_ratio(G: networkx.DiGraph, partition):
    """
    Calculates the the edge boundary ratio efficiently by checking each edge
    """
    edge_boundary_size = 0
    in_edge_size = 0
    partition = set(partition)
    for node in partition:
        for neighbour in chain(G.predecessors(node), G.successors(node)):
            if neighbour not in partition:
                edge_boundary_size += 1
            else:
                in_edge_size += 1
    in_edge_size = in_edge_size / 2
    denom = edge_boundary_size + in_edge_size
    if denom == 0:
        return 0
    return in_edge_size / denom

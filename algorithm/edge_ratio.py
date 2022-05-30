import networkx

from networkx import subgraph_view, edge_boundary


# TODO: Type partition
def global_edge_ratio(G: networkx.DiGraph, partitions):
    score_sum = 0
    for partition in partitions:
        internal_edges = len(G.subgraph(partition).edges)
        out_edges = len(list(edge_boundary(G, partition, G.nodes - partition)))
        score_sum += internal_edges / (internal_edges + out_edges)
    return score_sum


def local_edge_ratio(
    G: networkx.DiGraph, u, neighbour, node_to_community, inner_partition, partition
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

    old_internal_edges_u = len(G.subgraph(nodes_in_u).edges)
    old_out_edges_u = len(list(edge_boundary(G, nodes_in_u, G.nodes - nodes_in_u)))
    old_score_u = old_internal_edges_u / (old_internal_edges_u + old_out_edges_u)

    nodes_in_neighbour = G.nodes[neighbour].get("nodes", {neighbour})

    old_internal_edges_neighbour = len(G.subgraph(nodes_in_neighbour).edges)
    old_out_edges_neighbour = len(
        list(edge_boundary(G, nodes_in_neighbour, G.nodes - nodes_in_neighbour))
    )
    old_score_neighbour = old_internal_edges_neighbour / (
        old_internal_edges_neighbour + old_out_edges_neighbour
    )

    nodes_in_u_and_neighbour = [*nodes_in_u, *nodes_in_neighbour]
    new_internal_edges = len(G.subgraph(nodes_in_u_and_neighbour).edges)
    new_out_edges = len(
        list(
            edge_boundary(
                G, nodes_in_u_and_neighbour, G.nodes - nodes_in_u_and_neighbour
            )
        )
    )
    new_score = new_internal_edges / (new_internal_edges + new_out_edges)

    return new_score - old_score_u - old_score_neighbour

import networkx

from utils.types import Partition


def global_modularity(G: networkx.DiGraph, partitions: Partition, m: int):
    """
    Calculates the modularity of the graph
    :param G: Total graph
    :param partitions: Partitions on te graph
    :param m: size of the graph.
    :return: Edge ratio score
    """
    score_sum = 0
    for partition in partitions:
        for u in partition:
            u_in_degree = sum(map(lambda x: x[2], G.in_edges(u, "weight")))
            for (
                _,
                n,
                wt,
            ) in G.out_edges(u, "weight"):
                if n in partition:
                    n_out_degree = sum(map(lambda x: x[2], G.out_edges(n, "weight")))
                    score_sum += wt - ((u_in_degree * n_out_degree) / m)
    return score_sum / m


def local_modularity(
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

    in_degree_u = sum(map(lambda x: x[2], G.in_edges(u, "weight")))
    out_degree_u = sum(map(lambda x: x[2], G.out_edges(u, "weight")))

    # removing u from the current partition
    u_partition = inner_partition[node_to_community[u]]

    remove_loss_out = sum(
        map(
            lambda edge: (
                edge[2]
                - (
                    (
                        in_degree_u
                        * sum(map(lambda x: x[2], G.out_edges(edge[1], "weight")))
                    )
                    / m
                )
            ),
            filter(lambda n: n[1] in u_partition, G.out_edges(u, "weight")),
        ),
    )
    remove_loss_in = sum(
        map(
            lambda edge: (
                edge[2]
                - (
                    (
                        sum(map(lambda x: x[2], G.in_edges(edge[0], "weight")))
                        * out_degree_u
                    )
                    / m
                )
            ),
            filter(lambda n: n[0] in u_partition, G.in_edges(u, "weight")),
        ),
    )

    # adding it to the neighbouring partition
    neighbour_partition = inner_partition[node_to_community[neighbour]]
    add_gain_out = sum(
        map(
            lambda edge: (
                edge[2]
                - (
                    (
                        in_degree_u
                        * sum(map(lambda x: x[2], G.out_edges(edge[1], "weight")))
                    )
                    / m
                )
            ),
            filter(lambda n: n[1] in neighbour_partition, G.out_edges(u, "weight")),
        ),
    )

    add_gain_in = sum(
        map(
            lambda edge: (
                edge[2]
                - (
                    (
                        sum(map(lambda x: x[2], G.in_edges(edge[0], "weight")))
                        * out_degree_u
                    )
                    / m
                )
            ),
            filter(lambda n: n[0] in neighbour_partition, G.in_edges(u, "weight")),
        ),
    )

    return add_gain_in + add_gain_out - remove_loss_in - remove_loss_out

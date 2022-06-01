import networkx

from itertools import chain


# TODO: Type partition
from networkx.algorithms.community import modularity


def global_modularity(G: networkx.DiGraph, partitions):
    return modularity(G, partitions)


def local_modularity(
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

    k_i_in = len(filter(lambda n: n in  G.successors(u)

    in_degree = len(original_graph.predecessors(u))
    out_degree = len(original_graph.successors(u))
    Stot_in = [deg for deg in in_degrees.values()]
    Stot_out = [deg for deg in out_degrees.values()]

    in_degree = in_degrees[u]
    out_degree = out_degrees[u]
    Stot_in[best_com] -= in_degree
    Stot_out[best_com] -= out_degree

    gain = wt - (out_degree * Stot_in[nbr_com] + in_degree * Stot_out[nbr_com]) / m

    Stot_in[best_com] += in_degree
    Stot_out[best_com] += out_degree

    return gain

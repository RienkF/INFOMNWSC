from collections import deque
from random import shuffle
from typing import Callable

import networkx as nx

from utils.types import Partition


def louvain_communities(
    G: nx.DiGraph,
    global_community_measure: Callable[[nx.DiGraph, Partition, int], float],
    local_community_measure: Callable[
        [nx.DiGraph, int, int, dict, Partition, int], float
    ],
):
    """
    Calculates the best partition for a given community measure using the louvain optimization algorithm.

    Parameters
    ----------
    G:
        The graph for which to calculate the communities.
    global_community_measure:
        Function to calculate the global score of a generic community structure measure.
    local_community_measure:
        Function to calculate the local gain in community measure score if the node represented by the second argument
        is moved to the community of the node represented by the third argument.
    :return:
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.
    """
    partitions = louvain_partitions(
        G,
        global_community_measure,
        local_community_measure,
    )
    q = deque(partitions, maxlen=1)
    return q.pop()


def louvain_partitions(
    G: nx.DiGraph,
    global_community_measure: Callable[[nx.DiGraph, Partition, int], float],
    local_community_measure: Callable[
        [nx.DiGraph, int, int, dict, Partition, int], float
    ],
) -> list[set[int]]:
    """Yields partitions for each level of the Louvain Community Detection Algorithm

    Parameters
    ----------
    G :
        The graph for which to calculate the best communities.
    global_community_measure:
        Function to calculate the global score of a generic community structure measure.
    local_community_measure:
        Function to calculate the local gain in community measure score if the node represented by the second argument
        is moved to the community of the node represented by the third argument.

    Yields
    ------
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.
    """
    # Initially every node is its own partition
    partition: Partition = [{u} for u in G.nodes()]

    # Create a copy of the graph
    graph = G.__class__()
    graph.add_nodes_from(G)
    graph.add_weighted_edges_from(G.edges(data="weight"))

    m = graph.size()

    # Get initial community score
    comm_score = global_community_measure(graph, partition, m)

    # Don't look at improvement on the first iteration
    partition, inner_partition, _ = _one_level(
        graph, m, partition, local_community_measure
    )
    improvement = True
    counter = 0
    while improvement:
        counter += 1
        yield partition
        new_community_score = global_community_measure(G, partition, m)
        if abs(new_community_score - comm_score) <= 0.0000000000001:
            return
        comm_score = new_community_score
        graph = _gen_graph(graph, inner_partition)
        partition, inner_partition, improvement = _one_level(
            graph, m, partition, local_community_measure
        )


def _one_level(
    G,
    m: int,
    partition: Partition,
    local_community_measure: Callable[
        [nx.DiGraph, int, int, dict, Partition, int], float
    ],
):
    """Calculate one level of the Louvain partitions tree

    Parameters
    ----------
    G : NetworkX Graph/DiGraph
        The graph from which to detect communities
    m : number
        The size of the graph `G`.
    partition:
        A valid partition of the graph `G`
    local_community_measure:
        Function to calculate the local gain in community measure score if the node represented by the second argument
        is moved to the community of the node represented by the third argument.
    """

    # Give each node its own community
    node_to_community = {u: i for i, u in enumerate(G.nodes())}
    inner_partition = [{u} for u in G.nodes()]

    # Go through the nodes in random order
    rand_nodes = list(G.nodes)
    shuffle(rand_nodes)
    nb_moves = 1
    improvement = False
    while nb_moves > 0:
        nb_moves = 0
        for u in rand_nodes:
            best_community_score = 0.0000000000001
            best_com = node_to_community[u]

            # We pass the node_to_community dict, as well as the current node, and its neighbours
            for neighbour in G.neighbors(u):
                if node_to_community[u] == node_to_community[neighbour]:
                    continue
                # Calculate the gain if u is moved to the community of this neighbour
                new_score = local_community_measure(
                    G,
                    u,
                    neighbour,
                    node_to_community,
                    inner_partition,
                    m,
                )
                if new_score > best_community_score:
                    best_community_score = new_score
                    best_com = node_to_community[neighbour]
                # best_com at the end of this will be the community that the node should now be in

            if best_com != node_to_community[u]:
                com = G.nodes[u].get("nodes", {u})
                # Update the global en local partitions
                partition[node_to_community[u]].difference_update(com)
                inner_partition[node_to_community[u]].remove(u)
                partition[best_com].update(com)
                inner_partition[best_com].add(u)
                improvement = True
                nb_moves += 1
                node_to_community[u] = best_com

    # Discard communities without any nodes.
    partition = list(filter(len, partition))
    inner_partition = list(filter(len, inner_partition))
    return partition, inner_partition, improvement


def _gen_graph(G: nx.DiGraph, partition: Partition):
    """
    Generate a new graph based on the partitions of a given graph
    :param G:
        The graph to transform.
    :param partition:
        The partition that should be used to transform the graph.
    :return:
         A new graph for which each partition is now a node.
    """
    new_graph = G.__class__()
    node_community_map = {}
    # For each partition, create a node.
    for i, part in enumerate(partition):
        nodes = set()
        for node in part:
            node_community_map[node] = i
            nodes.update(G.nodes[node].get("nodes", {node}))
        new_graph.add_node(i, nodes=nodes)

    # For each edge between two nodes in the original graph, add 1 weight to the edge between the nodes representing
    # the communities of the nodes.
    for node1, node2, weight in G.edges(data="weight"):
        com1 = node_community_map[node1]
        com2 = node_community_map[node2]
        temp = new_graph.get_edge_data(com1, com2, {"weight": 0})["weight"]
        new_graph.add_edge(com1, com2, **{"weight": weight + temp})
    return new_graph

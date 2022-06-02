from collections import deque
from random import shuffle
from typing import Callable

import networkx as nx

from algorithm.edge_ratio import global_edge_ratio


def louvain_communities(
    G: nx.DiGraph,
    global_community_measure: Callable,
    local_community_measure: Callable,
    resolution=1,
    threshold=0.0000001,
):
    partitions = louvain_partitions(
        G,
        global_community_measure,
        local_community_measure,
        resolution,
        threshold,
    )
    q = deque(partitions, maxlen=1)
    return q.pop()


def louvain_partitions(
    G: nx.DiGraph,
    global_community_measure: Callable,
    local_community_measure: Callable,
    resolution=1,
    threshold=0.0000001,
) -> list[set[int]]:
    """Yields partitions for each level of the Louvain Community Detection Algorithm

    Parameters
    ----------
    G : NetworkX graph
    resolution : float, optional (default=1)
        If resolution is less than 1, the algorithm favors larger communities.
        Greater than 1 favors smaller communities
    threshold : float, optional (default=0.0000001)
     Modularity gain threshold for each level. If the gain of modularity
     between 2 levels of the algorithm is less than the given threshold
     then the algorithm stops and returns the resulting communities.

    Yields
    ------
    list
        A list of sets (partition of `G`). Each set represents one community and contains
        all the nodes that constitute it.
    """
    partition = [{u} for u in G.nodes()]

    # Get initial community score
    comm_score = global_community_measure(G, partition)

    graph = G.__class__()
    graph.add_nodes_from(G)
    graph.add_weighted_edges_from(G.edges(data="weight"))
    print(f"Created graph copy")

    m = graph.size()
    # Don't look at improvement on the first iteration
    partition, inner_partition, _ = _one_level(
        graph, m, partition, local_community_measure, G, resolution
    )
    improvement = True
    counter = 0
    while improvement:
        print("Executing iteration {}".format(counter))
        counter += 1
        yield partition
        new_community_score = global_community_measure(G, partition)
        print(f"Calculated global measure score: {new_community_score}")
        if new_community_score - comm_score <= threshold:
            return
        comm_score = new_community_score
        graph = _gen_graph(graph, inner_partition)
        partition, inner_partition, improvement = _one_level(
            graph, m, partition, local_community_measure, G, resolution
        )


def _one_level(
    G,
    m: int,
    partition: list[set[int]],
    local_community_measure: Callable,
    original_graph: nx.DiGraph,
    resolution=1,
):
    """Calculate one level of the Louvain partitions tree

    Parameters
    ----------
    G : NetworkX Graph/DiGraph
        The graph from which to detect communities
    m : number
        The size of the graph `G`.
    partition : list of sets of nodes
        A valid partition of the graph `G`
    resolution : positive number
        The resolution parameter for computing the modularity of a partition
    """

    # Give each node its own community
    node_to_community = {u: i for i, u in enumerate(G.nodes())}
    inner_partition = [{u} for u in G.nodes()]

    nbrs = {u: list(G[u].keys()) for u in G}

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
                new_score = local_community_measure(
                    G,
                    u,
                    neighbour,
                    node_to_community,
                    inner_partition,
                    partition,
                    original_graph,
                    m,
                )
                if new_score > best_community_score:
                    best_community_score = new_score
                    best_com = node_to_community[neighbour]
                # best_com at the end of this will be the community that the node should now be in

            if best_com != node_to_community[u]:
                com = G.nodes[u].get("nodes", {u})
                partition[node_to_community[u]].difference_update(com)
                inner_partition[node_to_community[u]].remove(u)
                partition[best_com].update(com)
                inner_partition[best_com].add(u)
                improvement = True
                nb_moves += 1
                node_to_community[u] = best_com
    partition = list(filter(len, partition))
    inner_partition = list(filter(len, inner_partition))
    return partition, inner_partition, improvement


def _gen_graph(G, partition):
    """Generate a new graph based on the partitions of a given graph"""
    H = G.__class__()
    node_community_map = {}
    for i, part in enumerate(partition):
        nodes = set()
        for node in part:
            node_community_map[node] = i
            nodes.update(G.nodes[node].get("nodes", {node}))
        H.add_node(i, nodes=nodes)

    for node1, node2, weight in G.edges(data="weight"):
        com1 = node_community_map[node1]
        com2 = node_community_map[node2]
        temp = H.get_edge_data(com1, com2, {"weight": 0})["weight"]
        H.add_edge(com1, com2, **{"weight": weight + temp})
    return H

"""
Our modified version of the LFR benchmark model, suited to fit the particular properties
of the judicial citation network. The specific procedure and parameters utilized is set out
in Section 2 and 3 of our paper.
"""

from random import choice, seed as randseed

import networkx as nx

AVG_DEGREE = 6.7
DEGREE_ALPHA = 3.565

# 1.7 is the average value of the default nx powerlaw sequence
SCALING_FACTOR = AVG_DEGREE / 1.56

COMM_FRACTIONS = [
    0.029933491,
    0.039929701,
    0.064415727,
    0.066738343,
    0.067251111,
    0.071532444,
    0.078061959,
    0.083100037,
    0.087952031,
    0.097088114,
    0.153322995,
    0.160674041,
]

INTER_COMMUNITY_FRAC = 0.282

# DEG_FIT, COMM_FIT = power_law_fits(load_network())
DEG_ALPHA = 3.565129


def generate_fs_graph(n: int, seed=None) -> nx.DiGraph:
    """
    Algorithm description:
    1. Creates num_comm_nodes = n * COMM_FRACTIONS[i] nodes for each community i
    2. Get num_comm_nodes random values from a power law distribution representing degrees
    3. For a given node and its degree deg, create (1 - INTER_COMMUNITY_FRAC) * deg edges to random nodes within the same community
        and (INTER_COMMUNITY_FRAC) * deg edges to random nodes in other communities

    Lots of optimizations we can make here, just getting it to work for now.
    """
    # Initialize random seed
    if seed is not None:
        randseed(seed)
    G = nx.DiGraph()
    nodes_per_community = [int(n * f) for f in COMM_FRACTIONS]
    # Create power law distribution for degrees
    deg_dist = [v * SCALING_FACTOR for v in nx.utils.powerlaw_sequence(n, exponent=DEGREE_ALPHA, seed=seed)]
    curr_node = 0
    comm_nodes = []
    for community_idx, num_nodes in enumerate(nodes_per_community):
        curr_comm = []
        for _ in range(num_nodes):
            G.add_node(curr_node, community=community_idx, degree=deg_dist[curr_node])
            curr_comm.append(curr_node)
            curr_node += 1
        comm_nodes.append(curr_comm)
    all_nodes = [n for comm in comm_nodes for n in comm]
    # Add edges
    nodes = list(G.nodes(data=True))
    for node, data in nodes:
        deg = data["degree"]
        comm_idx = data["community"]
        # Add (1 - INTER_COMMUNITY_FRAC) * deg edges to nodes in the same community
        for n in range(round(deg * (1 - INTER_COMMUNITY_FRAC))):
            random_node = choice(comm_nodes[comm_idx])
            G.add_edge(node, random_node, weight=1)
        # Add (INTER_COMMUNITY_FRAC) * deg edges to nodes in other communities
        for n in range(round(deg * INTER_COMMUNITY_FRAC)):
            random_node = None
            # Pick a node in a different community
            while random_node is None:
                selection = choice(all_nodes)
                if G.nodes[selection]["community"] != comm_idx:
                    random_node = selection
            G.add_edge(node, random_node, weight=1)
    # Set partition on graph
    G.graph['partition'] = [set(comm) for comm in comm_nodes]
    return G


if __name__ == "__main__":
    generate_fs_graph(1000)

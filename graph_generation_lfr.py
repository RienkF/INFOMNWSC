# Creates LFR benchmark graphs based on the properties of the main graph

# Power law degree exponent = 3.5651290105965305
# Power law community size exponent = 4.1918
# Average degree = 6.783669266744867
# Minimum degree = 1 (don't specify this in the algorithm)
# Maximum degree = 6756
# Minimum community size = 21716
# Maximum community size = 116565
# Inter-community edge fraction = 0.282

import networkx as nx

DEG_ALPHA = 3.565129
COMM_SIZE_ALPHA = 4.1918
AVG_DEG = 6.783669
MIN_COMM_FRAC = 0.065
MAX_COMM_FRAC = 0.16
INTER_COMMUNITY_FRAC = 0.282


def generate_lfr_graph(
    n: int,
    deg_exponent: float = DEG_ALPHA,
    comm_exponent: float = COMM_SIZE_ALPHA,
    avg_deg: float = AVG_DEG,
    min_comm_frac: float = MIN_COMM_FRAC,
    max_comm_frac: float = MAX_COMM_FRAC,
    inter_community_frac: float = INTER_COMMUNITY_FRAC,
    seed=None,
) -> nx.DiGraph:
    # First, scale absolute quantities by n / ORIGINAL_GRAPH_SIZE
    min_comm_size = round(min_comm_frac * n)
    max_comm_size = round(max_comm_frac * n)
    G = nx.generators.LFR_benchmark_graph(
        n,
        tau1=deg_exponent,
        tau2=comm_exponent,
        average_degree=avg_deg,
        min_community=min_comm_size,
        max_community=max_comm_size,
        mu=inter_community_frac,
        seed=seed,
    )
    G = G.to_directed()
    # Add weight=1 to each edge
    for u, v in G.edges():
        G[u][v]["weight"] = 1
    # Partitions are stored in sets on node properties 'community'
    partition_set = set()
    for node, data in G.nodes(data=True):
        partition_set.add(frozenset(data["community"]))
    G.graph["partition"] = list(partition_set)
    return G

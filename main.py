import networkx as nx
import csv
from pathlib import Path

from algorithm.edge_ratio import global_edge_ratio, local_edge_ratio
from algorithm.modularity import global_modularity, local_modularity
from louvain import louvain_communities

EDGE_CSV_PATH = Path("data", "citations.csv")
METADATA_CSV_PATH = Path("data", "case_metadata.csv")
NETWORK_CACHE_PATH = Path("data", "network_cache.pik")


def load_network(
    directed=True,
    metadata_csv: Path = METADATA_CSV_PATH,
    edge_csv: Path = EDGE_CSV_PATH,
) -> nx.Graph:
    # We can get a performance bump on subsequent runs by storing the graph as a pickle
    if NETWORK_CACHE_PATH.exists():
        return nx.read_gpickle(NETWORK_CACHE_PATH)
    base_graph = nx.DiGraph() if directed else nx.Graph()
    g = nx.read_edgelist(
        edge_csv,
        delimiter=",",
        create_using=base_graph,
    )
    with open(metadata_csv, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            # Check if row[0] is a node
            if row[0] in g.nodes:
                g.nodes[row[0]]["court"] = row[1]
    nx.write_gpickle(g, NETWORK_CACHE_PATH)
    return g


def main():
    # G = load_network()
    # Barabasi-Albert graph
    G = nx.barabasi_albert_graph(20, 3)
    # Add edge weight of 1 to each edge
    for u, v, d in G.edges(data=True):
        d["weight"] = 1
    G = nx.to_directed(G)
    print(f"Loaded {len(G.nodes)} nodes and {len(G.edges)} edges")

    # communities = louvain_communities(G, global_edge_ratio, local_edge_ratio)
    communities = louvain_communities(G, global_modularity, local_modularity)
    print(len(communities))


if __name__ == "__main__":
    main()

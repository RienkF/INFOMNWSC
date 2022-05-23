import networkx as nx
import csv
from pathlib import Path

EDGE_CSV_PATH = Path("data", "citations.csv")
METADATA_CSV_PATH = Path("data", "case_metadata.csv")
NETWORK_CACHE_PATH = Path("data", "network_cache.pik")


def load_network(
    metadata_csv: Path = METADATA_CSV_PATH, edge_csv: Path = EDGE_CSV_PATH
) -> nx.DiGraph:
    # We can get a performance bump on subsequent runs by storing the graph as a pickle
    if NETWORK_CACHE_PATH.exists():
        return nx.read_gpickle(NETWORK_CACHE_PATH)
    g = nx.read_edgelist(
        edge_csv,
        delimiter=",",
        create_using=nx.DiGraph(),
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
    G = load_network()


if __name__ == "__main__":
    main()

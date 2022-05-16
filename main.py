import networkx as nx


def main():
    path_to_networks = ".\\data\\networks\\"
    g = nx.read_edgelist(path_to_networks + "facebook_combined.txt", delimiter=' ', create_using=nx.Graph())

    print(nx.info(g))


if __name__ == "__main__":
    main()

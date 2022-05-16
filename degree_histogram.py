from collections import Counter

import matplotlib.pyplot as plt

from main import load_network

G = load_network()
degrees = [deg for _, deg in G.degree()]
degree_freq = Counter(degrees)
x, y = zip(*degree_freq.items())

total_degree = sum(y)
y = [y / total_degree for y in y]

# Plot histogram
plt.figure(1)

plt.xlabel("$k$")
plt.xscale("log")
plt.ylabel("$p_k$")
plt.yscale("log")
plt.title("Degree Distribution")

plt.scatter(x, y, marker=".")

plt.show()

# INFOMNWSC: Community Measure Analysis

## Reproducing Results

1. This codebase was developed on Python 3.9.1. For best results, use that version of Python or later.
2. To install the necessary packages, run `pip install -r requirements.txt`.
3. To reproduce the main results of the paper, run `python assess.py`. In addition to logging many intermediate results to stdout, this will save results of the experiment to two files: `data/benchmark_results.csv` (which contains aggregated statistics such as NMI mean and variance for each measure) and `data/benchmark_results_full.csv` (which contains the results broken down by each synthetic graph seed).

## Navigating the Codebase

The core functionality, should you wish to inspect it, is spread across several files:

- The code that implements our LFR benchmark-inspired synthetic graphs is in `graph_generation_fs.py`.
- The code that runs the optimization algorithm on each combination of synthetic graph and measure is in `assess.py`.
- Our implementation of the Louvain algorithm is in `algorithm/louvain.py`.
- Our implementations of the community measures are found in `algorithm/edge_ratio.py`, `algorithm/modularity.py`, and `algorithm/modularity_density.py`.

Other files contain functionality of various utility, but are not necessary to reproduce the results of the paper.

Godspeed!

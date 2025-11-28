import os
import re
import csv
import argparse
from datetime import datetime
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Phase 4: Graph Construction")
parser.add_argument("-i", "--input", required=True, help="Input CSV file with resolved entities")
parser.add_argument("--image", default="graph.png", help="Filename to save graph visualization")
parser.add_argument("--output_gml", default="graph.gml", help="Output GML file for the graph")
args = parser.parse_args()

INPUT_FILE = args.input
IMAGE_FILE = args.image
OUTPUT_GML = args.output_gml

# --- LOAD DATA ---
df = pd.read_csv(INPUT_FILE)

# --- BUILD GRAPH ---
G = nx.DiGraph()

for _, row in df.iterrows():
    src = row['sender']
    dst = row['receiver']
    timestamp = row['timestamp']
    msg = row['message']
    label = f"{timestamp}: {msg}"[:100]  # short label

    if not G.has_node(src):
        G.add_node(src)
    if not G.has_node(dst):
        G.add_node(dst)

    if G.has_edge(src, dst):
        G[src][dst]['messages'].append(label)
        G[src][dst]['weight'] += 1
    else:
        G.add_edge(src, dst, messages=[label], weight=1)

# --- SAVE GRAPH ---
nx.write_gml(G, OUTPUT_GML)
print(f"Graph written to {OUTPUT_GML} with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

# --- DRAW GRAPH ---
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=0.5)
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700)
nx.draw_networkx_labels(G, pos, font_size=10)
nx.draw_networkx_edges(G, pos, arrows=True)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): G[u][v]['weight'] for u, v in G.edges()}, font_size=8)
plt.axis('off')
plt.tight_layout()
plt.savefig(IMAGE_FILE)
print(f"Graph visualization saved as {IMAGE_FILE}.")

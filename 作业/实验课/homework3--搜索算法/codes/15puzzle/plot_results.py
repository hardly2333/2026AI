import os
import csv
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
results_path = os.path.join(HERE, "results.txt")

ids = []
steps = []
nodes = []
times = []

with open(results_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ids.append(int(row['id']))
        steps.append(int(row['steps']))
        nodes.append(int(row['expanded_nodes']))
        times.append(float(row['time_seconds']))

fig, axes = plt.subplots(3, 1, figsize=(7, 9))

axes[0].plot(ids, steps, marker='o')
axes[0].set_title('Steps')
axes[0].set_xlabel('Example ID')
axes[0].set_ylabel('Steps')

axes[1].plot(ids, nodes, marker='o')
axes[1].set_title('Expanded Nodes')
axes[1].set_xlabel('Example ID')
axes[1].set_ylabel('Nodes (log scale)')
axes[1].set_yscale('log')

axes[2].plot(ids, times, marker='o')
axes[2].set_title('Time (seconds)')
axes[2].set_xlabel('Example ID')
axes[2].set_ylabel('Seconds')

plt.tight_layout()
out_png = os.path.join(HERE, 'results.png')
plt.savefig(out_png)
print(f"Saved plot to: {out_png}")

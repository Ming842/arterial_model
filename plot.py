"""
This script loads the most recent simulation output from the 'Output' directory and plots the results.
It extracts data based on the debugger settings specified in 'settings.json'.

db is a dictionary structured as:
{
    't': [time_array],

    'SS<segment_index>': {
        '<port_name>': [data_array],
        ...
    },
    ...
}
"""
import os
import pickle
import re

from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from filer import loader, load_latest_simulation_output, build_debug_db

def plot_all_segments(db, fi_substring, ss_keys=False, figsize=(10, 6), cmap_name='tab20'):
    t = np.asarray(db.get('t', []))
    # find SS keys and sort by numeric index if present
    if not ss_keys:
        ss_keys = [k for k in db.keys() if re.match(r'^SS\d+$', k)]
    

    def _idx(k):
        m = re.match(r'^SS(\d+)$', k)
        return int(m.group(1)) if m else float('inf')
    ss_keys.sort(key=_idx)

    fig, ax = plt.subplots(figsize=figsize)
    cmap = plt.get_cmap(cmap_name)

    any_plotted = False
    for i, ss in enumerate(ss_keys):
        seg = db.get(ss, {})
        fi_keys = [k for k in seg.keys() if k.lower() == fi_substring.lower()]
        if not fi_keys:
            continue

        for j, key in enumerate(fi_keys):
            y = np.asarray(seg[key])
            label = f"{ss}:{key}"
            color = cmap((i * len(fi_keys) + j) % cmap.N)
            # align lengths of t and y if necessary
            if t.size and y.size and t.size != y.size:
                n = min(t.size, y.size)
                ax.plot(t[:n], y[:n], label=label, color=color)
            else:
                ax.plot(t, y, label=label, color=color)
            any_plotted = True

    ax.set_xlabel('time')
    ax.set_ylabel(f'{fi_substring}')
    ax.set_title(f'{fi_substring} for all SS segments')
    if any_plotted:
        ax.legend(loc='best', fontsize='small')
    else:
        ax.text(0.5, 0.5, 'No matching Fi data found', ha='center', va='center', transform=ax.transAxes)
    ax.grid(True)

    return fig, ax

#load settings file
settings, _ = loader()

# Load the most recent simulation output
data, last_file = load_latest_simulation_output(pattern='simulation_output_*.pkl')
print(f'Loaded data from {last_file}')

# Build and save the debugger DB using the loaded data/settings
with open(r'Output/db_simulation_output_006.pkl', 'rb') as fh:
    db1 = pickle.load(fh)

# with open(r'Output/db_simulation_output_010.pkl', 'rb') as fh:
#     db2 = pickle.load(fh)

# # debugger_port_list = ["Pi", "Fo", "-Rs*Fi", "-Fi", "-Po", "int_fi", "int_po"]
# debugger_port_list = ["Pi", "Fo", "-Rs*Fi", "-Fi", "-Po", "int_fi", "int_po"]
# ss_keys = ['SS1', 'SS13']
# for port in debugger_port_list:
#     fig, ax = plot_all_segments(db1, port, ss_keys=ss_keys)
#     ax.set_title(f"{port} for all SS segments")

with open(r'Output/db_simulation_output_014.pkl', 'rb') as fh:
    db1 = pickle.load(fh)
debugger_port_list = ["Pi","int_fi"]
ss_keys = ['SS1', 'SS5', 'SS9','SS13']
for port in debugger_port_list:
    fig, ax = plot_all_segments(db1, port, ss_keys=ss_keys)
    ax.set_title(f"{port} for all SS segments")

with open(r'Output/db_simulation_output_015.pkl', 'rb') as fh:
    db2 = pickle.load(fh)
debugger_port_list = ["Pi","int_fi"]
ss_keys = ['SS1', 'SS5', 'SS9','SS13']
for port in debugger_port_list:
    fig1, ax1 = plot_all_segments(db2, port, ss_keys=ss_keys)
    ax1.set_title(f"{port} for all SS segments")

with open(r'Output/db_simulation_output_016.pkl', 'rb') as fh:
    db3 = pickle.load(fh)
debugger_port_list = ["Pi","int_fi"]
ss_keys = ['SS1', 'SS5', 'SS9','SS13']
for port in debugger_port_list:
    fig2, ax2 = plot_all_segments(db3, port, ss_keys=ss_keys)
    ax2.set_title(f"{port} for all SS segments")
plt.show()

"""
This script loads the most recent simulation output from the 'Output' directory and plots the results.
"""

import glob
import pickle
import re

import numpy as np
import matplotlib.pyplot as plt

from filer import loader

# Load the most recent simulation output
files = glob.glob('Output/simulation_output_*.pkl')
if not files:
    raise FileNotFoundError("No simulation_output_XXX.pkl files found in Output directory.")

last_file = max(files, key=lambda f: int(re.search(r'(\d+)', f).group(1)))

with open(last_file, 'rb') as f:
    data = pickle.load(f)

print(f'Loaded data from {last_file}')

settings, _ = loader()

index = settings['debugger']['debug_for_index']
port_list = settings['debugger']['debugger_port_list']

db = {}  # dictionary to hold data for plotting

# Extract numbers after 'out_' and up to the '[' for each yname
out_numbers = []
pattern = re.compile(r'out_(\d+)\[')
for yname in data.ynames:
    match = pattern.search(yname)
    if match:
        out_numbers.append(int(match.group(1)))
    else:
        out_numbers.append(None)

for i, yname in enumerate(out_numbers):
    attr = f'y{i}'

    if hasattr(data, attr):
        try: 
            db[f'SS{yname}'][f'{port_list[i % len(port_list)]}'] = getattr(data, attr)
        except:
            db[f'SS{yname}'] = {}
            db[f'SS{yname}'][f'{port_list[i % len(port_list)]}'] = getattr(data, attr)

print(db)



# # Optionally set time window (uncomment and set t_min, t_max as needed)
# t_min = 5      # minimum time (inclusive)
# t_max = 6     # maximum time (exclusive)
# mask = (data.t > t_min) & (data.t < t_max)

if 't_min' in locals() and 't_max' in locals():
    mask = (data.t > t_min) & (data.t < t_max)
    t_plot = data.t[mask]
else:
    mask = slice(None)
    t_plot = data.t

for ss_key, port_data in db.items():
    num_ports = len(port_data)
    fig, axes = plt.subplots(num_ports, 1, figsize=(10, 4 * num_ports), sharex=True)
    if num_ports == 1:
        axes = [axes]
    for ax, (port, values) in zip(axes, port_data.items()):
        ax.plot(t_plot, np.array(values)[mask], label=port)
        ax.set_title(f'{ss_key} - {port}')
        ax.set_ylabel('Value')
        ax.legend()
    axes[-1].set_xlabel('Time (s)')
    fig.tight_layout()


plt.show()

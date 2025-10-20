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

import glob
import pickle
import re
import os

import numpy as np
import matplotlib.pyplot as plt

from filer import loader, load_latest_simulation_output, build_debug_db

#load settings file
settings, _ = loader()

db, lastfile = load_latest_simulation_output(pattern='db_simulation_output_*.pkl')

debugger_port_list = ["Pi"]

for port in debugger_port_list:
    fig, ax = plot_all_segments(db, port)
    ax.set_title(f"{port} for all SS segments")

plt.show()


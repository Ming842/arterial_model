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

# Load the most recent simulation output
data, last_file = load_latest_simulation_output(pattern='simulation_output_*.pkl')
print(f'Loaded data from {last_file}')

# Build and save the debugger DB using the loaded data/settings
db, out_path = build_debug_db(data, settings, last_file, save=False)


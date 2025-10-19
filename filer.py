"""
This module loads settings and model parameters from JSON files.
"""
import json
import os
import pickle
import re
import glob

def loader():
    """
    Load settings and model parameters from JSON files.
    Returns:
        settings (dict): Settings loaded from settings.json.
        model_params (dict): Model parameters loaded from model_params.json.
    """
    # Load settings from JSON file
    with open(r'Data\settings.json', encoding='utf-8') as file:
        settings = json.load(file)

    # Load model parameters from JSON file
    with open(r'Data\model_params.json', encoding='utf-8') as file:
        model_params = json.load(file)
    return settings, model_params

def saver(out):
    """
    Save simulation output to a pickle file with an incremented filename.
    The filename format is 'simulation_output_XXX.pkl', where XXX is a zero-padded integer.
    """
    i = 1
    while os.path.exists(f'Output\simulation_output_{i:03d}.pkl'):
        i += 1

    with open(f'Output\simulation_output_{i:03d}.pkl', 'wb') as f:
        pickle.dump(out, f)

    print(f"Simulation complete and output saved to 'simulation_output_{i:03d}.pkl'.")

def load_latest_simulation_output(output_dir='Output', pattern=str):
    """
    Load the most recent simulation output pickle from output_dir matching pattern.
    Returns (data, last_file).
    Chooses by the largest numeric index in the filename if present, otherwise by file mtime.
    """
    files = glob.glob(os.path.join(output_dir, pattern))
    if not files:
        raise FileNotFoundError(f"No files matching {pattern!r} found in {output_dir!r}.")

    def index_from_name(f):
        m = re.search(r'(\d+)', os.path.basename(f))
        return int(m.group(1)) if m else None

    if any(index_from_name(f) is not None for f in files):
        last_file = max(files, key=lambda f: index_from_name(f) or -1)
    else:
        last_file = max(files, key=os.path.getmtime)

    with open(last_file, 'rb') as fh:
        data = pickle.load(fh)

    return data, last_file

def build_debug_db(data, settings, last_file, output_dir='Output', save=False):
    """
    Build a debugger DB from simulation `data` and `settings`.
    Returns (db, out_path).
    Saves the DB to a pickle file in output_dir if save is True.
    """

    os.makedirs(output_dir, exist_ok=True)
    
    port_list = settings['debugger'].get('debugger_port_list', [])

    db = {'t': data.t}

    pattern = re.compile(r'out_(\d+)\[')
    for i, yname in enumerate(data.ynames):
        match = pattern.search(yname)
        out_num = int(match.group(1)) if match else None

        attr = f'y{i}'
        if not hasattr(data, attr):
            continue

        # choose a stable SS key (use parsed out number if available, otherwise use index)
        ss_key = f'SS{out_num}' if out_num is not None else f'SS{i}'
        # pick port from port_list circularly if available, otherwise fall back to a generated name
        port = port_list[i % len(port_list)] if port_list else f'port{i}'

        db.setdefault(ss_key, {})[port] = getattr(data, attr)

    # Save the debugger DB if requested
    if save:
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(last_file))[0]
        out_path = os.path.join(output_dir, f'db_{base}.pkl')
        with open(out_path, 'wb') as f:
            pickle.dump(db, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f'Saved debugger DB to {out_path}')
    return db
"""
This module loads settings and model parameters from JSON files.
"""
import json
import os
import pickle

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
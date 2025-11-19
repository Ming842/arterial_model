"""
Main script to set up and run the arterial network model simulation.

Connects arterial elements based on configuration from a JSON file.
"""

import bdsim
import re
from arterial_element import arterial_elements_from_params, to_subsystem, connect_segments
from filer import loader, saver, load_latest_simulation_output, build_debug_db
import numpy as np



def main():
    settings, model_params = loader()
    # Initialize simulation and arterial elements dictionary
    sim = bdsim.BDSim()

    settings['debugger']['debug_for_index'] = [1,3,5,7,9,11,13]
    settings['input_signal']['frequency'] = 0.5  # Change frequency to 0.5 Hz
    init_and_run(settings, model_params, sim)
    data1, last_file1 = load_latest_simulation_output(pattern='simulation_output_*.pkl')
    db1 = build_debug_db(data1, settings, last_file1, save=True)

    # settings['input_signal']['frequency'] = 0.4  # Change frequency to 0.5 Hz
    # init_and_run(settings, model_params, sim)
    # data2, last_file2 = load_latest_simulation_output(pattern='simulation_output_*.pkl')
    # db2 = build_debug_db(data2, settings, last_file2, save=True)
    
    # settings['input_signal']['frequency'] = 0.20  # Change frequency to 0.5 Hz
    # init_and_run(settings, model_params, sim)
    # data3, last_file3 = load_latest_simulation_output(pattern='simulation_output_*.pkl')
    # db3 = build_debug_db(data3, settings, last_file3, save=True)
    

def init_and_run(settings, model_params, sim):
    """
    Initialize and run the arterial network simulation.
    Args:
        settings (dict): Simulation settings.
        model_params (dict): Model parameters.
        sim (bdsim.BDSim): BDSim simulation instance.
    """
    arterial_elements = arterial_elements_from_params(sim, model_params, settings)

    ## Initialize main model and add subsystems to dictionary
    
    model = sim.blockdiagram(name='Arterial Network Model')

    # Convert all arterial elements to subsystems under main model and store in 'SS' dictionary
    arterial_elements = to_subsystem(model, arterial_elements)

    # Connect segments based on model_params connections
    connect_segments(model, arterial_elements, model_params, settings)

    if settings['simulation']['report']:
        model.report()    # list all blocks and wires

    model.compile()

    out = sim.run(model, dt = settings['simulation']['time_step'],
                  T = settings['simulation']['simulation_time'],
                  block = settings['simulation']['block'])  # simulate for 30s
    
    # Save the output if specified in settings
    if settings['output']['save_results']: # only save if specified in settings
        print(out)
        saver(out, settings)
    else :
        print("Output saving is disabled in settings.")

if __name__ == "__main__":
    main()

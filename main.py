"""
Main script to set up and run the arterial network model simulation.

Connects arterial elements based on configuration from a JSON file.
"""

import bdsim

from arterial_element import arterial_elements_from_params, to_subsystem, connect_segments
from filer import loader, saver



def main():
    settings, model_params = loader()
    # Initialize simulation and arterial elements dictionary
    sim = bdsim.BDSim()
    
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
        saver(out)
    else :
        print("Output saving is disabled in settings.")

if __name__ == "__main__":
    main()

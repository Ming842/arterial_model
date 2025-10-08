"""
Main script to set up and run the arterial network model simulation.

Connects arterial elements based on configuration from a JSON file.
"""

import bdsim
import json
import pickle

from arterial_element import ArterialElement


# Load model parameters from JSON file
with open(r'.venv\Data\model_params.json', encoding='utf-8') as file:
    model_params = json.load(file)

# Extract parameters for each segment
for segment in model_params['rows']:
    name, index, rs, l, c, rp, type, connections, debug = segment
    print(f"Segment: {name}, Rs: {rs}, L: {l}, C: {c}, Rp: {rp}, Viscoelastic Model: {type}, Connections: {connections}")

# Initialize simulation and arterial elements dictionary
sim = bdsim.BDSim()
arterial_elements = {}
arterial_elements['BD'] = {}

# Create arterial elements based on parameters from json file
for art_seg in model_params['rows']:
    name, index, rs, l, c, rp, _ , _ , debug = art_seg
    rs *= 1e-3  # Convert Rs from dyn·s/cm^5 to mmHg·s/ml
    l  *= 1e-3  # Convert L from dyn·s^2
    c  *= 1e-3   # Convert C from ml/dyn to ml/mmHg

    if rp is None:
        cls_art = ArterialElement(sim, rs, l, c, index, debug)
        arterial_elements['BD'][index] = cls_art.arterial_element
        print(f"Created arterial element for segment {name} with index {index}")
    else:
        cls_art = ArterialElement(sim, rs, l, c, index, debug, rp)
        arterial_elements['BD'][index] = cls_art.arterial_element
        print(f"Created arterial element for segment {name} with index {index} and peripheral resistance Rp={rp}")

print("All arterial elements created.")

## Initialize main model and add subsystems to dictionary
arterial_elements['SS'] = {}
model = sim.blockdiagram(name='Arterial Network Model')

# Convert all arterial elements to subsystems and store in 'SS' dictionary
for arterial_element in arterial_elements['BD'].values():
    arterial_elements['SS'][str(arterial_element.name)] = model.SUBSYSTEM(arterial_element)

fo_plug = model.CONSTANT(0)  # Outflow plugged

# Flow generator (sine wave for now)
generator = model.WAVEFORM(wave = 'sine', freq=0.5)
wave = model.FUNCTION(lambda u1: ((u1**(1/2))*40 + 80), name='Waveform')

# Connections of the 1st segment
model.connect(generator, wave)
model.connect(wave, arterial_elements['SS']['1'][0])



for art_seg in model_params['rows']:
    _ , index, _, _, _, _, _, connections, debug = art_seg
    if index == 1:
        pass
    match connections:
        case []: # No connections
            print(f"Segment {index} has no connections.")
            model.connect(fo_plug, arterial_elements['SS'][str(index)][1])  # Plugging Fo
        case [a, *rest]:
            if not rest:  # Only one connection
                model.connect(arterial_elements['SS'][str(index)][0], arterial_elements['SS'][str(a)][0])
                model.connect(arterial_elements['SS'][str(a)][1], arterial_elements['SS'][str(index)][1])
            else: # Multiple connections
                print(f"Segment {index} has multiple connections {connections}, now connecting {[a, *rest]}.")
                n = len([a, *rest])
                sumb = model.SUM('+' * n, name=f"Sum: {connections} to {index}")   # Create a appropriately sized sum block to combine outputs
                for i, conn in enumerate([a, *rest]):
                    model.connect(arterial_elements['SS'][str(index)][0], arterial_elements['SS'][str(conn)][0]) # Connect Pi to connected segment
                    model.connect(arterial_elements['SS'][str(conn)][1], sumb[i]) # Connect Fi of connected segment to sum block
                    print(f"Connected segment {index} to {conn} with sum block of {n} inputs.")
                model.connect(sumb, arterial_elements['SS'][str(index)][1])  # Connect Fi of connected segment to sum block
                print(f"All connections for segment {index} have been made.")
        case _: # Error handeling for any other format
            raise ValueError(f"Unexpected connections format for segment {index}: {connections}")


## alterative flow input options
# step = model.STEP(2, off=-1, on=1)
# step = model.PIECEWISE((0,0), (1, 1), (1.2,0), (3,1), (3.2, 0), (3000,0))

# scope_1 = model.SCOPE(name = 'Scope RS')

# scope_2 = model.SCOPE(name = 'Scope 2')
# scope_3 = model.SCOPE(name = 'Scope 3')
# # scope_4 = model.SCOPE(name = 'Scope 4')
# model.connect(arterial_elements['SS']['1']['k_rs'], scope_1)
  # Pi of 1st segment
model.report()    # list all blocks and wires

model.compile()

out = sim.run(model, dt = 0.02, T = 10, watch=[wave], block = False)  # simulate for 30s
print(out)
with open(r'.venv\Data\simulation_output.pkl', 'wb') as f:
    pickle.dump(out, f)

print("Simulation complete and output saved to 'simulation_output.pkl'.")

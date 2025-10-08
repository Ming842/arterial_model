# Arterial Network Model

A cardiovascular simulation model for arterial blood flow dynamics based on the Wesseling model (1983). This project was developed for Technical Medicine Year 2 Stage 1 at OLVG IC.

## Overview

This model simulates blood flow through a network of arterial segments, each modeled as lumped parameter elements with resistance, inductance, and compliance. The simulation uses block diagram simulation (BDSim) to create a connected network of arterial elements representing the human arterial system.

## Features

- **Modular arterial elements**: Each segment is modeled with physiological parameters (resistance, inductance, compliance)
- **Configurable network topology**: Connections between segments defined via JSON configuration
- **Peripheral resistance modeling**: Optional peripheral resistance for terminal segments
- **Customizable input signals**: Sine wave pressure/flow input with adjustable frequency, amplitude, and baseline
- **Simulation output**: Results saved as pickle files for further analysis
- **Visualization tools**: Built-in plotting capabilities for analyzing simulation results

## Model Physics

Each arterial element implements the Wesseling model equations:

```
dFi/dt = 1/L * (Pi - Po - Rs*Fi)
dPo/dt = 1/C * (Fi - Fo - Po/Rp)
```

Where:
- `Fi`, `Fo`: Input and output flow
- `Pi`, `Po`: Input and output pressure  
- `Rs`: Series resistance
- `L`: Inductance
- `C`: Compliance
- `Rp`: Peripheral resistance (optional)

## Project Structure

```
arterial_model/
├── main.py              # Main simulation script
├── arterial_element.py  # Arterial element class and connection logic
├── filer.py            # JSON file loader and output saver
├── plot.py             # Visualization and analysis tools
├── debugger.py         # Debugging utilities (currently empty)
├── Data/
│   ├── settings.json    # Simulation parameters and configuration
│   └── model_params.json # Arterial network topology and parameters
└── Output/             # Simulation results (*.pkl files)
```

## Installation

### Prerequisites

- Python 3.x
- Required packages:
  - `bdsim` - Block diagram simulation library
  - `numpy` - Numerical computing
  - `matplotlib` - Plotting and visualization
  - `pickle` - Data serialization (built-in)

### Setup

1. Clone this repository
2. Install required dependencies:
   ```bash
   pip install bdsim numpy matplotlib
   ```

## Usage

### Running a Simulation

1. Configure simulation parameters in `Data/settings.json`
2. Adjust arterial network parameters in `Data/model_params.json` if needed
3. Run the simulation:
   ```bash
   python main.py
   ```

### Configuration Files

#### `Data/settings.json`
```json
{
    "simulation": {
        "simulation_time": 2,        # Total simulation time (seconds)
        "time_step": 0.001,          # Integration time step (seconds)
        "block": false,              # Block execution until completion
        "report": false              # Generate detailed block diagram report
    },
    "input_signal": {
        "frequency": 1,              # Input signal frequency (Hz)
        "amplitude": 40,             # Signal amplitude
        "baseline": 80               # Baseline pressure/flow value
    },
    "output": {
        "save_results": false        # Save simulation results to pickle file
    }
}
```

#### `Data/model_params.json`
Defines the arterial network with columns:
- **Segment name**: Anatomical name
- **Index**: Unique segment identifier
- **rs**: Series resistance (dyn·s/cm⁵)
- **l**: Inductance (dyn·s²/cm⁵)
- **c**: Compliance (ml/dyn)
- **rp**: Peripheral resistance (optional, dyn·s/cm⁵)
- **Visco elast model**: Model type identifier
- **Connections**: List of connected downstream segments

### Analysing results

## Model Parameters

The default model includes 28 arterial segments representing major arteries:

- **Central arteries**: Ascending aorta, aortic arch, thoracic and abdominal aorta
- **Peripheral arteries**: Carotid, brachial, femoral, and iliac arteries
- **Terminal segments**: With peripheral resistance modeling end-organ circulation

### Parameter Units

- Resistance: dyn·s/cm⁵ → converted to mmHg·s/ml
- Inductance: dyn·s²/cm⁵ → converted to mmHg·s²/ml  
- Compliance: ml/dyn → converted to ml/mmHg
- Pressure: mmHg
- Flow: ml/s

## Development

### Adding New Segments

1. Add segment parameters to `model_params.json`
2. Define connections to existing segments
3. Assign unique index number
4. Run simulation to validate connectivity

### Debugging

Enable debug mode in `settings.json` and specify segments to monitor:

```json
{
    "debug_mode": true,
    "debug_for_index": [1, 2, 3]
}
```

This adds SCOPE blocks to visualize internal signals for specified segments.

## Contributing

This project is part of an academic study. For questions or contributions, please contact the development team.

## License

This project is developed for educational purposes as part of the Technical Medicine program.

## References

- Wesseling, K.H. (1983). A computer model of the systemic circulation. *Medical & Biological Engineering & Computing*
- BDSim Documentation: Block diagram simulation library for Python

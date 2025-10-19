"""
Arterial element block for cardiovascular simulations
- Either with or without peripheral resistance
- Based on the Wesseling model (1983)

Inputs:  Pi, Fo
Outputs: Po, Fi
"""

import bdsim
class ArterialElement():
    """
    Simple arterial element model
    """
    def __init__(self, sim: bdsim.BDSim, rs, l, c, index, settings, rp=None):
        """
        Initialize the arterial element block
        """
        self.settings = settings

        self.debug_port_list = self.settings['debugger']['debugger_port_list'] if self.settings['debugger']['enabled'] else []
        self.sim = sim
        self.arterial_element = bdsim.BlockDiagram()
        self.rs = rs
        self.l = l
        self.c = c
        self.index = index
        self.rp = rp
        self.int_fi = settings['initial_conditions']['int_fi']
        self.int_po = settings['initial_conditions']['int_po']
        self.make_art_element()

    def make_art_element(self):
        """
        Simple arterial element model
        dFi/dt = 1/L * (Pi - Po)
        dPo/dt = 1/C * (Fi - Fo - Po/Rp)
        """

        # Initialize block diagram for arterial element to build upon
        self.arterial_element  = self.sim.blockdiagram(name=str(self.index))

        # Logic for extra output ports if debugger is enabled in settings for this index
        debugger_enabled = self.settings['debugger']['enabled']
        debug_this_index = self.index in self.settings['debugger']['debug_for_index']
        output_names = ['-Po', 'Fi'] if self.index != 1 else ['-Po']  # Naming inputs, just Po for first segment

        if debugger_enabled and debug_this_index:
            print(f"Debugging enabled for arterial element {self.index}, adding extra ports to output.")
            debugger_ports = len(self.debug_port_list)
            output_names += self.debug_port_list
        else:
            debugger_ports = 0

        output_ports = 2 if self.index != 1 else 1  # Fi is clipped for the 1st segment to mimic aortic valve behavior

        # Ports: inputs [Pi, Fo], outputs [Po, Fi]
        inp  = self.arterial_element.INPORT(2, name=f'in_{self.index}')   # inp[0]=Pi, inp[1]=Fo
        outp = self.arterial_element.OUTPORT(output_ports+debugger_ports, name=f'out_{self.index}', onames= output_names)  # outp[0]=Po , outp[1]=Fi, outp[2...]=debugger ports

        # Gains
        k_invl = self.arterial_element.GAIN(-1.0 / self.l, name= "k_invl")     # -1/L
        k_invc = self.arterial_element.GAIN(-1.0 / self.c, name= "k_invc")     # -1/C
        k_rs   = self.arterial_element.GAIN(self.rs, name= "k_rs")          # Rs

        if self.rp is not None: # peripheral resistance block only if rp is provided
            k_1rp  = self.arterial_element.GAIN(1.0 / self.rp, name= "k_1rp")    # 1/Rp

        # Integrators
        int_fi = self.arterial_element.INTEGRATOR(x0=self.int_fi,  name='Fi')   #∫ (Pi - Po - Rs*Fi) dt
        int_po = self.arterial_element.INTEGRATOR(x0=self.int_po, name='Po')    #∫ (Fi - Fo - Po/Rp) dt

        # Sums
        sum_f = self.arterial_element.SUM('+++', name='F')   # Pi + (- Po) + (- Rs*Fi)

        if self.rp is not None: # room for peripheral resistance added to sum only if rp is provided
            sum_p = self.arterial_element.SUM('--+', name='P')   # Fi + (- Fo) + (- Po/Rp)
        else:
            sum_p = self.arterial_element.SUM('--', name='P')   # - Fi - (- Fo) + (- Po/Rp)

        # Connections
        if self.rp is not None: # -Po/Rp only if rp is provided
            self.arterial_element.connect(k_invc, k_1rp)    # - Po/Rp
            self.arterial_element.connect(k_1rp, sum_p[2])  # -Po -> -Po/Rp

        self.arterial_element.connect(inp[0],  sum_f[0])   # inp Pi -> sum_f[0]
        self.arterial_element.connect(k_invc,  sum_f[1])   # - Po
        self.arterial_element.connect(k_rs,    sum_f[2])   # - Rs*Fi

        self.arterial_element.connect(sum_f, int_fi)       # Pi + (- Po) + (- Rs*Fi) -> ∫()

        self.arterial_element.connect(int_fi, k_invl)      # ∫(Pi + (- Po) + (- Rs*Fi)) -> 1/L * ∫(Pi + (- Po) + (- Rs*Fi))

        if self.index == 1: # clipping Fi output for 1st segment to mimic aortic valve behavior
            clip = self.arterial_element.CLIP(min= float('-inf'), max=0, name=f'Clip -Rs*Fi {self.index}')
            self.arterial_element.connect(k_invl, clip)
            self.arterial_element.connect(clip, sum_p[0], k_rs)  # -Fi -> -Rs*Fi & sum_p[0] for next calculations
        else: # normal behavior for all other segments
            self.arterial_element.connect(k_invl, k_rs, outp[1])
            self.arterial_element.connect(k_invl, sum_p[0])    # Fi
        
        self.arterial_element.connect(inp[1],  sum_p[1])    # - Fo

        self.arterial_element.connect(sum_p, int_po)       # Fi + (- Fo) + (- Po/Rp) -> ∫()
        self.arterial_element.connect(int_po, k_invc)  # ∫(Fi + (- Fo) + (- Po/Rp)) -> -1/C * ∫(Fi + (- Fo) + (- Po/Rp)) = -Po

        # bd.connect(k_invC, k_1rp, outp[0])  # -Po -> -Po/Rp
        self.arterial_element.connect(k_invc, outp[0])  # -Po -> -Po/Rp

        if debugger_enabled and debug_this_index:
            # Connect extra debugger ports based on settings['debugger']['debug_port_list']
            self.debug_port_map = {
            'Pi': inp[0],
            'Fo': inp[1],
            '-Rs*Fi': k_rs,
            '-Fi': k_invl,
            '-Po': k_invc,
            'int_fi': int_fi,
            'int_po': int_po
            }
            if self.index == 1:
                self.debug_port_map['-Fi'] = clip
            for i, port_name in enumerate(self.debug_port_list):
                if port_name in self.debug_port_map:
                    self.arterial_element.connect(self.debug_port_map[port_name], outp[output_ports + i])

                else: # Handle unknown port names
                    raise ValueError(f"Unknown debug port name: {port_name}, available options: {list(self.debug_port_map.keys())}")

def arterial_elements_from_params(sim: bdsim.BDSim, model_params, settings):
    """
    Create arterial elements in dict from model parameters.
    Args:
        sim (bdsim.BDSim): BDSim simulation instance.
        model_params (dict): Model parameters loaded from JSON file.
    """

    arterial_elements = {}
    arterial_elements['BD'] = {}

    # Create arterial elements based on model parameters
    for art_seg in model_params['rows']:
        name, index, rs, l, c, rp, _ , _ = art_seg
        rs *= 1e-3  # Convert Rs from dyn·s/cm^5 to mmHg·s/ml
        l  *= 1e-3  # Convert L from dyn·s^2
        c  *= 1e-3   # Convert C from ml/dyn to ml/mmHg

        if rp is None:
            cls_art = ArterialElement(sim, rs, l, c, index, settings)
            arterial_elements['BD'][index] = cls_art.arterial_element
            print(f"Created arterial element for segment {name} with index {index}")
        else:
            cls_art = ArterialElement(sim, rs, l, c, index, settings, rp)
            arterial_elements['BD'][index] = cls_art.arterial_element
            print(f"Created arterial element for segment {name} "
                  f"with index {index} and peripheral resistance Rp={rp}")
    print("All arterial elements created.")
    return arterial_elements

def to_subsystem(model: bdsim.BlockDiagram, arterial_elements):
    """
    Convert all arterial elements to subsystems and store in 'SS' dictionary
    Args:
        model (bdsim.BlockDiagram): Main block diagram to add subsystems to.
        arterial_elements (dict): Dictionary containing arterial elements.
    """
    arterial_elements['SS'] = {}
    for arterial_element in arterial_elements['BD'].values():
        arterial_elements['SS'][str(arterial_element.name)] = model.SUBSYSTEM(arterial_element)

    print("All arterial elements converted to subsystems.")
    return arterial_elements

def connect_segments(model, arterial_elements, model_params, settings):
    """
    Connect arterial segments based on model parameters.
    Args:
        model (bdsim.BlockDiagram): Main block diagram to add subsystems to.
        arterial_elements (dict): Dictionary containing arterial elements.
        model_params (dict): Model parameters loaded from JSON file.
        settings (dict): Settings loaded from JSON file.
    """

    # Create a flow plug for the outer ends of the model.
    fo_plug = model.CONSTANT(0)  # Outflow plug

    # Flow generator (ROOTSINE for now)
    generator = model.WAVEFORM(wave = 'sine', freq=settings['input_signal']['frequency'])
    wave = model.FUNCTION(lambda u1: ((u1**(1/2))*settings['input_signal']['amplitude'] + settings['input_signal']['baseline']), name='Waveform')

    # Seperately handle connections of the 1st segment
    model.connect(generator, wave)
    model.connect(wave, arterial_elements['SS']['1'][0])

    # Segments have 2 inputs: [0] = Pi, [1] = Fo
    # Segments have 2 outputs: [0] = -Po, [1] = -Fi

    # Code below connects all in- and outputs of segments based on the connections specified in model_params.json
    # In the case of multiple connections, a SUM block is used to combine the flows.
    for art_seg in model_params['rows']:
        _ , index, _, _, _, _, _, connections = art_seg
        debug_for_index = index in settings['debugger']['debug_for_index']
        debugger_enabled = settings['debugger']['enabled']

        if debugger_enabled and debug_for_index:
            print(f"Debugging enabled for segment {index}, connecting ports to dataports.")
            output_ports = 2 if index != 1 else 1  # Fi is clipped for the 1st segment to mimic aortic valve behavior

            debugger_ports = len(settings['debugger']['debugger_port_list']) if debugger_enabled else 0

            for i, port_name in enumerate(settings['debugger']['debugger_port_list']):
                watch = model.WATCH(name=f"watch_seg{index}_{port_name}", inames=[f"watch_seg{index}_{port_name}"])
                model.connect(arterial_elements['SS'][str(index)][output_ports + i], watch)

        if index == 1: # Skip the first segment as it's already connected
            pass

        match connections:
            case []: ## NO CONNECTIONS ---------------------------------------------------------------------------
                print(f"Segment {index} has no connections.")
                # Plugging Fo with outflow plug
                model.connect(fo_plug, arterial_elements['SS'][str(index)][1])

            case [a, *rest]:
                if not rest: ## ONE CONNECTION -------------------------------------------------------------------
                    print(f"Segment {index} has one connection to segment {a}, now connecting.")

                    # Connecting Pi of current segment to Po of connected segment
                    arterial_elements['SS'][str(a)][0] = -1 * arterial_elements['SS'][str(index)][0]
                    # model.connect(arterial_elements['SS'][str(index)][0], arterial_elements['SS'][str(a)][0])
                    
                    # Connecting Fi of connected segment to Fo of current segment
                    arterial_elements['SS'][str(index)][1] = -1 * arterial_elements['SS'][str(a)][1]
                    # model.connect(arterial_elements['SS'][str(a)][1], arterial_elements['SS'][str(index)][1])

                else: ## MULTIPLE CONNECTIONS --------------------------------------------------------------------
                    print(f"Segment {index} has multiple connections {connections}, now connecting {[a, *rest]}.")
                    n = len([a, *rest])
                    sumb = model.SUM('+' * n, name=f"Sum: {connections} to {index}")   # Create a appropriately sized sum block to combine outputs
                    for i, conn in enumerate([a, *rest]):

                        # Connecting Pi of current segment to Po of connected segment
                        arterial_elements['SS'][str(conn)][0] = -1 * arterial_elements['SS'][str(index)][0]
                        # model.connect(arterial_elements['SS'][str(index)][0], arterial_elements['SS'][str(conn)][0])

                        # Connect Fi of connected segment to sum block
                        sumb[i] = -1 * arterial_elements['SS'][str(conn)][1]
                        # model.connect(arterial_elements['SS'][str(conn)][1], sumb[i]) 
                        print(f"Connected segment {index} to {conn} with sum block of {n} inputs.")

                    # Connect Fi of combined segments back into Fo of current segment
                    model.connect(sumb, arterial_elements['SS'][str(index)][1])

            case _: # Error handling for any other format
                raise ValueError(f"Unexpected connections format for segment {index}: {connections}")

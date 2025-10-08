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
    def __init__(self, sim: bdsim.BDSim, rs, l, c, index, rp=None, ped=80):
        """
        Initialize the arterial element block
        """
        self.sim = sim
        self.arterial_element = bdsim.BlockDiagram()
        self.make_art_element(rs, l, c, index, rp, ped)
    
    def make_art_element(self, rs, l, c, index, rp=None, ped=80):
        """
        Simple arterial element model
        dFi/dt = 1/L * (Pi - Po)
        dPo/dt = 1/C * (Fi - Fo - Po/Rp)
        """
        
            
        self.arterial_element  = self.sim.blockdiagram(name=str(index))

        # Ports: inputs [Pi, Fo], outputs [Po, Fi]
        inp  = self.arterial_element.INPORT(2, name=f'in_{index}')   # inp[0]=Pi, inp[1]=Fo

        # logic to remove Fi output for 1st segment
        if index == 1:

            outp = self.arterial_element.OUTPORT(1, name=f'out_{index}')  # outp[0]=Po
        else:
            outp = self.arterial_element.OUTPORT(2, name=f'out_{index}')  # outp[0]=Po, outp[1]=Fi

        # Gains
        k_invl = self.arterial_element.GAIN(-1.0 / l, name= "k_invl")     # -1/L
        k_invc = self.arterial_element.GAIN(-1.0 / c, name= "k_invc")     # -1/C
        k_rs   = self.arterial_element.GAIN(rs, name= "k_rs")          # Rs

        # States (integrators)
        int_fi = self.arterial_element.INTEGRATOR(x0=0.0,  name='Fi')   #∫ (Pi - Po - Rs*Fi) dt
        int_po = self.arterial_element.INTEGRATOR(x0=ped, name='Po')    #∫ (Fi - Fo - Po/Rp) dt

        # Sums
        sum_f = self.arterial_element.SUM('+++', name='F')   # Pi + (- Po) + (- Rs*Fi)

        if rp is not None:
            sum_p = self.arterial_element.SUM('--+', name='P')   # Fi + (- Fo) + (- Po/Rp)
            k_1rp  = self.arterial_element.GAIN(1.0 / rp, name= "k_1rp")    # 1/Rp
            self.arterial_element.connect(k_invc, k_1rp)    # - Po/Rp
            self.arterial_element.connect(k_1rp, sum_p[2])  # -Po -> -Po/Rp
        else:
            sum_p = self.arterial_element.SUM('--', name='P')   # - Fi - (- Fo) + (- Po/Rp)


        ### Fi Calculations: dFi/dt = 1/L * ∫(Pi - Po - Rs*Fi)dt
        # Pi + (- Po) + (- Rs*Fi)
        self.arterial_element.connect(inp[0],  sum_f[0])   # inp Pi -> sum_f[0]
        self.arterial_element.connect(k_invc,  sum_f[1])   # - Po
        self.arterial_element.connect(k_rs,    sum_f[2])   # - Rs*Fi

        self.arterial_element.connect(sum_f, int_fi)       # Pi + (- Po) + (- Rs*Fi) -> ∫()

        self.arterial_element.connect(int_fi, k_invl)      # ∫(Pi + (- Po) + (- Rs*Fi)) -> 1/L * ∫(Pi + (- Po) + (- Rs*Fi))

        # -Fi
        if index == 1:
            clip = self.arterial_element.CLIP(min= -100000000, max=0, name=f'Clip -Rs*Fi {index}')
            self.arterial_element.connect(k_invl, clip)
            self.arterial_element.connect(clip, sum_p[0], k_rs)  # -Fi -> -Rs*Fi & sum_p[0] for next calculations

             # -Fi -> -Rs*Fi & sum_p[0] for next calculations
        else:
            self.arterial_element.connect(k_invl, k_rs, outp[1])
            self.arterial_element.connect(k_invl, sum_p[0])    # Fi
        # Fi + (- Fo) + (- Po/Rp)
        
        self.arterial_element.connect(inp[1],  sum_p[1])    # - Fo

        self.arterial_element.connect(sum_p, int_po)       # Fi + (- Fo) + (- Po/Rp) -> ∫()
        self.arterial_element.connect(int_po, k_invc)  # ∫(Fi + (- Fo) + (- Po/Rp)) -> -1/C * ∫(Fi + (- Fo) + (- Po/Rp)) = -Po

        # bd.connect(k_invC, k_1rp, outp[0])  # -Po -> -Po/Rp
        self.arterial_element.connect(k_invc, outp[0])  # -Po -> -Po/Rp
        if index == 1 or index == 2:
            scope_pi = self.arterial_element.SCOPE(name = f'Scope Pi {index}')
            scope_Fo = self.arterial_element.SCOPE(name = f'Scope Fo {index}')
            scope_rs = self.arterial_element.SCOPE(name = f'Scope RS, i.e. -Rs*Fi {index}')
            scope_invl = self.arterial_element.SCOPE(name = f'Scope invL, i.e. -Fi {index}')
            scope_invc = self.arterial_element.SCOPE(name = f'Scope invC, i.e. -Po {index}')
            scope_intfi = self.arterial_element.SCOPE(name = f'Scope int (P_i - P_o - R_s*F_i) {index}')
            scope_intpo = self.arterial_element.SCOPE(name = f'Scope int (F_i - F_o - P_o/R_p) {index}')
            
            self.arterial_element.connect(inp[1], scope_Fo)  # Fo
            self.arterial_element.connect(inp[0], scope_pi)  # Pi
            self.arterial_element.connect(k_rs, scope_rs)  # -Rs*Fi  # For debugging purposes
            self.arterial_element.connect(k_invl, scope_invl)  # -Fi  # For debugging purposes
            self.arterial_element.connect(k_invc, scope_invc)  # -Po
            self.arterial_element.connect(int_fi, scope_intfi)  # Pi + (- Po) + (- Rs*Fi)  # For debugging purposes
            self.arterial_element.connect(int_po, scope_intpo)  # Fi + (- Fo) + (- Po/Rp)  # For debugging purposes

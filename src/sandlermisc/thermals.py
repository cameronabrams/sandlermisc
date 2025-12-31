import numpy as np
from .gas_constant import GasConstant

def unpackCp(Cp: float | list[float] | dict[str, float]):
    if isinstance(Cp, float):
        a = Cp
        b, d, d = 0.0, 0.0, 0.0
    elif isinstance(Cp, list):
        a, b, c, d = Cp
    elif isinstance(Cp, dict):
        a, b, c, d = Cp['a'], Cp['b'], Cp['c'], Cp['d']
    else:
        a, b, c, d = 0.0, 0.0, 0.0, 0.0
    return a, b, c, d

def DeltaH_IG(T1: float, T2: float, Cp: float | list[float] | dict[str, float] = None):
    a, b, c, d = unpackCp(Cp)
    dt1 = T2 - T1
    dt2 = T2**2 - T1**2
    dt3 = T2**3 - T1**3
    dt4 = T2**4 - T1**4
    return a * dt1 + b / 2 * dt2 + c / 3 * dt3 + d / 4 * dt4

def DeltaS_IG(T1: float, P1: float, T2: float, P2: float, Cp: float | list[float] | dict[str, float], R: GasConstant):
    a, b, c, d = unpackCp(Cp)
    lrt = np.log(T2 / T1)
    dt1 = T2 - T1
    dt2 = T2**2 - T1**2
    dt3 = T2**3 - T1**3
    return a * lrt + b * dt1 + c / 2 * dt2 + d / 3 * dt3 - R * np.log(P2 / P1)
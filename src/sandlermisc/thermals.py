import math
import logging
from .gas_constant import GasConstant

logger = logging.getLogger(__name__)

def unpackCp(Cp: float | list[float] | dict[str, float]):
    if isinstance(Cp, float) or isinstance(Cp, int):
        return float(Cp), 0.0, 0.0, 0.0
    elif isinstance(Cp, dict):
        return Cp['a'], Cp['b'], Cp['c'], Cp['d']
    elif hasattr(Cp, '__len__'): # list, numpy.ndarray
        return Cp[0], Cp[1], Cp[2], Cp[3]
    else:
        raise TypeError(f'Unrecognized type {type(Cp)} for unpacking Cp')

def DeltaH_IG(T1: float, T2: float, Cp: float | list[float] | dict[str, float] = None):
    a, b, c, d = unpackCp(Cp)
    dt1 = T2 - T1
    dt2 = T2**2 - T1**2
    dt3 = T2**3 - T1**3
    dt4 = T2**4 - T1**4
    return a * dt1 + b / 2 * dt2 + c / 3 * dt3 + d / 4 * dt4

def DeltaS_IG(T1: float, P1: float, T2: float, P2: float, Cp: float | list[float] | dict[str, float], R: GasConstant = GasConstant()):
    a, b, c, d = unpackCp(Cp)
    lrt = math.log(T2 / T1)
    dt1 = T2 - T1
    dt2 = T2**2 - T1**2
    dt3 = T2**3 - T1**3
    return a * lrt + b * dt1 + c / 2 * dt2 + d / 3 * dt3 - R * math.log(P2 / P1)
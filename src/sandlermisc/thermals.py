import pint
import math
from .constants import R, ureg

def unpackCp(Cp: float | list[float] | dict[str, float]):
    """
    Unpack heat capacity polynomial coefficients.
    
    Returns coefficients for: Cp = a + b*T + c*T^2 + d*T^3
    where Cp is in J/(mol*K) and T is in K.
    """
    if isinstance(Cp, float) or isinstance(Cp, int):
        return float(Cp), 0.0, 0.0, 0.0
    elif isinstance(Cp, dict):
        return Cp['a'], Cp['b'], Cp['c'], Cp['d']
    elif hasattr(Cp, '__len__'):  # list, numpy.ndarray
        return Cp[0], Cp[1], Cp[2], Cp[3]
    else:
        raise TypeError(f'Unrecognized type {type(Cp)} for unpacking Cp')

def DeltaH_IG(
    T1: float | pint.Quantity, 
    T2: float | pint.Quantity, 
    Cp: float | list[float] | dict[str, float] = None
) -> pint.Quantity:
    """
    Calculate ideal gas enthalpy change.
    
    Parameters
    ----------
    T1, T2 : float or Quantity
        Temperatures (assumed Kelvin if float)
    Cp : float, list, or dict
        Heat capacity coefficients (no units needed - assumed J/mol/K basis)
        
    Returns
    -------
    Quantity
        Enthalpy change in J/mol
    """
    # Extract magnitudes in Kelvin
    if isinstance(T1, pint.Quantity):
        T1_K = T1.m_as('K')
    else:
        T1_K = T1
        
    if isinstance(T2, pint.Quantity):
        T2_K = T2.m_as('K')
    else:
        T2_K = T2
    
    # Calculate (dimensionless)
    a, b, c, d = unpackCp(Cp)
    dt1 = T2_K - T1_K
    dt2 = T2_K**2 - T1_K**2
    dt3 = T2_K**3 - T1_K**3
    dt4 = T2_K**4 - T1_K**4
    
    dH = a * dt1 + b / 2 * dt2 + c / 3 * dt3 + d / 4 * dt4
    
    # Return with units
    return dH * ureg.J / ureg.mol


def DeltaS_IG(
    T1: float | pint.Quantity,
    P1: float | pint.Quantity,
    T2: float | pint.Quantity,
    P2: float | pint.Quantity,
    Cp: float | list[float] | dict[str, float],
    R_gas: pint.Quantity = R
) -> pint.Quantity:
    """
    Calculate ideal gas entropy change.
    
    Parameters
    ----------
    T1, T2 : float or Quantity
        Temperatures (assumed Kelvin if float)
    P1, P2 : float or Quantity
        Pressures (assumed Pascal if float)
    Cp : float, list, or dict
        Heat capacity coefficients (no units needed - assumed J/mol/K basis)
    R_gas : Quantity
        Gas constant (default: 8.314 J/mol/K)
        
    Returns
    -------
    Quantity
        Entropy change in J/(mol*K)
    """
    # Extract magnitudes in consistent units
    if isinstance(T1, pint.Quantity):
        T1_K = T1.m_as('K')
    else:
        T1_K = T1
        
    if isinstance(T2, pint.Quantity):
        T2_K = T2.m_as('K')
    else:
        T2_K = T2
        
    if isinstance(P1, pint.Quantity):
        P1_Pa = P1.m_as('Pa')
    else:
        P1_Pa = P1
        
    if isinstance(P2, pint.Quantity):
        P2_Pa = P2.m_as('Pa')
    else:
        P2_Pa = P2
    
    # Get R magnitude
    R_val = R_gas.m_as('J/(mol*K)')
    
    # Calculate (dimensionless)
    a, b, c, d = unpackCp(Cp)
    lrt = math.log(T2_K / T1_K)
    dt1 = T2_K - T1_K
    dt2 = T2_K**2 - T1_K**2
    dt3 = T2_K**3 - T1_K**3
    
    dS = a * lrt + b * dt1 + c / 2 * dt2 + d / 3 * dt3 - R_val * math.log(P2_Pa / P1_Pa)
    
    # Return with units
    return dS * ureg.J / (ureg.mol * ureg.K)
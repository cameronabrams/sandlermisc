# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
TeX utility functions for sandlermisc
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def table_as_tex(table: dict | pd.DataFrame, float_format: callable = '\({:.4f}\)'.format, 
                 drop_zeros: list[bool] = None, total_row: list[str] = [],
                 index: bool = False):
    """
    A wrapper to Dataframe.to_latex() that takes a dictionary of heading: column
    items and generates a table 
    
    Parameters
    ----------
    table : dict or pd.DataFrame
        dictionary of column_name: list_of_column_values or a ready DataFrame
    float_format : callable, optional
        function to format floating point numbers; default is 4 decimal places in math mode
    drop_zeros : list of bool, optional
        list of booleans parallel to table keys indicating whether to drop rows with zero in that column; default is None
    total_row : list, optional
        list of strings representing a total row to be added at the bottom of the table; default is empty list
    index : bool, optional
        whether to include the DataFrame index in the LaTeX table; default is False

    Returns
    -------
    tablestring : str
        LaTeX formatted table string
    """
    if isinstance(table, pd.DataFrame):
        df = table
    else:
        df = pd.DataFrame(table)
    if drop_zeros:
        for k, d in zip(table.keys(), drop_zeros):
            if d:
                df = df[df[k] != 0.]
    tablestring = df.to_latex(float_format=float_format, index=index, header=True)
    logger.debug(f'Generated table string:\n{tablestring}\n')
    if len(total_row) > 0:
        i = tablestring.find(r'\bottomrule')
        tmpstr = tablestring[:i-1] + r'\hline' + '\n' + '&'.join(total_row) + r'\\' + '\n' + tablestring[i:]
        tablestring = tmpstr
    return tablestring

def Cp_as_tex(Cp_coeff: dict | list, decoration='*', sig: int = 5) -> str:
    """
    Formats a heat capacity polynomial as a LaTeX string.
    
    Parameters
    ----------
    Cp_coeff : dict or list
        dictionary with keys 'a', 'b', 'c', 'd' or list of four coefficients
    decoration : str, optional
        decoration for Cp, e.g., '*' for Cp^*, default is '*'
    sig : int, optional
        number of significant figures for coefficients, default is 5

    Returns
    -------
    retstr : str
        LaTeX formatted heat capacity polynomial string
    """
    idx = [0, 1, 2, 3]
    if type(Cp_coeff) == dict:
        idx = 'abcd'
    sgns=[]
    for i in range(4):
        sgns.append('-' if Cp_coeff[idx[i]]<0 else '+')
    retstr = r'$C_p^' + f'{decoration}' + r'$ = ' + f'{Cp_coeff[idx[0]]:.3f} {sgns[1]} '
    retstr += format_sig(np.abs(Cp_coeff[idx[1]]),sig=sig)+r' $T$ '+f'{sgns[2]} '
    retstr += format_sig(np.abs(Cp_coeff[idx[2]]),sig=sig)+r' $T^2$ '+f'{sgns[3]} '
    retstr += format_sig(np.abs(Cp_coeff[idx[3]]),sig=sig)+r' $T^3$'
    return(retstr)

def format_sig(x: float, sig: int = 5, use_tex: bool = True) -> str:
    """
    Formats a floating point number to a specified number of significant figures.
    
    Parameters
    ----------
    x : float
        the number to format
    sig : int, optional
        number of significant figures, default is 5
    use_tex : bool, optional
        whether to format in LaTeX scientific notation, default is True 

    Returns
    -------
    s : str
        formatted string
    """
    s = format(x, f",.{sig}g")
    if "e" in s:
        mantissa, exponent = s.split("e")
        if use_tex:
            exponent = int(exponent)      # removes + and leading zeros
            return rf"{mantissa}\times 10^{{{exponent}}}"
    return s

# def StoProd_as_tex(bases,nu,parens=False):
#     """
#     Formats a stoichiometric expression as a LaTeX string.

#     Parameters
#     ----------
#     bases : list of str
#         list of species names
#     nu : list of float
#         list of stoichiometric coefficients, parallel to bases
#     parens : bool, optional
#         whether to enclose species in parentheses, default is False
    
#     Returns
#     -------
#     str
#         LaTeX formatted stoichiometric expression
#     """
#     reactants, products, nureactants, nuproducts = split_reactants_products(bases,nu)
#     expreactants = ['' if n==1 else r'^{'+n+r'}' for n in nureactants]
#     expproducts = ['' if n==1 else r'^{'+n+r'}' for n in nuproducts]
#     if parens:
#         numerator = ''.join([r'('+c+r')'+e for c,e in zip(products,expproducts)])
#         denominator = ''.join([r'('+c+r')'+e for c,e in zip(reactants,expreactants)])
#     else:
#         numerator = ''.join([c+e for c,e in zip(products,expproducts)])
#         denominator = ''.join([c+e for c,e in zip(reactants,expreactants)])
#     return r'\frac{' + numerator + r'}{' + denominator + r'}'

# def split_reactants_products(emps: list[str], nu: list[float]) -> tuple[list[str], list[str], list[str], list[str]]:
#     """
#     Splits species and their stoichiometric coefficients into reactants and products.
    
#     Parameters
#     ----------
#     emps : list of str
#         list of species names
#     nu : list of float
#         list of stoichiometric coefficients, parallel to emps

#     Returns
#     -------
#     tuple of lists
#         (reactants, products, nureactants, nuproducts)
#     """
#     reactants = []
#     products = []
#     nureactants = []
#     nuproducts = []
#     for e, nn in zip(emps, nu):
#         n = float(np.round(nn, 5))
#         if n < 0:
#             reactants.append(e)
#             f = fr.Fraction(-n)
#             nureactants.append(frac_or_int_as_tex(f))
#         elif n > 0:
#             products.append(e)
#             f = fr.Fraction(n)
#             nuproducts.append(frac_or_int_as_tex(f))
#     return (reactants, products, nureactants, nuproducts)

# def frac_or_int_as_tex(f: fr.Fraction) -> str:
#     """
#     Formats a Fraction as a LaTeX string, using \frac{}{} if necessary.
    
#     Parameters
#     ----------
#     f : fr.Fraction
#         the fraction to format
        
#     Returns
#     -------
#     str
#         LaTeX formatted string
#     """
#     if f.denominator > 1:
#         return r'\frac{'+'{:d}'.format(f.numerator)+r'}{'+'{:d}'.format(f.denominator)+r'}'
#     else:
#         if f.numerator == 1:
#             return ''
#         else:
#             return '{:d}'.format(f.numerator)
        

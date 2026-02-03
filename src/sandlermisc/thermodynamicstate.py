# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Defines the ThermodynamicState base class for thermodynamic states.
"""

from __future__ import annotations
import pint
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import logging

import numpy as np

from .statereporter import StateReporter
from .constants import ureg, R

logger = logging.getLogger(__name__)

def is_none_or_empty(val):
    if val is None:
        return True
    if isinstance(val, (list, dict)) and len(val) == 0:
        return True
    if isinstance(val, np.ndarray) and val.size == 0:
        return True
    return False

_cached_properties_location = '_calculated_vars'
def cached_property(func):
    """Decorator that dynamically looks up _calc_xxx methods"""
    cache_key = func.__name__
    calc_method_name = f'_calc_{cache_key}'
    
    @property
    def wrapper(self):
        if getattr(self, '_do_smart_resolve', True):
            calc_method = getattr(self, calc_method_name)  # ← Runtime lookup
            if self._cache_property_update(cache_key, calc_method):
                return self._cache[_cached_properties_location][cache_key]
        return getattr(self, calc_method_name)()  # ← Runtime lookup
    
    wrapper.__doc__ = func.__doc__
    return wrapper

@dataclass
class ThermodynamicState(ABC):
    """
    Base class for thermodynamic state of a pure component
    """

    name: str = "ThermodynamicState"
    """ Name of the thermodynamic state """

    """ State variables """
    P: pint.Quantity = None
    """ Pressure """
    T: pint.Quantity = None
    """ Temperature """
    v: pint.Quantity = None
    """ Specific volume """
    u: pint.Quantity = None
    """ Specific internal energy """
    h: pint.Quantity = None
    """ Specific enthalpy """
    s: pint.Quantity = None
    """ Specific entropy """

    x: float = None
    """ Vapor fraction (quality) """
    Liquid: ThermodynamicState = None
    """ Liquid phase state when saturated """
    Vapor: ThermodynamicState = None
    """ Vapor phase state when saturated """

    _STATE_VAR_ORDERED_FIELDS = ['T', 'P', 'v', 's', 'h', 'u']
    """ Ordered fields that define the input state """

    _STATE_VAR_FIELDS = frozenset(_STATE_VAR_ORDERED_FIELDS).union({'x'})
    """ Fields that define the input state for caching purposes; includes vapor fraction 'x' """

    _PARAMETER_FIELDS = frozenset(set())
    """ Fields that define parameters for the EOS; to be defined in subclasses """

    def swap_input_vars(self, input_var: str, state_var: str):
        """ Swap one of the state vars into the input var set """
        logger.debug(f'Swapping input var {input_var} with state var {state_var} in ThermodynamicState {self.name}')
        inputs = self._cache.get('_input_vars_specified', [])
        if input_var in inputs and state_var not in inputs:
            inputs.remove(input_var)
            inputs.append(state_var)
            self._cache['_input_vars_specified'] = inputs
            logger.debug(f'Input vars after swap: {self._cache["_input_vars_specified"]}')
        else:
            raise(ValueError(f'Cannot swap input var {input_var} with state var {state_var}: check if input var is specified and state var is not specified.'))

    def get_input_varnames(self) -> list[str]:
        """ Get the list of input variable names """
        return self._cache.get('_input_vars_specified', []).copy()

    def _dimensionalize(self, name: str, value: float | pint.Quantity) -> pint.Quantity:
        """
        Apply default units to raw numbers or convert incoming quantities to default units.

        Parameters
        ----------
        name : str
            Name of the field
        value : float or Quantity
            Value to dimensionalize

        Returns
        -------
        Quantity
            Dimensionalized value
        """
        # update value to carry default units if necessary
        if (isinstance(value, float) or isinstance(value, int)) and name in self._STATE_VAR_FIELDS:
            # apply default units to raw numbers
            default_unit = self.get_default_unit(name)
            if default_unit is not None:
                value = value * default_unit
        elif isinstance(value, pint.Quantity) and name in self._STATE_VAR_FIELDS:
            # convert any incoming pint.Quantity to default units
            value = value.to(self.get_default_unit(name))
        return value

    def get_default_unit(self, field_name: str) -> pint.Unit:
        """
        Get the default unit for a given field
        
        Parameters
        ----------
        field_name: str
            Name of the field

        Returns
        -------
        pint.Unit
            Default unit for the field
        """
        _default_unit_map = {
            'P': ureg.MPa,
            'T': ureg.K,
            'v': ureg.m**3 / ureg.mol,
            'u': ureg.J / ureg.mol,
            'h': ureg.J / ureg.mol,
            's': ureg.J / (ureg.mol * ureg.K),
        }

        return _default_unit_map.get(field_name, ureg.dimensionless)
    
    def get_formatter(self, field_name: str) -> str:
        """Get the formatter for a given field"""
        formatter_map = {
            'P': '{: 5g}',
            'T': '{: 5g}',
            'x': '{: 5g}',
            'v': '{: 6g}',
            'u': '{: 6g}',
            'h': '{: 6g}',
            's': '{: 6g}',
            'Pv': '{: 6g}',
        }
        return formatter_map.get(field_name)

    def _scalarize(self):
        """ Convert all properties to scalars (not np.float64) """
        for p in self._STATE_VAR_FIELDS.union({'x'}):
            val = getattr(self, p)
            if isinstance(val, np.float64):
                setattr(self, p, val.item())
        if hasattr(self, 'Liquid') and self.Liquid is not None:
            self.Liquid._scalarize()
        if hasattr(self, 'Vapor') and self.Vapor is not None:
            self.Vapor._scalarize()

    def delta(self, other: State) -> dict:
        """ Calculate property differences between this state and another state """
        delta_props = {}
        for p in self._STATE_VAR_FIELDS:
            val1 = getattr(self, p)
            val2 = getattr(other, p)
            if val1 is not None and val2 is not None:
                delta_props[p] = val2 - val1
        delta_props['Pv'] = other.Pv - self.Pv
        return delta_props

    def __repr__(self):
        """Show which variables are inputs vs computed."""
        inputs = self._cache.get('_input_vars_specified', [])
        parts = []
        for var in self._STATE_VAR_ORDERED_FIELDS + ['x']:
            val = getattr(self, var)
            if val is not None:
                marker = '*' if var in inputs else ''
                parts.append(f"{var}{marker}={val}")
        return f"State({self.name}: {', '.join(parts)})"

    def report(self, additional_fields: list[str] = [], 
                     parameters: list[str] = []) -> str:
        default_fields = self._STATE_VAR_ORDERED_FIELDS + ['Pv']
        for field in additional_fields:
            if not field in default_fields:
                default_fields.append(field)
        reporter = statereporter.StateReporter()
        for p in default_fields:
            if getattr(self, p) is not None:
                reporter.add_property(p, getattr(self, p).m, self.get_default_unit(p), self.get_formatter(p))
        for p in parameters:
            if hasattr(self, p):
                val = getattr(self, p)
                if val is not None:
                    if p != 'Cp':
                        reporter.add_property(p, val, None, None)
                    else:
                        reporter.pack_Cp(val, fmts=["{:.2f}", "{:.3e}", "{:.3e}", "{:.3e}"])
        if self.x is not None:
            reporter.add_property('x', self.x, f'mass fraction vapor')
            if 0 < self.x < 1:
                for phase, state in [('L', self.Liquid), ('V', self.Vapor)]:
                    for p in default_fields:
                        if not p in 'TP':
                            if getattr(state, p) is not None:
                                reporter.add_property(f'{p}{phase}', getattr(state, p).m, self.get_default_unit(p), self.get_formatter(p))
        return reporter.report()

    @abstractmethod
    def resolve(self) -> bool:
        """
        Resolve the thermodynamic state based on input variables.  Does no checking and should be implemented by 
        the subclass.
        
        Returns
        -------
        bool
            True if the state was successfully resolved, False otherwise.
        """
        return False

    def smart_resolve(self) -> bool:
        resolved = False
        if self._is_self_specified() and self._is_self_parameterized() and not self._cache.get('_is_complete', False):
            logger.debug(f'resolve: ThermodynamicState {self.name}: Starting resolution process.')
            if self._do_smart_resolve:
                self._cache['_is_calculating'] = True
            resolved = self.resolve()
            if self._do_smart_resolve:
                self._cache['_is_calculating'] = False
            self._scalarize()
            self._cache['_is_complete'] = resolved
        return resolved

    """ enable smart resolution of calculated variables """
    _do_smart_resolve: bool = field(default=True, init=True, repr=False, compare=False)

    _cache: dict = field(default_factory=dict, init=False, repr=False)
    """ Internal cache for tracking input variables and state completeness """

    def _cache_property_update(self, key: str, calculator: callable):
        if not self._do_smart_resolve:
            return False
        if not key in self._cache[_cached_properties_location]:
            value = calculator()
            self._cache[_cached_properties_location][key] = value
        return True
    
    def __new__(cls, *args, **kwargs):
        """
        Custom __new__ to handle smart checking initialization.  If smart checking is disabled,
        a minimal cache is created.  If enabled, a full cache with tracking is created.
        """
        # logger.debug(f'Creating new ThermodynamicState instance with args: {args}, kwargs: {kwargs}')
        instance = object.__new__(cls)
        # Check if smart_resolve is disabled
        smart_resolve = kwargs.get('_do_smart_resolve', True)

        instance._do_smart_resolve = smart_resolve

        if smart_resolve:
            # Full initialization with tracking
            object.__setattr__(instance, '_cache', {
                '_input_vars_specified': [],
                '_parameters_specified': [],
                '_is_specified': False, # True if enough input vars are specified
                '_is_parameterized': False, # True if all parameters are specified
                '_is_calculating': False, # true if currently in calculation process
                '_is_complete': False, # true if all caculated variables are valid
                '_calculated_vars': {} # calculated variables that aren't defined as state variables here
            })
            logger.debug(f'Initialized full _cache for ThermodynamicState instance')
            logger.debug(f'_cache initial state: {instance._cache}')
        else:
            # Minimal cache for simple version
            object.__setattr__(instance, '_cache', {})
            logger.debug(f'Initialized minimal _cache for ThermodynamicState instance')
        
        return instance

    @classmethod
    def simple(cls, *args, **kwargs) -> ThermodynamicState:
        """ Create a simple ThermodynamicState without smart checking """
        logger.debug(f'Creating simple {cls.__name__} instance with args: {args}, kwargs: {kwargs}')
        kwargs['_do_smart_resolve'] = False
        return cls(*args, **kwargs)

    def __setattr__(self, name, value):
        logger.debug(f'ThermodynamicState {self.name}: __setattr__ called for {name} with value {value} (smart? {getattr(self, "_do_smart_resolve", None)})')
        value = self._dimensionalize(name, value)
        if not hasattr(self, '_do_smart_resolve'):
            logger.debug(f'ThermodynamicState {self.name}: _do_smart_resolve attribute not found, defaulting to normal setattr.')
            object.__setattr__(self, name, value)
        elif self._do_smart_resolve:
            logger.debug(f'ThermodynamicState {self.name}: _do_smart_resolve attribute True, using _smart_setattr_.')
            self._smart_setattr_(name, value)
        else:
            logger.debug(f'ThermodynamicState {self.name}: _do_smart_resolve attribute False, defaulting to normal setattr.')
            object.__setattr__(self, name, value)

    def _blank_computed_state_vars(self):
        """
        Clear all computed state variables
        """
        for var in self._STATE_VAR_FIELDS:
            if var not in self._cache.get('_input_vars_specified', []):
                logger.debug(f'ThermodynamicState {self.name}: Blank computed state variable {var}')
                object.__setattr__(self, var, None) # this bypasses the smart setter so setting them to None is allowed
        self._cache['_is_complete'] = False

    def _invalidate(self):
        self._cache['_is_complete'] = False # all calculated variables are now invalid
        self._cache['_calculated_vars'] = {}
        self._blank_computed_state_vars()

    def _is_input_var(self, name):
        return name in self._STATE_VAR_FIELDS

    def _is_parameter(self, name):
        return name in self._PARAMETER_FIELDS

    def _is_specified_input_var(self, name):
        """ Check if a variable is one of the specified input variables """
        return name in self._cache.get('_input_vars_specified', [])

    def _is_self_specified(self):
        """ Check if the state is fully specified """
        current_inputs = self._cache.get('_input_vars_specified', [])
        return len(current_inputs) == 2

    def _is_self_parameterized(self):
        """ Check if the state is fully parameterized """
        if len(self._PARAMETER_FIELDS) == 0:
            return True
        return all(param in self._cache.get('_parameters_specified', []) for param in self._PARAMETER_FIELDS)

    def _set_state_var(self, name, value):
        object.__setattr__(self, name, value)
        current_inputs = self._cache.get('_input_vars_specified', [])
        if len(current_inputs) < 2:
            if name not in current_inputs:
                logger.debug(f'__set_attr__: ThermodynamicState {self.name}: Adding new input variable {name} with value {value}')
                current_inputs.append(name)
        self._cache['_input_vars_specified'] = current_inputs
        if name in current_inputs:
            logger.debug(f'__set_attr__: Invalidating ThermodynamicState {self.name} due to change in input variable {name}')
            self._invalidate() # we've changed an existing input variable

    def _is_specified_parameter(self, name):
        """ Check if a variable is one of the specified parameters """
        return name in self._cache.get('_parameters_specified', [])

    def _set_parameter(self, name, value):
        object.__setattr__(self, name, value)
        if value is not None:
            self._invalidate() # changing a parameter invalidates the state
            if name not in self._cache['_parameters_specified']:
                logger.debug(f'__set_attr__: ThermodynamicState {self.name}: Adding new parameter variable {name} with value {value}')
                self._cache['_parameters_specified'].append(name)

    def _smart_setattr_(self, name, value):
        """Custom attribute setter with input tracking and auto-resolution."""
        logger.debug(f'ThermodynamicState {self.name}: _smart_setattr_ called for {name} with value {value} (current value: {getattr(self, name, None)})')

        # Prevent overwriting any attributes with None or empty 
        if is_none_or_empty(value):
            logger.debug(f'ThermodynamicState {self.name}: Not setting {name} to None or empty value; skipping.')
            return
            
        # Set non-state variables normally
        if not (self._is_input_var(name) or self._is_parameter(name)):
            logger.debug(f'ThermodynamicState {self.name}: Setting non-state/non-parameter variable {name} to {value}')
            object.__setattr__(self, name, value)
            # logger.debug(f'ThermodynamicState {self.name}: __setattr__ completed for non-state variable {name}. Current _cache: {self._cache}')
            return
        
        # handle parameters
        if self._is_parameter(name):
            logger.debug(f'ThermodynamicState {self.name}: Setting parameter {name} to {value}')
            self._set_parameter(name, value)
            # logger.debug(f'ThermodynamicState {self.name}: __setattr__ completed for parameter {name}. Current _cache: {self._cache}')
        else: # handle state variables
            self._set_state_var(name, value)
            # self._set_input_var(name, value)
                
        self._cache['_is_specified'] = self._is_self_specified()
        self._cache['_is_parameterized'] = self._is_self_parameterized()
        self._smart_post_init()
        
        # logger.debug(f'ThermodynamicState {self.name}: __setattr__ completed for {name}. Current _cache: {self._cache}')

    def _smart_post_init(self):
        """Post-initialization to check for completeness and resolve state if needed."""
        logger.debug(f'__post_init__: ThermodynamicState {self.name}: checking specification completeness.')
        logger.debug(f'_cache at post_init: {self._cache}')
        if not self._cache['_is_calculating']:
            self._cache['_is_complete'] = self.smart_resolve()
            logger.debug(f'__post_init__: ThermodynamicState {self.name}: state resolved: {self._cache["_is_complete"]}')

    def __post_init__(self):
        if not hasattr(self, '_do_smart_resolve'):
            pass
        elif self._do_smart_resolve:
            self._smart_post_init()
        else:
            pass
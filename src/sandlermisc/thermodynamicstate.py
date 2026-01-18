from __future__ import annotations
import pint
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import logging

import numpy as np

from . import statereporter

logger = logging.getLogger(__name__)

_ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)

@dataclass
class ThermodynamicState(ABC):
    """
    Thermodynamic state of a pure component
    """

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

    _cache: dict = field(default_factory=dict, init=False, repr=False)
    """ Internal cache for tracking input variables and state completeness """

    def __new__(cls, *args, **kwargs):
        """Set up _cache before any field assignments."""
        logger.debug(f'Creating new State instance with args: {args}, kwargs: {kwargs}')
        instance = object.__new__(cls)
        object.__setattr__(instance, '_cache', {
            '_input_vars': [],
            '_is_specified': False,
            '_is_complete': False
        })
        logger.debug(f'Initialized _cache for State instance: {instance._cache}')
        return instance

    def _dimensionalize(self, name, value):
        # update value to carry default units if necessary
        if (isinstance(value, float) or isinstance(value, int)) and name in self._STATE_VAR_FIELDS:
            # apply default units to raw numbers
            default_unit = self.get_default_unit(name)
            if default_unit is not None:
                value = value * _ureg(default_unit)
        elif isinstance(value, pint.Quantity) and name in self._STATE_VAR_FIELDS:
            # convert any incoming pint.Quantity to default units
            value = value.to(self.get_default_unit(name))
        return value
    
    def __setattr__(self, name, value):
        """Custom attribute setter with input tracking and auto-resolution."""

        logger.debug(f'State {self.name}: __setattr__ called for {name} with value {value} (current value: {getattr(self, name, None)})')
        if (value is None or value == {} or value == []) and getattr(self, name, None) is not None:
            logger.debug(f'State {self.name}: Attempt to set {name} to None ignored to preserve resolved value {getattr(self, name)}')
            return   # Don't overwrite resolved value with None

        # Non-state variables set normally
        if name not in self._STATE_VAR_FIELDS:
            logger.debug(f'State {self.name}: Setting non-state variable {name} to {value}')
            object.__setattr__(self, name, value)
            return

        current_inputs = self._cache.get('_input_vars', [])
        if name in current_inputs:
            if value is not None:
                value = self._dimensionalize(name, value)
                object.__setattr__(self, name, value)
                logger.debug(f'State {self.name}: Updated input variable {name} to {value}')
                self._cache['_is_complete'] = False
                self._cache['_is_specified'] = len(current_inputs) == 2
                if self._cache['_is_specified']:
                    logger.debug(f'__set_attr__: State {self.name}: Now fully specified with inputs: {current_inputs}, resolving state.')
                    self._resolve()
            else:
                current_inputs.remove(name)
                self._cache['_input_vars'] = current_inputs
                self._blank_computed_state_vars()
                logger.debug(f'State {self.name}: Removed input variable {name}')
                self._cache['_is_specified'] = False
                self._cache['_is_complete'] = False
        else:
            if value is not None:
                value = self._dimensionalize(name, value)
                object.__setattr__(self, name, value)
                if not self._cache.get('_is_specified', False):
                    logger.debug(f'__set_attr__: State {self.name}: Adding new input variable {name} with value {value}')
                    current_inputs.append(name)
                    self._cache['_input_vars'] = current_inputs
                    self._cache['_is_specified'] = len(current_inputs) == 2
                    if self._cache['_is_specified']:
                        logger.debug(f'__set_attr__: State {self.name}: Now fully specified with inputs: {current_inputs}, resolving state.')
                        self._resolve()
                elif self._cache.get('_is_complete', False):
                    logger.debug(f'__set_attr__: State {self.name}: Already fully specified; resetting state with first new input variable {name}')
                    # already fully specified - setting a new input var - blank all computed vars
                    current_inputs = [name]
                    self._cache['_input_vars'] = current_inputs
                    self._cache['_is_specified'] = False
                    self._cache['_is_complete'] = False
                    self._blank_computed_state_vars()
                # set the value
                # if not _is_specified, add to input vars
                # check for specification completeness, and if so, resolve
            else:
                logger.debug(f'__set_attr__: State {self.name}: Setting non-input variable {name} to None')
                # setting a non-input var to None - just set it
                object.__setattr__(self, name, value)

    def __post_init__(self):
        logger.debug(f'__post_init__: State {self.name}: __post_init__ called, checking specification completeness.')
        if self._cache['_is_specified'] and not self._cache['_is_complete']:
            current_inputs = self._cache.get('_input_vars', [])
            logger.debug(f'__post_init__: State {self.name}: Now fully specified with inputs: {current_inputs}, resolving state.')
            self._resolve()
            self._cache['_is_complete'] = True

    def _blank_computed_state_vars(self):
        """
        Clear all computed state variables
        """
        for var in self._STATE_VAR_FIELDS:
            if var not in self._cache.get('_input_vars', []):
                object.__setattr__(self, var, None)
        self._cache['_is_complete'] = False

    def __repr__(self):
        """Show which variables are inputs vs computed."""
        inputs = self._cache.get('_input_vars', [])
        parts = []
        for var in self._STATE_VAR_ORDERED_FIELDS + ['x']:
            val = getattr(self, var)
            if val is not None:
                marker = '*' if var in inputs else ''
                parts.append(f"{var}{marker}={val}")
        return f"State({self.name}: {', '.join(parts)})"

    def get_default_unit(self, field_name: str) -> str:
        """
        Get the default unit for a given field
        
        Parameters
        ----------
        field_name: str
            Name of the field

        Returns
        -------
        str: Default unit as a string that is understandable by pint
        """

        return self._default_unit_map.get(field_name)
    
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

    @property
    def Pv(self):
        """ Pressure * specific volume in default units """
        punit = self.get_default_unit('P')
        vunit = self.get_default_unit('v')
        eunit = self.get_default_unit('u')
        return (self.P.to(punit) * self.v.to(vunit)).to(eunit)

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

    @abstractmethod
    def _resolve(self):
        """
        Abstract method to resolve the thermodynamic state based on input variables.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("The _resolve method must be implemented by subclasses of ThermodynamicState.")
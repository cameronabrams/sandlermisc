# Sandlermisc

> Miscellaneous utilities from Sandler's 5th ed.

Sandlermisc implements a python interface to a few miscellaneous utilities from  _Chemical, Biochemical, and Engineering Thermodynamics_ (5th edition) by Stan Sandler (Wiley, USA). It should be used for educational purposes only.

Current utilities:

1. ``ThermodynamicState``: An abstract class for handling thermodynamic states for pure components
2. ``ureg``: a pint unit registry
3. ``R``: the universal gas constant as a pint Quantity
4. ``DeltaH_IG`` and ``DeltaS_IG``: Ideal-gas delta-h and delta-s calculations

## Installation 

Sandlermisc is available via `pip`:

```sh
pip install sandlermisc
```

## Usage

### API

`ThermodynamicState` is an abstract class that manages state-variable attributes:

* `T` -- temperature
* `P` -- pressure
* `v` -- molar volume or specific volume
* `h` -- molar ethalpy or specific enthapy
* `u` -- molar internal energy or specific internal energy
* `s` -- molar entropy or specific entropy
* `x` -- vapor fraction for a saturated state

A subclass of `ThermodynamicState` must define the method `resolve()` to compute state variables from input state variables.  Any instance of such a subclass will automatically compute all state variables once enough inputs are specified.

`DeltaH_IG` requires the temperature of state 1 (assumed in K if units not specified), the temperature of state 2, and an ideal-gas heat-capacity argument, which can be a scalar, four-element list of floats, or four-element dict with keys `a`, `b`, `c`, and `d`.

```python
>>> from sandlermisc import DeltaH_IG
>>> DeltaH_IG(100, 200, 10)
<Quantity(1000.0, 'joule / mole')>
>>> DeltaH_IG(500, 600, [10., 0.01, 0.00002, 0.000000032]) 
<Quantity(2693.46667, 'joule / mole')>
>>> DeltaH_IG(500, 600, dict(a=10., b=0.01, c=0.00002, d=0.000000032)) 
<Quantity(2693.46667, 'joule / mole')>
```

`DeltaS_IG` requires the temperature and pressure of state 1, the temperature and pressure of state 2, the ideal-gas heat-capacity argument.

```python
>>> from sandlermisc import DeltaS_IG 
>>> DeltaS_IG(500, 10, 600, 12, 10)                
<Quantity(0.307309799, 'joule / mole / kelvin')>
```

One can optionally provide a value for the gas constant `R` to match units of one's `Cp`, if necessary.  By default, `sandlermisc` assumes `Cp` has energy units of J.

## Release History

* 0.4.1
    * pint incorporation
    * Full smart-resolution of ThermodynamicState
* 0.3.2
    * bugfix: `unpackCp` ignored `int`s -- now fixed
    * bugfix: `unpackCp` ignored `np.ndarray` -- now fixed
* 0.3.0
    * `StateReporter` implemented
* 0.1.1
    * bug in converting Cp
* 0.1.0
    * Initial release

## Meta

Cameron F. Abrams – cfa22@drexel.edu

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/cameronabrams](https://github.com/cameronabrams/)

## Contributing

1. Fork it (<https://github.com/cameronabrams/sandlermisc/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

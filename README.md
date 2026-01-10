# Sandlermisc

> Miscellaneous utilities from Sandler's 5th ed.

Sandlermisc implements a python interface to a few miscellaneous utilities from  _Chemical, Biochemical, and Engineering Thermodynamics_ (5th edition) by Stan Sandler (Wiley, USA). It should be used for educational purposes only.

Current utilities:

1. ``GasConstant`` -- a unit-specific implementation of the universal gas constant
2. ``Thermals`` -- ideal-gas calculations of ΔH and ΔS


## Installation 

Sandlermisc is available via `pip`:

```sh
pip install sandlermisc
```

## Usage


### API

`GasConstant()` expects two optional argurments: the pressure units (default Pascal, or "pa") and the volume units (default cubic meter, or "m3").  It returns an object that can be used like a float.

```python
>>> from sandlermisc.gas_constant import GasConstant
R = GasConstant() # J/mol-K
>>> print(R)
8.31446 (pa-m3)/(mol-K)
>>> print(float(R))
8.31446261815324
R_pv = GasConstant("bar", "m3") # bar-m3/mol-K
>>> print(R_pv)     
8.31446e-05 (bar-m3)/(mol-K)
>>> print(float(R_pv)) 
8.31446261815324e-05
>>> R_pv = GasConstant("atm", "l")  
>>> print(R_pv)        
0.0820574 (atm-l)/(mol-K)
>>> print(float(R_pv))
0.08205736608095968
```

`DeltaH_IG` requires the temperature of state 1, the temperature of state 2, and an ideal-gas heat-capacity argument, which can be a scalar, four-element list of floats, or four-element dict with keys `a`, `b`, `c`, and `d`.

```python
>>> from sandlermisc.thermals import DeltaH_IG
>>> DeltaH_IG(100, 200, 10)
1000.0
>>> DeltaH_IG(500, 600, [10., 0.01, 0.00002, 0.000000032]) 
2693.466666666667
>>> DeltaH_IG(500, 600, dict(a=10., b=0.01, c=0.00002, d=0.000000032)) 
2693.466666666667
```

`DeltaS_IG` requires the temperature and pressure of state 1, the temperature and pressure of state 2, the ideal-gas heat-capacity argument, and a GasConstant instance.

```python
>>> from sandlermisc.thermals import DeltaS_IG 
>>> DeltaS_IG(500, 10, 600, 12, 10)                
0.30730979949270765
```

One can optionally provide a value for the gas constant `R` to match units of one's `Cp`, if necessary.  By default, `sandlermisc` assumes `Cp` has energy units of J.

## Release History

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

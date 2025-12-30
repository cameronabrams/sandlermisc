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

```python
>>> from sandlermisc.gas_consant import GasConstant
R = GasConstant() # J/mol-K
R_pv = GasConstant("bar", "m3") # bar-m3/mol-K
```

## Release History

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

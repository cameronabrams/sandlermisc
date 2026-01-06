from scipy.constants import R # J/mol-K, aka m3-Pa/mol-K

class GasConstant(float):
    """
    Universal gas constant R in (pressure * volume)/(mol * K).
    """

    # base value: J/(mol*K) = Pa*m^3/(mol*K)
    _R_SI = R

    _pressure_units = {
        "pa":   1.0,
        "kpa":  1e-3,
        "mpa":  1e-6,
        "bar":  1e-5,
        "atm":  1.0 / 101325.0,
    }

    _volume_units = {
        "m3":  1.0,
        "l":   1e3,       # 1 m^3 = 1000 L
        "cm3": 1e6,
    }

    def __new__(cls, pressure_unit: str = "pa", volume_unit: str = "m3"):
        p = pressure_unit.lower()
        v = volume_unit.lower()

        if p not in cls._pressure_units:
            raise ValueError(f"Unsupported pressure unit: {pressure_unit}")
        if v not in cls._volume_units:
            raise ValueError(f"Unsupported volume unit: {volume_unit}")

        factor = cls._pressure_units[p] * cls._volume_units[v]
        value = cls._R_SI * factor

        obj = super().__new__(cls, value)
        obj.pressure_unit = p
        obj.volume_unit = v
        obj.factor = factor
        return obj

    def __repr__(self):
        return f"GasConstant({self.pressure_unit!r}, {self.volume_unit!r})"

    def __str__(self):
        return (
            f"{float(self):g} "
            f"({self.pressure_unit}-{self.volume_unit})/(mol-K)"
        )

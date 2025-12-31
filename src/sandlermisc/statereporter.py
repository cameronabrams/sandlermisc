# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Module for reporting state properties in a formatted manner.
"""

def transfer_minus(value: float | str, units: str):
    """ if units start with '-', transfer to value """
    if isinstance(value, str):
        return value, units
    if isinstance(units, str) and units.startswith('-'):
        value = -value
        units = units[1:].strip()
    return value, units

class StateReporter:
    """Class for reporting state properties."""

    def __init__(self, properties: dict = {}):
        self.properties = properties

    def add_property(self, name: str, value: float | str, units: str = '', fstring : str = None):
        value, units = transfer_minus(value, units)
        self.properties[name] = (value, units, fstring)
    
    def add_value_to_property(self, name: str, value: float | str, units: str = '', fstring : str = None):
        value, units = transfer_minus(value, units)
        if name in self.properties:
            current_entry = self.properties[name]
            if isinstance(current_entry, list):
                current_entry.append((value, units, fstring))
                self.properties[name] = current_entry
            else:
                current_entry = [current_entry, (value, units, fstring)]
                self.properties[name] = current_entry
        else:
            self.add_property(name, value, units, fstring)

    def get_value(self, name: str, idx: int = 0):
        """ Get the value of a property by name. """
        entry = self.properties.get(name, None)
        if entry is None:
            return None
        if isinstance(entry, list):
            entry = entry[idx]
            val, _, _ = entry
            return val
        else:
            value, units, _ = entry
            return value

    def pack_Cp(self, Cp: float | list[float] | dict [str, float], fmts: list[str] = ["{:.2f}"]*4):
        """ Pack heat capacity data into the reporter. """
        Tpowers = ['', '^2', '^3', '^4']
        if isinstance(Cp, dict):
            for (key, val), fmt, tp in zip(Cp.items(), fmts, Tpowers):
                self.add_value_to_property(f'Cp{key}', val, f'J/mol-K{tp}', fstring=fmt)
        elif isinstance(Cp, list):
            for key, val, fmt, tp in zip('ABCD', Cp, fmts, Tpowers):
                self.add_value_to_property(f'Cp{key}', val, f'J/mol-K{tp}', fstring=fmt)
        else:
            self.add_property('Cp', Cp, 'J/mol-K', fstring=fmts[0])

    def report(self):
        """
        Return a formatted string report of the state properties.
        """
        if not self.properties:
            return ""
        report_lines = []
        length_of_longest_name = max(len(name) for name in self.properties.keys())
        name_formatter = f"{{:<{length_of_longest_name}}}"
        for name, entry in self.properties.items():
            formatted_name = name_formatter.format(name)
            if isinstance(entry, list):
                line = ''
                for i, (value, units, fstring) in enumerate(entry):
                    if fstring is not None:
                        value = fstring.format(value)
                    if not i:
                        line = f"{formatted_name} = {value} {units}".strip()
                    else:
                        line += f" = {value} {units}"
                report_lines.append(line)
            else:
                value, units, fstring = entry
                if fstring is not None:
                    value = fstring.format(value)
                line = f"{formatted_name} = {value} {units}".strip()
                report_lines.append(line)
        return "\n".join(report_lines)
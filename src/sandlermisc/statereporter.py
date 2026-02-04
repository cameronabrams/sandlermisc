# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Module for reporting state properties in a formatted manner.
"""
import pint

class StateReporter:
    """Class for reporting state properties."""

    def __init__(self, properties: dict = {}):
        self.properties = properties

    def add_property(self, name: str, value: float | str | pint.Quantity, fstring : str = None):
        self.properties[name] = (value, fstring)
    
    def add_value_to_property(self, name: str, value: float | str | pint.Quantity, fstring : str = None):
        if name in self.properties:
            current_entry = self.properties[name]
            if isinstance(current_entry, list):
                current_entry.append((value, fstring))
                self.properties[name] = current_entry
            else:
                current_entry = [current_entry, (value, fstring)]
                self.properties[name] = current_entry
        else:
            self.add_property(name, value, fstring)

    def get_value(self, name: str, idx: int = 0):
        """ Get the value of a property by name. """
        entry = self.properties.get(name, None)
        if entry is None:
            return None
        if isinstance(entry, list):
            entry = entry[idx]
            val, _ = entry
            return val
        else:
            value, fstring = entry
            return value

    def pack_Cp(self, Cp: float | list[float] | dict [str, float], fmts: list[str] = ["{:.2f}"]*4):
        """ Pack heat capacity data into the reporter. """
        Tpowers = ['', '^2', '^3', '^4']
        if isinstance(Cp, dict):
            for (key, val), fmt, tp in zip(Cp.items(), fmts, Tpowers):
                self.add_value_to_property(f'Cp{key}', val, fstring=fmt)
        elif hasattr(Cp, '__len__') and len(Cp) == 4:
            for key, val, fmt, tp in zip('ABCD', Cp, fmts, Tpowers):
                self.add_value_to_property(f'Cp{key}', val, fstring=fmt)
        else:
            self.add_property('Cp', Cp, fstring=fmts[0])

    def report(self, property_notes: dict[str, str] = {}) -> str:
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
                for i, (value, fstring) in enumerate(entry):
                    if fstring is not None:
                        value = fstring.format(value)
                    if not i:
                        line = f"{formatted_name} = {value}".strip()
                    else:
                        line += f" = {value}".strip()
                report_lines.append(line)
            else:
                value, fstring = entry
                if fstring is not None:
                    value = fstring.format(value)
                line = f"{formatted_name} = {value}".strip()
                if name in property_notes:
                    line += " " + property_notes[name]
                report_lines.append(line)
        return "\n".join(report_lines)
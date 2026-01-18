from unittest import TestCase
from sandlermisc.thermals import DeltaH_IG, DeltaS_IG
import pint
ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)

class TestThermals(TestCase):
    def test_default_units(self):
        dh = DeltaH_IG(300, 400, 30)
        self.assertAlmostEqual(dh.magnitude, 3000)
        self.assertEqual(dh.dimensionality, ureg('joule / mole').dimensionality)

        ds = DeltaS_IG(300, 10, 400, 20, 30)
        self.assertAlmostEqual(ds.magnitude, 2.86731585)
        self.assertEqual(ds.dimensionality, ureg('joule / mole / kelvin').dimensionality)
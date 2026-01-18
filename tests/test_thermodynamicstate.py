from unittest import TestCase
from sandlermisc.thermodynamicstate import ThermodynamicState

import pint
ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)

class TestThermodynamicState(TestCase):


    def test_default_units(self):
        state = ThermodynamicState(T=300, P=101325)
        self.assertAlmostEqual(state.T.magnitude, 300)
        self.assertEqual(str(state.T.units), 'kelvin')
        self.assertAlmostEqual(state.P.magnitude, 101325)
        self.assertEqual(str(state.P.units), 'pascal')

    def test_custom_units(self):
        state = ThermodynamicState(T=27 * ureg.degC, P=1 * ureg.atm)
        self.assertAlmostEqual(state.T.magnitude, 300.15, places=2)
        self.assertEqual(str(state.T.units), 'kelvin')
        self.assertAlmostEqual(state.P.magnitude, 101325, places=2)
        self.assertEqual(str(state.P.units), 'pascal')

    def test_mixed_units(self):
        state = ThermodynamicState(T=500 * ureg.K, P=200000)
        self.assertAlmostEqual(state.T.magnitude, 500)
        self.assertEqual(str(state.T.units), 'kelvin')
        self.assertAlmostEqual(state.P.magnitude, 200000)
        self.assertEqual(str(state.P.units), 'pascal')
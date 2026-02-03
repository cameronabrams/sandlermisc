from unittest import TestCase
from sandlermisc.thermodynamicstate import ThermodynamicState, ureg
import logging
logger = logging.getLogger(__name__)

class MyState(ThermodynamicState):
    def resolve(self):
        logger.debug(f'Resolving MyState with T={self.T}, P={self.P}')
        self.resolved = True
        logger.debug(f'MyState cache after resolve: {self._cache}')

class TestThermodynamicState(TestCase):

    def test_default_units(self):
        state = MyState(T=300 * ureg.K, P=101325 * ureg.Pa)
        self.assertTrue('_is_specified' in state._cache)
        self.assertAlmostEqual(state.T.magnitude, 300)
        self.assertEqual(str(state.T.units), 'kelvin')
        self.assertAlmostEqual(state.P.magnitude, 0.101325)
        self.assertEqual(str(state.P.units), 'megapascal')

    def test_custom_units(self):
        state = MyState(T=27 * ureg.degC, P=1 * ureg.atm)
        self.assertAlmostEqual(state.T.magnitude, 300.15, places=2)
        self.assertEqual(str(state.T.units), 'kelvin')
        self.assertAlmostEqual(state.P.magnitude, 0.101325, places=2)
        self.assertEqual(str(state.P.units), 'megapascal')

    def test_mixed_units(self):
        state = MyState(T=500 * ureg.K, P=2 * ureg.bar)
        self.assertAlmostEqual(state.T.magnitude, 500)
        self.assertEqual(str(state.T.units), 'kelvin')
        self.assertAlmostEqual(state.P.magnitude, 0.2)
        self.assertEqual(str(state.P.units), 'megapascal')

class TestThermodynamicStateSimple(TestCase):

    def test_set_attributes(self):
        state = MyState.simple()
        state.T = 350 * ureg.K
        state.P = 5 * ureg.bar
        self.assertAlmostEqual(state.T.magnitude, 350)
        self.assertEqual(str(state.T.units), 'kelvin')
        self.assertAlmostEqual(state.P.magnitude, 0.5)
        self.assertEqual(str(state.P.units), 'megapascal')
        self.assertIsNone(state.h)
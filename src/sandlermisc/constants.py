# Author: Cameron F. Abrams, <cfa22@drexel.edu>

"""
Declares the global pint UnitRegistry and universal gas constant R.
"""

import pint
from scipy.constants import R as R_SI

ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
# below should not be necessary, but just in case
R = R_SI * ureg.J / (ureg.mol * ureg.K)

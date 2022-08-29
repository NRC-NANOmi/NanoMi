import numpy as np
from nanomi_optics.engine.lens_excitation import (
    ur_symmetric, ur_asymmetric, cf_symmetric, cf_asymmetric
)


def test_ur_conversion():
    cf_values = [67.29, 22.94, 39.88]
    ur_values = [
        0.451594826137448, 0.658143283120472, 0.540230594932434
    ]
    ur_calc = []
    ur_calc.append(ur_symmetric(cf_values[0]))
    ur_calc.append(ur_asymmetric(cf_values[1]))
    ur_calc.append(ur_asymmetric(cf_values[2]))

    np.testing.assert_allclose(
        ur_calc,
        ur_values,
        rtol=1e-15,
        atol=1e-15
    )
    cf_values = [6.0, 300.0]
    ur_values = [
        0.999424487508870, 0.252694397536193,
        1.040510306512289, 0.259411378674336
    ]
    ur_calc = []
    ur_calc.append(ur_symmetric(cf_values[0]))
    ur_calc.append(ur_symmetric(cf_values[1]))
    ur_calc.append(ur_asymmetric(cf_values[0]))
    ur_calc.append(ur_asymmetric(cf_values[1]))

    np.testing.assert_allclose(
        ur_calc,
        ur_values,
        rtol=1e-15,
        atol=1e-15
    )


def test_cf_conversion():
    cf_values = [67.29, 22.94, 39.88]
    ur_values = [
        0.451594826137448, 0.658143283120472, 0.540230594932434
    ]
    cf_calc = []
    cf_calc.append(cf_symmetric(ur_values[0]))
    cf_calc.append(cf_asymmetric(ur_values[1]))
    cf_calc.append(cf_asymmetric(ur_values[2]))

    np.testing.assert_allclose(
        cf_calc,
        cf_values,
        rtol=1e-15,
        atol=1e-15
    )
    cf_values = [6.0, 300.0]
    ur_values = [
        0.999424487508870, 0.252694397536193,
        1.040510306512289, 0.259411378674336
    ]
    cf_calc = []
    cf_calc.append(cf_symmetric(ur_values[0]))
    cf_calc.append(cf_symmetric(ur_values[1]))
    cf_calc.append(cf_asymmetric(ur_values[2]))
    cf_calc.append(cf_asymmetric(ur_values[3]))

    np.testing.assert_allclose(
        cf_calc,
        cf_values * 2,
        rtol=1e-13,
        atol=1e-13
    )

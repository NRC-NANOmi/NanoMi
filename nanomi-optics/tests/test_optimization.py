import numpy as np
from nanomi_optics.engine.lens import Lens
from nanomi_optics.engine.optimization import optimize_focal_length

OPTICAL_DISTANCE = 0.00001
LAMBDA_ELECTRON = 0.0112e-6
SCATTERING_ANGLE = LAMBDA_ELECTRON / OPTICAL_DISTANCE

RAYS = [
    np.array([[0], [SCATTERING_ANGLE]]),
    np.array([[OPTICAL_DISTANCE], [SCATTERING_ANGLE]])
]

"""
for the Image optimization, the Scintillator lens
vaccum matrix should have a ray vector with height
as close to zero. These are the height output from
the matlab code
"""
Y_POINTS = [
    -4.0968268138824245894e-12,
    -1.1357412494183741452e-05,
    -0.0026889413214573167424
]

"""
for the Diffraction optimization, the difference between
the vaccum matrix's ray vector height should be close to zero.
These are the height output from the matlab code
"""
Y_POINTS_RED = [
    57.221005454854299899,
    0.39533346627242704763,
    -0.0018439883556115666333
]
Y_POINTS_GREEN = [
    57.218338662064461175,
    0.39326517213370454362,
    -0.0040173071880824067631
]
CF = [19.67, 6.498, 6]
LOCATION = [551.6, 706.4, 826.9]


def create_lenses(focal_length):
    lenses = []
    sample = Lens(528.9, None, None, None)

    for i, cf in enumerate(focal_length):
        lenses.append(
            Lens(
                LOCATION[i],
                cf,
                lenses[-1] if i > 0 else sample,
                3 if i < 2 else 2
            )
        )

    return lenses


def ray_path(rays, lenses):
    results = []
    sc = Lens(972.7, 0, lenses[-1], 1)

    for ray in rays:
        for j, lens in enumerate(lenses):
            if j != 0:
                lens.update_output_plane_location()
            lens.ray_path(
                ray if j == 0 else
                lenses[j - 1].ray_out_lens
            )
        sc.update_output_plane_location()
        sc.ray_path(lenses[-1].ray_out_lens)
        results.append(sc.ray_in_vac[0][0])

    if len(results) == 1:
        return results[0]
    elif len(results) == 2:
        return results[0] - results[1]


def test_ray_path():
    # test Image optimization for Objective lense
    cf = CF.copy()
    cf[0] = optimize_focal_length(
      "Image", 0, LOCATION, cf, RAYS, [True, True, True]
    )
    lenses = create_lenses(cf)
    opt = ray_path([RAYS[0]], lenses)

    assert abs(Y_POINTS[0]) >= abs(opt)

    # test Image optimization for Intermediate lense
    cf = CF.copy()
    cf[1] = optimize_focal_length(
      "Image", 1, LOCATION, cf, RAYS, [True, True, True]
    )
    lenses = create_lenses(cf)
    opt = ray_path([RAYS[0]], lenses)

    assert abs(Y_POINTS[1]) >= abs(opt)

    # test Image optimization for Projective lense
    cf = CF.copy()
    cf[2] = optimize_focal_length(
      "Image", 2, LOCATION, cf, RAYS, [True, True, True]
    )
    lenses = create_lenses(cf)
    opt = ray_path([RAYS[0]], lenses)

    assert abs(Y_POINTS[2]) >= abs(opt)

    # test Diffraction optimization for Objective lense
    cf = CF.copy()
    cf[0] = optimize_focal_length(
      "Diffraction", 0, LOCATION, cf, RAYS, [True, True, True]
    )
    lenses = create_lenses(cf)
    opt = ray_path(RAYS, lenses)

    assert abs(Y_POINTS_GREEN[0] - Y_POINTS_RED[0]) >= abs(opt)

    # test Diffraction optimization for Intermediate lense
    cf = CF.copy()
    cf[1] = optimize_focal_length(
      "Diffraction", 1, LOCATION, cf, RAYS, [True, True, True]
    )
    lenses = create_lenses(cf)
    opt = ray_path(RAYS, lenses)

    assert abs(Y_POINTS_GREEN[1] - Y_POINTS_RED[1]) >= abs(opt)

    # test Diffraction optimization for Projective lense
    cf = CF.copy()
    cf[2] = optimize_focal_length(
      "Diffraction", 2, LOCATION, cf, RAYS, [True, True, True]
    )
    lenses = create_lenses(cf)
    opt = ray_path(RAYS, lenses)

    assert abs(Y_POINTS_GREEN[2] - Y_POINTS_RED[2]) >= abs(opt)

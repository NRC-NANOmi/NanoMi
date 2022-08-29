import numpy as np
from nanomi_optics.engine.lens import Lens

OPTICAL_DISTANCE = 0.00001
LAMBDA_ELECTRON = 0.0112e-6
SCATTERING_ANGLE = LAMBDA_ELECTRON / OPTICAL_DISTANCE

ray = np.array(
    [[0], [SCATTERING_ANGLE]]
)
sample = Lens(528.9, None, None, None)
objective = Lens(551.6, 19.67, sample, 3)
intermediate = Lens(706.4, 6.498, objective, 3)
projective = Lens(826.9, 6, intermediate, 2)
screen = Lens(972.7, None, projective, 1)


def test_ray_path():
    x_points = [
        528.89999999999997726, 551.60000000000002274, 698.96270627062529002
    ]
    y_points = [
        0.0, 0.025424000000000047256,
        -6.9388939039072283776e-18, 0.0
    ]

    sl, el, li, mag = objective.ray_path(ray)
    np.testing.assert_allclose(
        sl,
        [
            [x_points[0], y_points[0]],
            [x_points[1], y_points[1]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        el,
        [
            [x_points[2], y_points[2]],
            [x_points[2], y_points[3]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        li,
        [
            [x_points[1], y_points[1]],
            [x_points[2], y_points[2]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        mag,
        -6.4917491749174001114,
        rtol=1e-8,
        atol=1e-8
    )

    intermediate.update_output_plane_location()
    x_points = [
        551.60000000000002274, 706.39999999999997726, 757.85092865215824531
    ]

    y_points = [
        0.025424000000000047256, -0.0012831316725981922744,
        4.9656459499836103078e-17, 0.0, 5.0306980803327405738e-17
    ]
    sl, el, li, mag = intermediate.ray_path(objective.ray_out_lens)
    np.testing.assert_allclose(
        sl,
        [
            [x_points[0], y_points[0]],
            [x_points[1], y_points[1]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        el,
        [
            [x_points[2], y_points[3]],
            [x_points[2], y_points[4]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        li,
        [
            [x_points[1], y_points[1]],
            [x_points[2], y_points[2]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        mag,
        -6.9179637814955823316,
        rtol=1e-8,
        atol=1e-8
    )

    projective.update_output_plane_location()
    x_points = [
        706.39999999999997726, 826.89999999999997726, 833.47098382625472368
    ]

    y_points = [
        -0.0012831316725981922744, 0.0017220107144984920025,
        0.0, -4.6078592330633938445e-18
    ]

    sl, el, li, mag = projective.ray_path(intermediate.ray_out_lens)
    np.testing.assert_allclose(
        sl,
        [
            [x_points[0], y_points[0]],
            [x_points[1], y_points[1]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        el,
        [
            [x_points[2], y_points[2]],
            [x_points[2], y_points[3]]
        ],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        li,
        [],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        mag,
        -0.095163971042459924443,
        rtol=1e-8,
        atol=1e-8
    )

    screen.update_output_plane_location()
    x_points = [
        826.89999999999997726, 972.70000000000004547
    ]

    y_points = [
        0.0017220107144984920025, -0.036486752054132744194
    ]
    sl, el, li, mag = screen.ray_path(projective.ray_out_lens)

    # only test that passes with atol 1e-14
    np.testing.assert_allclose(
        sl,
        [
            [x_points[0], y_points[0]],
            [x_points[1], y_points[1]]
        ],
        rtol=1e-15,
        atol=1e-14
    )
    np.testing.assert_allclose(
        el,
        [],
        rtol=1e-15,
        atol=1e-15
    )
    np.testing.assert_allclose(
        li,
        [],
        rtol=1e-15,
        atol=1e-15
    )

    assert mag is None

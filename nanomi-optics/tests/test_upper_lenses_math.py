import numpy as np
from nanomi_optics.engine.lens import Lens
CA_DIAMETER = 0.01
CONDENSOR_APERATURE = [192.4, 1.5, 1, [0, 0, 0], 'Cond. Apert']
ray = np.array(
    [[0], [(CA_DIAMETER/2) / CONDENSOR_APERATURE[0]]]
)
c1 = Lens(257.03, 67.29, None, 3)
c2 = Lens(349, 22.94, c1, 3)
c3 = Lens(517, 39.88, c2, 3)


def test_transfer_thin():
    np.testing.assert_allclose(
        c1.transfer_thin_lens(),
        [[1, 0], [-0.014861049190073, 1]],
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        c2.transfer_thin_lens(),
        [[1, 0], [-0.043591979075850, 1]],
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        c3.transfer_thin_lens(),
        [[1, 0], [-0.025075225677031, 1]],
        rtol=1e-8,
        atol=1e-8
    )


def test_thin_lens_matrix():
    ray_out, overall_ray_out, distance, mag = c1.thin_lens_matrix(
        [[0.006679573804574], [0.000025987525988]],
        0
    )
    np.testing.assert_allclose(
        ray_out,
        [[0.006679573804574], [-0.000073277948891]],
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        overall_ray_out,
        [[-0.000000000000004], [-0.000073277948891]],
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        distance,
        91.15394065563403,
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        mag,
        -0.35464319595235593852,
        rtol=1e-8,
        atol=1e-8
    )

    ray_out, overall_ray_out, distance, mag = c2.thin_lens_matrix(
        [[-0.597991549284478], [-0.732779488909672]],
        348.18394065563398954
    )
    np.testing.assert_allclose(
        ray_out,
        [[-0.597991549284478], [-0.706711853805727]],
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        overall_ray_out,
        [[0.000000000000009], [-0.706711853805727]],
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        distance,
        -0.84616034960250274821,
        rtol=1e-8,
        atol=1e-8
    )
    np.testing.assert_allclose(
        mag,
        1.0368858042546862386,
        rtol=1e-8,
        atol=1e-8
    )


def test_ray_path():
    x_points = [
        0, 257.02999999999997272, 348.18394065563398954
    ]
    y_points = [
        0.0, 0.006679573804573804563, 0.0, -4.336808689942017736e-19
    ]

    sl, el, li, mag = c1.ray_path(ray)
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

    c2.update_output_plane_location()
    x_points = [
        257.02999999999997272, 349, 348.15383965039751502
    ]

    y_points = [
        0.006679573804573804563, -5.9799154928447811885e-05,
        0.0, 9.0801931945660996348e-19
    ]
    sl, el, li, mag = c2.ray_path(c1.ray_out_lens)
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

    c3.update_output_plane_location()
    x_points = [
        349, 517, 569.21202877164591882
    ]

    y_points = [
        -5.9799154928447811885e-05, -0.011932558298864670218,
        0.0, 8.6736173798840354721e-19
    ]
    sl, el, li, mag = c3.ray_path(c2.ray_out_lens)
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

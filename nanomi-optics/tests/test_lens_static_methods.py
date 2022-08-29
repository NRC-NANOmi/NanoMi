import numpy as np
from nanomi_optics.engine.lens import Lens


def test_transfer_free():
    np.testing.assert_allclose(
        Lens.transfer_free_space(257.03),
        [[1, 257.03], [0, 1]]
    )
    np.testing.assert_allclose(
        Lens.transfer_free_space(349),
        [[1, 349], [0, 1]]
    )
    np.testing.assert_allclose(
        Lens.transfer_free_space(168),
        [[1, 168], [0, 1]]
    )
    np.testing.assert_allclose(
        Lens.transfer_free_space(13.69253780272917),
        [[1, 13.6925378], [0, 1]]
    )
    np.testing.assert_allclose(
        Lens.transfer_free_space(91.97000000000003),
        [[1, 91.97], [0, 1]]
    )
    np.testing.assert_allclose(
        Lens.transfer_free_space(38.90127388535032),
        [[1, 38.90127389], [0, 1]]
    )


def test_vacuum_matrix():
    ray_out, distance = Lens.vacuum_matrix(
        257.03,
        [[1.5000000e-02], [-2.5987526e-05]]
    )
    np.testing.assert_allclose(
        ray_out,
        [[8.3204262e-03], [-2.5987526e-05]],
        rtol=1e-5
    )
    assert distance == 257.03

    ray_out1, distance1 = Lens.vacuum_matrix(
        13.69253780272917,
        [[0.00832043], [-0.00066602]]
    )
    np.testing.assert_allclose(
        ray_out1,
        [[-0.00079908], [-0.00066602]],
        rtol=1e-5
    )
    assert distance1 == 13.69253780272917

    ray_out2, distance2 = Lens.vacuum_matrix(
        168,
        [[-0.05293346], [0.00084636]]
    )
    np.testing.assert_allclose(
        ray_out2,
        [[0.08925574], [0.00084636]],
        rtol=1e-5
    )
    assert distance2 == 168

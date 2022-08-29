import scipy.optimize
from .lens import Lens


def create_optimizable_funcion(
    mode, lens_i, lens_location, focal_lengths, rays, active
):
    """Creates a cf_function which it will optimize the focal
    length of a lense to get the first ray close to zero
    or the difference between the first two ray close to zero

    Return:
        (func): function to optimize
    """
    def cf_function(x):
        """_summary_

        Args:
            x (float): focal length

        Returns:
            float: output ray or difference between outputs
        """
        sample = Lens(528.9, None, None, None)
        lenses = []
        for i, cf in enumerate(focal_lengths):
            if active[i]:
                lenses.append(
                    Lens(
                        lens_location[i],
                        x[0] if lens_i == i else cf,
                        lenses[-1] if len(lenses) else sample,
                        3 if i < 2 else 2
                    )
                )

        if len(lenses):
            sc = Lens(972.7, 0, lenses[-1], 1)

        if mode == "Image":
            opt_rays = [rays[0]]
        elif mode == "Diffraction":
            opt_rays = [rays[0], rays[1]]
        results = []

        for ray in opt_rays:
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

    return cf_function


def optimize_focal_length(
    mode, lens, lens_locations, focal_lengths, rays, active
):
    """

    Args:
        mode (int): Image optimization
        lens (int): lens index to optimize focal length
        lens_locations (float): lens distance from origin
        focal_lengths (list): list for lens' focal length
        rays (list): list with ray vectors
        active (list): bool list with for active lenses

    Returns:
        float: optimized focal length
    """
    # get function to optimize
    opt_function = create_optimizable_funcion(
        mode, lens, lens_locations, focal_lengths, rays, active
    )

    result = scipy.optimize.least_squares(
        opt_function, focal_lengths[lens], bounds=(6, 300),
        ftol=1e-15, xtol=1e-15, gtol=1e-15
    )
    return result.x[0]

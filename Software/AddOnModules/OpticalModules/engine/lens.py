import numpy as np

ONE_STEP = 1
TWO_STEP = 2
THREE_STEP = 3


class Lens:
    """This class represent the nanomi optics lenses and calculates ray path

    Attributes:
        source_distance: distance from origin
        focal_length: lens focal length in micrometers
        last_lens: lens object of the last lens
        last_lens_location: last lens source distance
        last_lens_distance: last lens distance form actual lens
        last_lens_output_location: last lens output plane location
        type: type of lens
        output_plane_location: image location
    """
    def __init__(
        self, location, focal_length,
        last_lens, type
    ):
        """Init lens object

        Args:
            location: lens location from origin
            focal_length: lens focal length
            last_lens: last lens object
            type: lens type
        """
        self.source_distance = location
        self.focal_length = focal_length
        self.last_lens = last_lens
        if last_lens is None:
            self.last_lens_location = 0
            self.last_lens_distance = self.source_distance
            self.last_lens_output_location = 0
        else:
            self.last_lens_location = last_lens.source_distance
            self.last_lens_distance = self.source_distance \
                - last_lens.source_distance
            self.last_lens_output_location = self.last_lens.source_distance
        self.type = type
        self.output_plane_location = 0

    def __str__(self):
        """return string for print() and str() calls on lens objects"""
        return (
            f"[source_distance={self.source_distance}, "
            f"focal_length = {self.focal_length}, "
            f"last_lens_location = {self.last_lens_location}, "
            f"last_lens_distance = {self.last_lens_distance}, "
            f"last_lens_output_location = {self.last_lens_output_location}, "
            f"type = {self.type}, "
            f"output_plane_location = {self.output_plane_location}]"
        )

    @staticmethod
    def transfer_free_space(distance):
        """calculate transfer matrix for free space

        Return:
            (np.array): transfer matrix
        """
        return np.array([[1, distance], [0, 1]], dtype=float)

    @staticmethod
    def vacuum_matrix(distance, ray_in_vector):
        """method to calculate vacuum matrix

        Args:
            distance = distance in space traveled in micrometers
            ray_in = height IN beam, angle of IN beam

        Returns:
            ray_out (column vector): height OUT-beam and angle of OUT beam
            ditance (float) = distance beam traveled along z in micrometers
        """
        out_beam_vector = np.matmul(
            Lens.transfer_free_space(distance), ray_in_vector
        )
        return out_beam_vector, distance

    # transfer matrix for thin lens
    def transfer_thin_lens(self):
        return np.array([[1, 0], [-1/self.focal_length, 1]], dtype=float)

    # In matlab the location was used to plot the line

    def thin_lens_matrix(self, ray_in, obj_location):
        """
        Args:
            ray_in: [height of IN beam [mm], angle of IN beam [rad]]
            obj_location: location of object [mm] from source

        Return:
            ray_out: height of OUT-beam-at-image, angle of OUT-beam [rad]
            overall_ray_out: height of OUT-beam, angle of OUT-beam [rad]
            distance: lens centre-image distance along z [mm]
            mag_out: magnification image/object
        """

        # locate image z & crossover
        # temporary matrix calculating transfer vacuum to lens, and lens
        temp_matrix = np.matmul(
            self.transfer_thin_lens(),
            self.transfer_free_space(self.source_distance - obj_location)
        )
        distance = -temp_matrix[0, 1]/temp_matrix[1, 1]
        self.output_plane_location = self.source_distance + distance
        overall_ray_out = np.matmul(
            self.transfer_free_space(distance),
            np.matmul(self.transfer_thin_lens(), ray_in)
        )
        ray_out = np.matmul(self.transfer_thin_lens(), ray_in)
        mag_out = 1/temp_matrix[1, 1]

        return ray_out, overall_ray_out, distance, mag_out

    def ray_path(self, ray_vector):
        """calculate the ray path for all types of lens

        Args:
            ray_vector (np.array): ray vector with length and angle

        Returns:
            points_source_to_lens: source to lens line points
            points_effect_of_lens: image output line points
            points_lens_to_image: lens to output line points
            mag_out: lens magnification on image/object
        """
        points_source_to_lens = []
        points_effect_of_lens = []
        points_lens_to_image = []
        mag_out = None

        # step one vacuum matrix
        self.ray_in_vac, ray_in_vac_dist = self.vacuum_matrix(
            self.last_lens_distance, ray_vector
        )
        points_source_to_lens.append(
            (self.last_lens_location, ray_vector[0][0])
        )
        points_source_to_lens.append(
            (self.last_lens_location + ray_in_vac_dist, self.ray_in_vac[0][0])
        )

        if self.type > ONE_STEP:
            # step two thin lens matrix
            self.ray_out_lens, self.overall_ray_out_lens, \
                ray_out_dist, mag_out = self.thin_lens_matrix(
                    self.ray_in_vac, self.last_lens_output_location
                )
            points_effect_of_lens.append(
                (self.output_plane_location, 0.0)
            )
            points_effect_of_lens.append(
                (self.output_plane_location, self.overall_ray_out_lens[0][0])
            )

            if self.type == THREE_STEP:
                # step three, vacuum matrix
                ray_out_vac, ray_out_vac_dist = Lens.vacuum_matrix(
                    ray_out_dist, self.ray_out_lens
                )
                points_lens_to_image.append(
                    (
                        (
                            self.last_lens_location + ray_in_vac_dist,
                            self.ray_in_vac[0][0]
                        )
                    )
                )
                points_lens_to_image.append(
                    (
                        self.source_distance + ray_out_vac_dist,
                        ray_out_vac[0][0]
                    )
                )
        return points_source_to_lens, points_effect_of_lens, \
            points_lens_to_image, mag_out

    def crossover_point_location(self):
        return np.array(
            [self.source_distance + self.focal_length, 0]
        )

    def update_output_plane_location(self):
        """updates the last lens output location for specific ray"""
        if self.last_lens is not None:
            self.last_lens_output_location = \
                self.last_lens.output_plane_location

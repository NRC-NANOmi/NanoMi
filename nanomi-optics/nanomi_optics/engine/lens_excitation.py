def ur_symmetric(focal_l):
    """This function converts the focal length to lens excitation
    for symmetric lenses.

    Args:
        focal_l (float): focal length in micrometers

    Returns:
        float: returns the lens excitation value
    """
    return ((focal_l + 3.723) / 9.709) ** (-1 / 2.503)


def ur_asymmetric(focal_l):
    """This function converts the focal length to lens excitation
    for asymmetric lenses.

    Args:
        focal_l (float): focal length in micrometers

    Returns:
        float: returns the lens excitation value
    """
    return ((focal_l + 0.811) / 7.59) ** (-1 / 2.727)


def cf_symmetric(ur):
    """This function converts the lens excitation to focal length
    for symmetric lenses.

    Args:
        ur (float): lens excitation

    Returns:
        float: returns the focal length in micrometers
    """
    return ((ur ** (2.503 / -1)) * 9.709) - 3.723


def cf_asymmetric(ur):
    """This function converts the lens excitation to focal length
    for asymmetric lenses.

    Args:
        ur (float): lens excitation

    Returns:
        float: returns the focal length in micrometers
    """
    return ((ur ** (2.727 / -1)) * 7.59) - 0.811

import csv


def save_csv(
    f_upper, a_upper, ur, f_lower, a_lower, mag_upper,
    mag_lower, aper, mag, file_path
):
    """this function will save all the results in a
    csv file given the file_path

    Args:
        f_upper (list): focal length for upper lenses
        a_upper (list): active upper lenses
        f_lower (list): focal length for lower lenses
        a_lower (list): active lower lenses
        mag_upper (list): magnification for upper lenses
        mag_lower (list): magnification for lower lenses
        aper (float): Condensor aperature
        mag (float): Scintillator magnification
        file_path (str): file path to save csv file
    """
    data = []
    data.append(["Lenses", "Focal Length", "UR", "Magnification", "Active"])
    for i in range(len(f_upper)):
        data.append([f"C{i + 1}"])
        data[-1].extend(
            [f_upper[i], ur[i], mag_upper[i], a_upper[i]]
         )

    data.append([])
    data.append([])
    data.append(["Lenses", "Focal Length", "Magnification", "Active"])
    lower_lenses = ["Objective", "Intermediate", "Projective"]
    for i in range(len(f_lower)):
        data.append([lower_lenses[i]])
        data[-1].extend(
            [f_lower[i], mag_lower[i], a_lower[i]]
        )

    data.append([])
    data.append([])
    data.append(["Condensor Aperature", "Magnification"])
    data.append([aper, mag])

    with open(file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(data)

import os
import csv
from tempfile import TemporaryDirectory
from nanomi_optics.engine.save_results import save_csv

dirname = os.path.dirname(__file__)
test_filename = os.path.join(dirname, 'resources/test.csv')


def test_csv():
    col_1 = [1, 2, 3]
    col_2 = [4, 5, 6]
    col_3 = [7, 8, 9]
    col_act = [True, False, True]

    test = []
    with open(test_filename, 'r') as csvfile:
        csv_test = csv.reader(csvfile)
        for row in csv_test:
            test.append(row)

    output = []
    with TemporaryDirectory() as tempdir:
        output_filename = os.path.join(tempdir, "output.csv")
        save_csv(
            col_1, col_act, col_2,
            col_1, col_act,
            col_3, col_2, 1,
            2, output_filename
        )
        with open(output_filename, 'r') as csvfile:
            csv_result = csv.reader(csvfile)
            for row in csv_result:
                output.append(row)

    assert test == output

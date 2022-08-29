import subprocess
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


def install():
    # use pip to install the nrcemt package at its current location
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--user", "-e", dir_path
    ])


if __name__ == "__main__":
    try:
        install()
        print("DONE! PRESS ENTER TO EXIT!")
    except subprocess.CalledProcessError as install_error:
        print(install_error)
        print("AN ERROR OCCURED! PRESS ENTER TO EXIT!")
    # wait for user to press enter
    input()

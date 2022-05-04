# NANOmi_Software

## Overview

Code for a microscope in development.

We have only tested the code thus far on Linux (OpenSUSE Tumbleweed), but we are aiming to target any OS.

## Prerequisites

When running the software, clone the repository from GitHub.

Before running NANOmi.py, install the following in your instance of Python:
- PyQt5 (using pip or other methods)
- AIOUSB (install instructions outlined below)

### AIOUSB Library Install (OpenSUSE Tumbleweed)

The proper install instructions can be viewed [here](https://github.com/accesio/AIOUSB). When installing on OpenSUSE Tumblweed, make sure the following packages are installed (using zypper):
- gcc
- gcc-c++
- libusb-1_0-devel

When accessing the AIOUSB directory as required by the install instructions, go to AIOUSB/AIOUSB, then follow the installation guide as usual. 
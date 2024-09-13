# STEM Unit

## STEM unit scanner

## Description
This project is all of the background code to make a scanning transmission electron microscopy (STEM) image generating scanning unit. The general premise is to communicate with a custom-built circuit board to generate two X-Y analog scanning signals, read in up to eight intensity values, correlate those intensities with the X-Y position and form an image which is stored in on-board RAM and then communicated to a computer via USB as soon and as fast as possible.

Applications were designed to interface with nanoMi, the open-source electron microscope. However, this is not the only application that the scanner could see use in. Other forms of microscopy like atomic force microscopy (AFM) could make use of a scanner like this, and so could lithography, and I'm sure there are even more applications that it can be adapted to.

The code included here comes in three parts:

A) VHDL code for the field programmable gate array (FPGA), which is the brain of the custom-built circuit board. The FPGA does all of the legwork of correlating output and input signals, jamming info down into RAM and then withdrawing the information to send it to a connected PC.

B) C shared library code that runs on the host PC and pulls image data out of the FPGA as fast as a computer can. It acts as a go-between for the circuit board and the computer's UI in python. It also does some image marshalling tasks to help speed up image acquisition rates.

C) python code for the user interface. It communicates directly with the C library.

## Installation
A) For VHDL, I used Vivado 2022.2, but a more recent version should be fine. You'll need a JTAG-to-USB cable to talk to the board.

B) The C shared library was coded in VS Code.

C) The version of python I used was 3.12, and I had the following modules installed:
    -pyqt6
    -pyqtgraph
    -numpy

## Usage
The end result is ideally grayscale, 16-bit images of whatever you're trying to image.

## Authors and acknowledgment
This project would not be possible without the contributions from Mohammad Kamal, a co-op student who did all of the background research on simultaneous analog inputs, how to land a RAM chip on a PCB and actually route traces to it, how to design a PCB for high-speed operations and a ton more.

Board layout and the majority of the programming was done by Darren Homeniuk, M.Sc., P.Eng.

Debugging credited to Sophia Cockram, a co-op student who is cleaning the code up considerably.

## Project status
This project is still in progress and testing. I've made a V1.0 of the board, and I'm working on code to run with it.
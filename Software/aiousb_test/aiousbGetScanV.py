# -*- coding: utf-8 -*-
"""
Demonstrate using USB-AIx16-16F and USB-AO16-16E in Python/Linux
"""
from AIOUSB import *

AIOUSB_Init()

diADC = None
diDAC = None

devMask = GetDevices()
boardsFound = 0
for di in range(31):
    if 0 != devMask & (1 << di):
        boardsFound = boardsFound + 1
        status, PID, name, dio, ctrs = QueryDeviceInfo(di)
        status, sn = GetDeviceSerialNumber(di)
        print("Board found at index {0} has deviceID {1:x} = {2}, SN= {3:x} [{4} dio bytes]".format(
            di, PID, name, sn, dio, ctrs))
        if PID == 0x815F:
            diADC = di
        if PID == 0x8071:
            diDAC = di

print("\nAIOUSB Boards found:", boardsFound)

if diADC is not None:
    print("ADC Device is at Index {0}".format(diADC))
    config = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              1, 1, 1, 1, 1, 1, 0, 5, 0xF0, 0, 0x00]
    status = ADC_SetConfig(diADC, config)
    print("ADC_SetConfig status was ", status)
    for i in range(10):
        status, data = ADC_GetScanV(diADC)
        print ("scan #",i,"First channel data was", "{0:1.4f}".format(data[0]), "Volts.  Second channel data was", "{0:1.4f}".format(data[1]), "Volts. 16th channel:", "{0:1.4f}".format(data[15]),"Volts." )


if diDAC is not None:
    print("DAC Device is at Index {0}".format(diDAC))

'''

Piezo Mover USB Interface code.

Runs a simple user interface to communicate with the pizeo mover. USB communications on the computer is the main
way that the piezo mover will operate - the only other ways are via BNC +/- 10V control and the jogging remote.

This module is called by other modules, and wraps the C DLL into python.

Initial Code:       Darren Homeniuk, P.Eng.
Initial Date:       November 16, 2020
*****************************************************************************************************************
Version:            2.0 - December 3, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              FPGA code complete (nearly), USB communications set up, just now small debugging.
*****************************************************************************************************************
Version:            1.0 - November 16, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Set up the initial module to handle interfacing to the main control board via USB.
*****************************************************************************************************************
'''

import sys          #import sys module for system-level functions
import os           #import os module to get paths in operating system native ways
from ctypes import *
import platform
from threading import Timer
import time


#this class handles the main window interactions, mainly initialization
class usbClass():

    #if platform is windows, load files in a windows-manner
    osType = platform.system()


    if platform.system() == 'Windows':
        try:
            # pth = os.path.join(os.getcwd() + '\SLABHIDtoUART.dll')
            # UartLibrary = cdll.LoadLibrary(pth)
            
            # UartLibrary = cdll.LoadLibrary(os.getcwd() + '\SLABHIDtoUART.dll')
            
            # UartLibrary = cdll.LoadLibrary('.\SLABHIDtoUART.dll')
            
            UartLibrary = cdll.LoadLibrary('SLABHIDtoUART.dll')
        except:
            print('failed basic load - ensure SLABHIDtoUART.dll is in the right place.')
    # if platform is Linux, load files in a linux-like manner
    elif osType == 'Linux':

        '''                               OLD
         ___________________________________________________________________________
        |  print('Linux! Not yet supported! Try to write some code for this, eh?')  |
        |                                                                           | #--------------> Just commented out this block on May 31, 2021
        |  UartLibrary = cdll.LoadLibrary('./libslabhidtouart.so')                  |
        |___________________________________________________________________________|     '''


        '''                              NEW
         ___________________________________________________________________________
        |                                                                           |     '''

        #Make sure these .so files are in same directory as the python script
        #FIRST import this
        _ = cdll.LoadLibrary('AddOnModules/LibrariesForPiezoMover/libslabhiddevice.so.1')
        #THEN import this                                                            #---------------> This NEW block replaces the OLD block; created on May 31, 2021
        UartLibrary = cdll.LoadLibrary('AddOnModules/LibrariesForPiezoMover/libslabhidtouart.so')

        '''

        |___________________________________________________________________________|    '''



    usbDevice = None
    receiveTimer = None
    stopTheTimer = False
    disconnectRequest = False
    writeLock = False
    readLock = False
    timerIsStopped = False
    haveNewData = False
    readValue = ''
    haveNewConnections = False
    readContinue = False
    FPGAs = []
    #this dictionary contains the error codes for the UART-to-USB functions (UartLibrary)
    dictValues =[   (1, 'Device not found.'),
                    (2, 'Invalid handle.'),
                    (3, 'Invalid device object.'),
                    (4, 'Invalid parameter.'),
                    (5, 'Invalid request length.'),
                    (16, 'UART Read error.'),
                    (17, 'UART Write error.'),
                    (18, 'UART Read timed out.'),
                    (19, 'UART Write timed out.'),
                    (20, 'Device IO failed.'),
                    (21, 'Device access error.'),
                    (22, 'Device not supported.'),
                    (255, 'Unknown error! Huh...')
                ]
    ErrorDictionary = dict(dictValues)
    # newData = pyqtSignal()
    
    #called manually after instantiation, starts checking USB connection possibilities
    def init(self):
        self.connectTimer = Timer(1, self.checkConnections, args=(self,))
        self.connectTimer.start()
    
    #function to routinely poll the USB connections, looking for FPGAs to connect with
    def checkConnections(self):
        self.readLock = True
        #format the variables as ctypes for the DLL call
        numDevices = (c_long)()
        self.UartLibrary.HidUart_GetNumDevices(byref(numDevices), 0x10C4, 0xEA80)
        #list of FPGAs found (with vendor ID 0x10C4 and product ID 0xEA80) this scan
        thisRoundFPGAs = []
        #add found devices to the scan by their serial number
        for i in range(0,numDevices.value):
            deviceStr = create_string_buffer(512)
            self.UartLibrary.HidUart_GetString(i, 0x10C4, 0xEA80, byref(deviceStr), 0x04)
            thisRoundFPGAs.append((deviceStr.value).decode('ascii'))
        #if the total length of currently found FPGAs doesn't match up with previously found ones, update
        if not (len(thisRoundFPGAs) == len(self.FPGAs)):
            self.FPGAs = thisRoundFPGAs
            self.haveNewConnections = True
        #restart the timer because it doesn't automatically restart for you (huh?)
        if self.stopTheTimer == False:
            self.connectTimer = Timer(0.1, self.checkConnections, args=(self,))
            self.connectTimer.start()
        else:
            self.connectTimer = None
        self.readLock = False




    #function to connect to the FPGA via USB-to-UART conversion
    def connectUsb(self, index):
        #if a usb device has not been connected, try to connect
        if self.usbDevice == None:
            #if the device index is -1, then there were no found devices, so we can't connect
            if index < 0:
                print('Inappropriate device index.')
                return 65535
            #attempt to open the USB-to-UART bridge device
            deviceNum = (c_long)(index)
            self.usbDevice = (c_void_p)()
            retVal = self.UartLibrary.HidUart_Open(byref(self.usbDevice), deviceNum,  0x10C4, 0xEA80) # <------------------------------------------------------ THIS IS THE PROBLEM I BELIEVE

            if retVal > 0:
                print('Connection failed. Error code ' + str(retVal) + ': ' + str(self.ErrorDictionary.get(retVal)))
                self.usbDevice = None

                return retVal
            
            #set up the UART communication - Baud rate, stop bits, etc
            # baudRate = (c_long)(230400)
            baudRate = (c_long)(1000000)
            # HidUart_SetUartConfig(device, baudRate, dataBits, parity, stopBits, flowControl)
            #dataBits, parity, stopBits, flowControl are all BYTE values, formed as a look up table
            #check the manual, but I've set them here to:
            #   230,400 baud, 8 data bits, no parity, 1 stop bit, no flow control
            if self.UartLibrary.HidUart_SetUartConfig(self.usbDevice, baudRate, 0x03, 0x00, 0x00, 0x00) > 0:
                print('Could not configure UART.')
                self.UartLibrary.HidUart_Close(self.usbDevice)
                self.usbDevice = None
                return 65534
                    
            #set timeouts to 5 ms (1/200 of a second) from a default value of 1 second, which is uber long
            readTimeout = (c_long)(5)
            writeTimeout = (c_long)(5)
            if self.UartLibrary.HidUart_SetTimeouts(self.usbDevice, readTimeout, writeTimeout) > 0:
                print('Could not configure timeouts')
                self.UartLibrary.HidUart_Close(self.usbDevice)
                self.usbDevice = None
                return 65533
            
            #set the UART communication on, which will flush the buffer as an initialization operation
            if self.UartLibrary.HidUart_SetUartEnable(self.usbDevice, True) > 0:
                print('Could not turn UART on.')
                self.UartLibrary.HidUart_Close(self.usbDevice)
                self.usbDevice = None
                return 65532
            
            #flush the buffers initially
            if self.UartLibrary.HidUart_FlushBuffers(self.usbDevice, True, True) > 0:
                print('Could not flush buffers')
                self.UartLibrary.HidUart_Close(self.usbDevice)
                self.usbDevice = None
                return 65531
            
            #start the timer for receiving checks - constantly checks the receive buffer
            self.restartTimer(self)
            
            return 0
    


    #function to set parameters in the FPGA - sent as "xxByyyyyyF"
    def set(self, register, setValue):
        self.readLock = True
        while self.writeLock:
            pass
        self.writeLock = True
        #please ensure value sent into register is an INTEGER variable.
        if type(register).__name__ != 'int':
            print('Incorrect format for register. Ensure it is an integer.')
            print('Register is type "' + type(register).__name__ + '".')
            return
        #determine the number of digits in the value to be sent for setting
        strValue = str(setValue)
        res = setValue
        digits = 0
        while res >= 1:
            res = res / 10
            digits = digits + 1
        if digits == 0:
            digits = 1
        #set up the first three nibbles of the write value, "xxB"
        # xx is the register to set
        # B is the operation, aka "set"
        writeValue = (register<<4 | 0xB)
        #add the value nibbles after that, one-by-one
        for n in range(0, digits):
            writeValue = (writeValue<<4 | int(strValue[n]))
        #finish the write value off with an "F" to signify end-of-transmission
        writeValue = writeValue<<4 | 0xF
        #if digits aren't even, add one to keep correct byte spacing, and add a zero at the end of the string
        if digits % 2 != 0:
            digits = digits + 1
            writeValue = writeValue<<4 | 0x0
        #determine the number of bytes in the string
        bytes = int((digits/2)+2)
        #format the variables as ctypes for the DLL call
        writeBuffer = create_string_buffer(writeValue.to_bytes(bytes,byteorder='big'))
        bytesToWrite = (c_long)(bytes)
        bytesWritten = (c_long)()
        #write the set request to the FPGA
        self.UartLibrary.HidUart_Write(self.usbDevice, byref(writeBuffer), bytesToWrite, byref(bytesWritten))

        self.writeLock = False
        self.readLock = False

        
    #function to request polling - usually only sent once
    def poll(self):
        self.readLock = True
        while self.writeLock:
            pass
        self.writeLock = True
        #Polling is different - this string gets sent once, and the FPGA feeds back a long string of values
        #when received and converted, another poll request is made
        #format the variables as ctypes for the DLL call
        writeBuffer = create_string_buffer((0xCF).to_bytes(1,byteorder='big'))
        bytesToWrite = (c_long)(1)
        bytesWritten = (c_long)()
        #request polling - if this is never sent, polling does not start
        self.UartLibrary.HidUart_Write(self.usbDevice, byref(writeBuffer), bytesToWrite, byref(bytesWritten))
        self.writeLock = False
        self.readLock = False
        
    #function to receive bytes from the FPGA via UART-to-USB conversion
    def receive(self):
        #only run here if there is no new data to be read - otherwise we might be overwriting the data our parent program might be reading
        if self.haveNewData == False:
            #format the variables as ctypes for the DLL call
            readBuffer = create_string_buffer(512)
            numBytesToRead = (c_long)(512)
            numBytesRead = (c_long)()

            while self.readLock:
                pass
            self.writeLock = True
            #the bytes that were read are contained in the readBuffer, as it is by reference
            self.UartLibrary.HidUart_Read(self.usbDevice, byref(readBuffer), numBytesToRead, byref(numBytesRead))
            #define a string to hold the decoded read value
            if self.readContinue == False:
                self.readValue = ''
            #to byte-by-byte and decode each byte into a string equivalent
            for i in range(0, numBytesRead.value):
                self.readValue = self.readValue + str(readBuffer[i:i+1].hex())
            #if bytes were read, then trigger the calling software to look in "self.readValue"
            if numBytesRead.value > 0:
                #if last character read is an "f", then the read is complete, so trigger new data
                if self.readValue[-1].lower() == 'f':
                    self.readContinue = False
                    self.haveNewData = True
                    # self.newData.emit()
                #if last character is not an 'f', then continue reading until you see an 'f'
                else:
                    self.readContinue = True

        self.writeLock = False
        #restart the read timer because it doesn't keep going for us (!!)
        self.restartTimer(self)
    
    #function to restart the receive timer unless shutdown has been started
    def restartTimer(self):
        while self.readLock:
            pass
        #start checking the receive buffer every 100ms
        if self.stopTheTimer == False and self.disconnectRequest == False:
            self.receiveTimer = Timer(0.100, self.receive, args=(self,))
            self.receiveTimer.start()
        else:
            #closing the software, disconnect from USB
            self.UartLibrary.HidUart_Close(self.usbDevice)
            self.usbDevice = None
            self.disconnectRequest = False
            self.readContinue = False
            self.readValue = ''
    
    #function called when the calling software is closing, and it turns off the timers
    def closing(self):
        self.stopTheTimer = True

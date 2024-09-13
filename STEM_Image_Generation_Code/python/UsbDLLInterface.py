'''

STEM Scanner USB Interface code via a C DLL for 245 FIFO Asynchronous protocol.

This module will handle all communications with the FPGA and hold onto current data in it, so that the UI can simply
call for data in a generic fashion and the usb module will handle it.

This module is called by other modules.

Initial Code:       Darren Homeniuk, P.Eng.
Initial Date:       August 25, 2023
*****************************************************************************************************************
Version:            1.0 - August 25, 2023
By:                 Darren Homeniuk, P.Eng.
Notes:              Set up the initial module to handle interfacing to the main control board via USB.
*****************************************************************************************************************
Version:            1.2 - February 14, 2024
By:                 Darren Homeniuk, P.Eng.
Notes:              After working on other USB projects in python, I realized this one was quite messy. I made
                    the UI handle only UI-type things and offloaded the usb communications purely to the USB
                    module. Also, a signals class now handles most of the work that timers handled before.
*****************************************************************************************************************
Version:            1.4 - February 19, 2024
By:                 Darren Homeniuk, P.Eng.
Notes:              Code is functional on a basic level, and so is the HDL code, so version 1.3 was born. Version
                    1.4 adds a randomized scan, where python sends the FPGA a ton of randomized coordinates which
                    get saved to RAM, and then the FPGA reads through those coordinates to make an image.
*****************************************************************************************************************
Version:            1.5 - March 1, 2024
By:                 Darren Homeniuk, P.Eng.
Notes:              Swapping from multiple bit-arrays in HDL code to FIFO operations. Will be more efficient.
                    Shouldn't need much python changes, hopefully.
*****************************************************************************************************************
Version:            1.6 - March 7, 2024
By:                 Darren Homeniuk, P.Eng.
Notes:              Targeting the USB mode 245 Asynchronous FIFO as opposed to the previously used RS232.
*****************************************************************************************************************
'''

import sys          #import sys module for system-level functions
import os           #import os module to get paths in operating system native ways
import platform
from threading import Timer
from threading import Thread
from ctypes import *
import numpy as np
import random
import time
from PyQt6.QtCore import *

#--------------------------------------------------------------------------------------------------------------------------
#this class handles the main window interactions, mainly initialization
class UsbClass():
        
    FPGA = None
    closing = False
    
    connectTimer = None
    readTimer = None
    
    imageData = np.array(np.zeros((2048, 2048), dtype=np.uint16))
    displayData = np.array(np.zeros((2048, 2048), dtype=np.uint8))
    
    #current status variables for the scan acquisition. These default values will be overwritten on FPGA connection, so they're just placeholders and examples
    mode = 1                #mode of the acquisition, range 0<->7: 0=idle, 1=raster scan, 2=raster single image, 3=random scan, 4=random single image, 5=fixed output voltage, 6=testing mode
    integrationTime = 0           #integer value, range 0<->16, where 2^(integrationTime) * 40ns = actual integration time
    pixelWaitTime = 12      #wait time to allow the beam to get to the next incremental pixel; range 0<->500000, multiples of 40ns per value. So a value of 25 is actually a wait of 1000ns
    lineFlybackTime = 125   #line flyback time from going from the end of a line to the first pixel in the next line, range 0<->500000, multiples of 40ns per value
    imageSize = 2048  #total pixels on one side of the image - square images only - range 8<->4096 in powers of 2 (i.e. 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)

    acquire = 0
    
    pixelStep = 1           #step size, used to determine pixel xy locations when counts come back from the FPGA
    
    timerTrigger = False
    t1 = None
    
    #called manually after instantiation, starts checking USB connection possibilities
    def initialize(self):
        dllPath = os.getcwd()
        self.FPGA = CDLL(dllPath + '\\STEM.dll')
        if type(self.FPGA) == type(None):
            print('Failed to load the dll. Bye!')
        
        #define the argument types and return types of all c-type functions in the DLL
        self.FPGA.initUSB.argtypes = ()
        self.FPGA.initUSB.restype = c_uint32
        
        self.FPGA.getConnected.argtypes = ()
        self.FPGA.getConnected.restype = c_bool
        
        self.FPGA.connectUSB.argtypes = (c_uint32, c_uint32)
        self.FPGA.connectUSB.restype = c_uint32
        
        self.FPGA.rxUSB.argtypes = ()
        self.FPGA.rxUSB.restype = None
        
        self.FPGA.getSetMode.argtypes = (c_int32,)
        self.FPGA.getSetMode.restype = c_int32
        
        self.FPGA.getSetDoneImage.argtypes = (c_int32,)
        self.FPGA.getSetDoneImage.restype = c_bool
        
        self.FPGA.getSetIntegrationTime.argtypes = (c_int32,)
        self.FPGA.getSetIntegrationTime.restype = c_int32
        
        self.FPGA.getSetLineFlybackTime.argtypes = (c_int32,)
        self.FPGA.getSetLineFlybackTime.restype = c_int32
        
        self.FPGA.getSetImageSize.argtypes = (c_int32,)
        self.FPGA.getSetImageSize.restype = c_int32
        
        self.FPGA.getSetPixelWaitTime.argtypes = (c_int32,)
        self.FPGA.getSetPixelWaitTime.restype = c_int32
        
        self.FPGA.getImage.argtypes = (c_void_p,)
        self.FPGA.getImage.restype = None           #really unsure about this one and how it'll work
        
        self.FPGA.closingUSB.argtypes = ()
        self.FPGA.closingUSB.restype = None
        
        self.FPGA.setRun.argtypes = (c_bool,)
        self.FPGA.setRun.restype = None
        
        self.FPGA.initUSB()
        
        self.signals = signalClass()
        self.connectTimer = Timer(1, self.checkConnections, args=(self,))
        self.connectTimer.start()
    
    #----------------------------------------------------------------------------------------------------------------------
    # function to routinely poll the USB connections, looking for FPGAs to connect with
    def checkConnections(self):
        # if no connections have been found
        if self.FPGA.getConnected() == False:
            if self.FPGA.connectUSB(500, 500) == 0:         #connectUSB has two arguments, the tx and rx timeouts
                
                #if we are here, we returned 0 (success!) so check out the current FPGA values on lots of things
                triggerFPGA = Thread(target=self.FPGA.rxUSB, args=())
                triggerFPGA.start()
                self.signals.fpgaConnected.emit()
                
                #query for current mode
                temp = self.FPGA.getSetMode(-1)
                if temp >= 0:
                    self.mode = temp
                    self.signals.modeUpdate.emit()
                else:
                    print('Mode request during boot-up failed with code ' + str(temp))
                
                #query for current integration time
                temp = self.FPGA.getSetIntegrationTime(-1)
                if temp >= 0:
                    self.integrationTime = temp
                    self.signals.integrationUpdate.emit()
                else:
                    print('Integration time request on boot-up failed with code ' + str(temp))
                
                #query for current pixel wait time
                temp = self.FPGA.getSetPixelWaitTime(-1)
                if temp >= 0:
                    self.pixelWaitTime = temp
                    self.signals.pixelMoveUpdate.emit()
                else:
                    print('Pixel wait time request on boot-up failed with code ' + str(temp))
                
                #query for current line flyback time
                temp = self.FPGA.getSetLineFlybackTime(-1)
                if temp >= 0:
                    self.lineFlybackTime = temp
                    self.signals.lineFlybackUpdate.emit()
                else:
                    print('Line flyback time request on boot-up failed with code ' + str(temp))
                
                # query for current image size
                temp = self.FPGA.getSetImageSize(-1)
                if temp >= 0:
                    self.imageSize = temp
                    self.signals.imageSizeUpdate.emit()
                else:
                    print('Image size request on boot-up failed with code ' + str(temp))
                    
                self.readTimer = Timer(0.1, self.readData, args=(self,))
                self.readTimer.start()
                return

        #if no communications were found, restart the timer to try again
        self.connectTimer = Timer(1, self.checkConnections, args=(self,))
        self.connectTimer.start()
    
    #----------------------------------------------------------------------------------------------------------------------
    #function to set the integration time on a specific pixel, how many samples to integrate basically (2^integrationTime = samples to integrate)
    def setIntegration(self, value):
        self.integrationTime = value
        self.FPGA.getSetIntegrationTime(value)
        print('updated integration time to combobox index ' + str(self.integrationTime))
    #----------------------------------------------------------------------------------------------------------------------
    #function to set the wait time for a pixel to allow for the beam to arrive at the next pixel
    def setPixelMoveDelay(self, value):
        self.pixelWaitTime = value
        self.FPGA.getSetPixelWaitTime(value)
        print('updated pixel move delay to ' + str(self.pixelWaitTime))
    #----------------------------------------------------------------------------------------------------------------------
    #function to set the delay time to allow for the beam to get back to the other side of the image
    def setLineMoveDelay(self, value):
        self.lineFlybackTime = value
        self.FPGA.getSetLineFlybackTime(value)
        print('updated line flyback time to ' + str(self.lineFlybackTime))
    #----------------------------------------------------------------------------------------------------------------------
    #function to set the count of pixels in the usb module and the FPGA simultaneously
    def setPixels(self, value):
        self.imageSize = value
        self.FPGA.getSetImageSize(value)
        self.imageData = np.array(np.zeros((self.imageSize, self.imageSize), dtype=np.uint16))
        self.displayData = np.array(np.zeros((self.imageSize, self.imageSize), dtype=np.uint8))
        print('updating image size to ' + str(self.imageSize) + ' x ' + str(self.imageSize))
    #----------------------------------------------------------------------------------------------------------------------
    #function to set the mode in the FPGA
    def setMode(self, value):
        self.mode = value
        self.FPGA.getSetMode(value)
        print('updated mode to ' + str(self.mode))
    #----------------------------------------------------------------------------------------------------------------------
    #function to turn the acquisition on or off
    def setRun(self, value):
        #on stopping an image (also happens before starting) clear out the FPGA buffer completely
        if value == 0:
            self.timerTrigger = False
        elif self.timerTrigger == False:
            self.timerTrigger = True
            self.t1 = time.time()
        #define the pixel step size for raster scan images
        self.pixelStep = int(65535/(self.imageSize-1))
        #if starting a run in random scan mode, generate an appropriate matrix of random x-y coordinates
        if  value == 1 and (self.mode == 3 or self.mode == 4):
            self.generateRandoms(self)
        self.FPGA.setRun(value)
        self.acquire = value
    
    #----------------------------------------------------------------------------------------------------------------------
    #function to generate the random matrix scans
    def generateRandoms(self):
        
        # #make a master list of indexed pixels possible in an image. In an 8x8 image, there are 64 pixels (0-indexed).
        # #   So pixel 5 would be x=0, y=5 and pixel 62 would be x=7, y=6 etc 
        # pixels = []
        # pixels.extend([j for j in range(0, self.imageSize*self.imageSize)])
        # #shuffle this master list to ensure we don't get duplicate values
        # random.shuffle(pixels)
        
        # #generate a list of all possible x coordinates in the image
        # xValues = []
        # for i in range(0, self.imageSize):
            # xValues.extend([j for j in range(0, self.imageSize)])
        # #scale the pixel integers into counts
        # for i in range(0, len(xValues)):
            # xValues[i] = int(xValues[i]*self.pixelStep)

        # #generate a list of all possible y coordinates in the image
        # yValues = []
        # for i in range(0, self.imageSize):
            # yValues.extend([i]*self.imageSize)
        # #scale the pixel integers into counts
        # for i in range(0, len(yValues)):
            # yValues[i] = int(yValues[i]*self.pixelStep)
        
        # #read out the x and y list from the randomized master list
        # self.xPix = []
        # self.yPix = []
        # for i in range(0, len(pixels)):
            # self.xPix.extend([xValues[pixels[i]]])
            # self.yPix.extend([yValues[pixels[i]]])
        
        # print('X pixels: ', end='')
        # print(self.xPix)
        # print('Y pixels: ', end='')
        # print(self.yPix)
        
        # #transmit all the data to the FPGA. X first, Y second
        # print('Sending FPGA random data')
        # for i in range(0, len(self.xPix)):
            # self.set(self, self.randomXRegister, self.xPix[i])
            # self.set(self, self.randomYRegister, self.yPix[i])
        # print('Finished sending random data, now acquiring')
        print('Not supported yet')
        
    #----------------------------------------------------------------------------------------------------------------------
    #function to read image data back from the FPGA
    def readData(self):
        if self.closing == True:
            return
        #if we are running, look for new image data
        if self.acquire == 1:
            tempImage = np.ctypeslib.as_array((c_ushort * 4096 * 4096).in_dll(self.FPGA, 'image'))
            # temp = np.zeros(shape=(4096, 4096), dtype=np.uint16)
            # temp.ctypes.data_as(c_void_p)
            # self.FPGA.getImage(byref(temp))
            # tempImage = np.ctypeslib.as_array(self.FPGA.getImage())
            self.imageData = tempImage[0:self.imageSize, 0:self.imageSize]
            div = 256 * np.ones(self.imageSize)
            self.displayData = np.array(self.imageData / div, dtype=np.uint8)
            self.signals.newImageData.emit(self.displayData)
            
        #check to see if the image data complete, and if so stop the run
        if self.FPGA.getSetDoneImage(-1) == True:
            self.signals.newImageData.emit(self.displayData)
            self.signals.imageDataComplete.emit()
            self.FPGA.getSetDoneImage(0)
            self.acquire = 0
            self.timerTrigger = False
            print('time to aquire the image: ' + str(round(time.time() - self.t1,4)) + ' seconds.')
                        
        self.readTimer = Timer(0.001, self.readData, args=(self,))
        self.readTimer.start()
    
    #----------------------------------------------------------------------------------------------------------------------
    #function called when the calling software is closing, and it turns off the timers
    def closing(self):
        self.closing = True
        if not self.FPGA == None:
            self.readTimer = None
            self.FPGA.closingUSB()
            self.FPGA = None
            
#----------------------------------------------------------------------------------------------------------------------
#this class is for signal handling. Signals will be thrown when new data arrives and it will trigger an update on the UI
class signalClass(QObject):
    modeUpdate = pyqtSignal()
    integrationUpdate = pyqtSignal()
    lineFlybackUpdate = pyqtSignal()
    imageSizeUpdate = pyqtSignal()
    pixelMoveUpdate = pyqtSignal()
    newImageData = pyqtSignal(np.ndarray)
    imageDataComplete = pyqtSignal()
    fpgaConnected = pyqtSignal()
    fpgaDisconnected = pyqtSignal()
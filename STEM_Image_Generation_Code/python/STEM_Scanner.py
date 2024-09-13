'''

STEM Scanner User Interface code.

Runs a simple user interface to communicate with the STEM unit via a selected USB module.

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

import sys
from UsbDLLInterface import UsbClass
from UsbDLLInterface import signalClass
import numpy as np
import time
import pyqtgraph

#import the necessary aspects of PyQt6 for this user interface window
from PyQt6.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QGridLayout, QComboBox, QLineEdit, QGroupBox, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QRadioButton, QCheckBox, QSlider, QSpinBox, QFileDialog
from PyQt6.QtCore import *
from PyQt6.QtGui import *

#this class handles the main window interactions, mainly initialization
class MainWindow(QWidget):
    
    usb = None                  #a holder for the usb connection module
    closing = False             #tells if the UI is closing or not
    enables = []                #a group of UI objects that are enabled once the FPGA connects
    invertedEnables = []        #a group of UI objects that are disabled on running
    initFromFPGA = False        #a status variable that tells if the UI has connected to the FPGA or not
    pixmap = None               #a variable that holds the current pixel-map of the image; None if uninitialized
    leftClickPos = None         #a variable that holds the last left-click position while over the image for line profiling
    horizontalPixel = None      #a variable that holds a pixel rendition of the horizontal line
    rightClickPos = None        #a variable that holds the last right-click position while over the image for line profiling
    verticalPixel = None        #a variable that holds a pixel rendition of the vertical line
    
    
    #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()

    #function to create the user interface, and load in external modules for equipment control
    def initUI(self):
        
        #define a font for the title of the UI
        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(12)
        
        #define a font for the buttons of the UI
        buttonFont = QFont()
        buttonFont.setBold(False)
        buttonFont.setPointSize(10)
        
        boldButtonFont = QFont()
        boldButtonFont.setBold(True)
        boldButtonFont.setPointSize(12)
        
        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 1200
        windowHeight = 800
        self.setGeometry(50, 50, windowWidth, windowHeight)
        # self.setStyleSheet("background-color: darkgray;")
        self.setMinimumSize(windowWidth, windowHeight)
        
        #number of columns on main inputs
        col = 12
        
        #name the window
        self.setWindowTitle('STEM Scanner Interface')
        
        #determine the grid pattern
        mainGrid = QGridLayout()
        mainGrid.setSpacing(10)
        mainGrid.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        #current row tracker to avoid a lot of rework when things move around
        r = 0
        
        #create a label at the top of the window so we know what the software does
        topTextLabel = QLabel('STEM Scanner Interface', self)
        topTextLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topTextLabel.setWordWrap(True)
        topTextLabel.setFont(titleFont)
        mainGrid.addWidget(topTextLabel, r, 0, 1, col)
        r += 1
        
        self.connectText = QLabel('USB: Disconnected', self)
        self.connectText.setFont(boldButtonFont)
        self.connectText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainGrid.addWidget(self.connectText, r, 0, 1, 3)
        r += 1
        
        #-------------------------------------------------------------
        #Operation Mode Radio group
        #-------------------------------------------------------------
        
        #mainGrid.addWidget(deviceName, row, col, rowSpan, colSpan)
        
        self.radioGroup = QGroupBox("Mode Selection")
        self.radioGroup.setFont(titleFont)
        self.radioGroup.setCheckable(False)
        self.radioGroup.setEnabled(False)
        self.enables.append(self.radioGroup)
        self.radioGroup.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainGrid.addWidget(self.radioGroup, r, 0, 4, 3)
        r += 4
        
        self.vbox = QVBoxLayout()
        self.radioGroup.setLayout(self.vbox)
        
        self.rasterScanRadio = QRadioButton('Continuous Scanning - Raster')
        self.rasterScanRadio.setFont(buttonFont)
        self.rasterScanRadio.setToolTip("This mode continuously scans the image area in a smooth linear raster scan pattern, horizontal line by horizontal line.")
        self.rasterScanRadio.clicked.connect(lambda: self.uiModeChanged(1))
        self.vbox.addWidget(self.rasterScanRadio)
        
        self.rasterImageRadio = QRadioButton('Single Image - Raster')
        self.rasterImageRadio.setFont(buttonFont)
        self.rasterImageRadio.setToolTip("This mode takes a single image of the image area in a smooth linear raster scan pattern, horizontal line by horizontal line.")
        self.rasterImageRadio.clicked.connect(lambda: self.uiModeChanged(2))
        self.vbox.addWidget(self.rasterImageRadio)
        
        self.randomScanRadio = QRadioButton('Scanning - Random')
        self.randomScanRadio.setFont(buttonFont)
        self.randomScanRadio.setToolTip("This mode continuously scans the image area in a random pattern, pixel by pixel.")
        self.randomScanRadio.clicked.connect(lambda: self.uiModeChanged(3))
        self.vbox.addWidget(self.randomScanRadio)
   
        self.randomImageRadio = QRadioButton('Single Image - Random')
        self.randomImageRadio.setFont(buttonFont)
        self.randomImageRadio.setToolTip("This mode takes a single image of hte image area in a random pattern, pixel by pixel.")
        self.randomImageRadio.clicked.connect(lambda: self.uiModeChanged(4))
        self.vbox.addWidget(self.randomImageRadio)
        
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        mainGrid.addItem(self.spacer, r, 0, 1, 3)
        r += 1
        
        #-------------------------------------------------------------
        #Settings (set and get)
        #-------------------------------------------------------------
        
        #SAMPLE TIME, AMOUNT OF SAMPLES TO ACQUIRE PER PIXEL
        integrationLabel = QLabel('Sampling integration time: ')
        integrationLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        integrationLabel.setToolTip("The integration time is how long the beam holds on any given pixel. \nSamples are taken over 20ns while integrationing at a pixel, and for integrations longer than 20ns an average is computed for the final value. \nHardware division is messy unless it is by 2^N (where N is an integer) which is just simple bit-shifting, so inputs have been limited to these specific values.")
        integrationLabel.setFont(titleFont)
        mainGrid.addWidget(integrationLabel, r, 0, 1, 3)
        r += 1
        
        self.integrationCycles = QComboBox()
        self.integrationCycles.addItem('40 ns, or 1 sample per pixel')
        self.integrationCycles.addItem('80 ns, or 2 samples per pixel')
        self.integrationCycles.addItem('160 ns, or 4 samples per pixel')
        self.integrationCycles.addItem('320 ns, or 8 samples per pixel')
        self.integrationCycles.addItem('640 ns, or 16 samples per pixel')
        self.integrationCycles.addItem('1.28 us, or 32 samples per pixel')
        self.integrationCycles.addItem('2.56 us, or 64 samples per pixel')
        self.integrationCycles.addItem('5.12 us, or 128 samples per pixel')
        self.integrationCycles.addItem('10.24 us, or 256 samples per pixel')
        self.integrationCycles.addItem('20.48 us, or 512 samples per pixel')
        self.integrationCycles.addItem('40.96 us, or 1024 samples per pixel')
        self.integrationCycles.addItem('81.92 us, or 2048 samples per pixel')
        self.integrationCycles.addItem('163.84 us, or 4096 samples per pixel')
        self.integrationCycles.addItem('327.68 us, or 8192 samples per pixel')
        self.integrationCycles.addItem('655.36 us, or 16384 samples per pixel')
        self.integrationCycles.addItem('1.3107 us, or 32768 samples per pixel')
        self.integrationCycles.addItem('2.6214 ms, or 65536 samples per pixel')
        self.integrationCycles.setToolTip("The integration time is how long the beam holds on any given pixel. \nSamples are taken over 20ns while integrationing at a pixel, and for integrations longer than 20ns an average is computed for the final value. \nHardware division is messy unless it is by 2^N (where N is an integer) which is just simple bit-shifting, so inputs have been limited to these specific values.")
        self.integrationCycles.setFont(buttonFont)
        self.integrationCycles.setEnabled(False)
        self.enables.append(self.integrationCycles)
        self.integrationCycles.currentIndexChanged.connect(self.uiIntegrationIndexChanged)
        mainGrid.addWidget(self.integrationCycles, r, 0, 1, 3)
        r += 1
        
        mainGrid.addItem(self.spacer, r, 0, 1, 3)
        r += 1
        
        #PIXEL WAIT TIME, TIME TO WAIT TO ALLOW THE BEAM TO MOVE TO THE NEXT PIXEL BEFORE STARTING NEXT SAMPLE
        pixelLabel = QLabel('Pixel delay time [ns]: ')
        pixelLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixelLabel.setToolTip("The pixel delay time is how long between moving the beam towards the next pixel and the start of sampling that pixel. \nThis gives time for the beam to move and stabilize at the location. This value need to be in 40ns increments.")
        pixelLabel.setFont(titleFont)
        mainGrid.addWidget(pixelLabel, r, 0, 1, 2)

        self.pixelDelay = QSpinBox()
        self.pixelDelay.setRange(40,10000000)
        self.pixelDelay.setSingleStep(40)
        self.pixelDelay.setValue(40)
        self.pixelDelay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pixelDelay.setFont(buttonFont)
        self.pixelDelay.setEnabled(False)
        self.pixelDelay.setToolTip("The pixel delay time is how long between moving the beam towards the next pixel and the start of sampling that pixel. \nThis gives time for the beam to move and stabilize at the location. This value need to be in 40ns increments.")
        self.enables.append(self.pixelDelay)
        self.pixelDelay.editingFinished.connect(self.uiPixelDelayChanged)
        mainGrid.addWidget(self.pixelDelay, r, 2, 1, 1)
        r += 1
        
        mainGrid.addItem(self.spacer, r, 0, 1, 3)
        r += 1
        
        #LINE WAIT TIME, TIME TO WAIT TO ALLOW THE BEAM TO GET BACK TO THE OTHER SIDE OF THE IMAGE AREA
        self.lineLabel = QLabel('Line delay time [ns]: ')
        self.lineLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineLabel.setToolTip("The line delay time is how long between the end of the last pixel in a line and the first pixel in the next line. \nThis gives time for the beam to get back and stable before starting the next line. This value need to be in 40ns increments.")
        self.lineLabel.setFont(titleFont)
        mainGrid.addWidget(self.lineLabel, r, 0, 1, 2)
        
        self.lineDelay = QSpinBox()
        self.lineDelay.setRange(500,10000000)
        self.lineDelay.setSingleStep(40)
        self.lineDelay.setValue(40)
        self.lineDelay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineDelay.setFont(buttonFont)
        self.lineDelay.setEnabled(False)
        self.lineDelay.setToolTip("The line delay time is how long between the end of the last pixel in a line and the first pixel in the next line. \nThis gives time for the beam to get back and stable before starting the next line. This value need to be in 40ns increments.")
        self.enables.append(self.lineDelay)
        self.lineDelay.editingFinished.connect(self.uiLineDelayChanged)
        mainGrid.addWidget(self.lineDelay, r, 2, 1, 1)
        r += 1
        
        mainGrid.addItem(self.spacer, r, 0, 1, 3)
        r += 1
        
        #TOTAL NUMBER OF PIXELS IN THE X AND Y DIRECTIONS
        xPixelsLabel = QLabel('Image Size [pixels]: ')
        xPixelsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        xPixelsLabel.setToolTip("The total number of pixels in the image.")
        xPixelsLabel.setFont(titleFont)
        mainGrid.addWidget(xPixelsLabel, r, 0, 1, 2)
        
        self.pixels = QComboBox()
        self.pixelList = ['8 x 8','16 x 16','32 x 32','64 x 64','128 x 128','256 x 256','512 x 512','1024 x 1024','2048 x 2048','4096 x 4096']
        self.pixels.addItems(self.pixelList)
        self.pixels.setToolTip("The total number of pixels in the image.")
        self.pixels.setFont(buttonFont)
        self.pixels.setEnabled(False)
        self.enables.append(self.pixels)
        self.pixels.currentIndexChanged.connect(self.uiPixelCountChanged)
        mainGrid.addWidget(self.pixels, r, 2, 1, 1)
        r += 1
        
        mainGrid.addItem(self.spacer, r, 0, 1, 3)
        r += 1
        
        self.startRunButton = QPushButton('Start')
        self.startRunButton.setFont(boldButtonFont)
        self.startRunButton.setEnabled(False)
        self.enables.append(self.startRunButton)
        self.startRunButton.clicked.connect(lambda: self.run(True))
        mainGrid.addWidget(self.startRunButton, r, 0, 1, 3)
        r += 2
        
        self.stopRunButton = QPushButton('Stop')
        self.stopRunButton.setFont(boldButtonFont)
        self.stopRunButton.setEnabled(True)
        self.invertedEnables.append(self.stopRunButton)
        self.stopRunButton.clicked.connect(lambda: self.run(False))
        mainGrid.addWidget(self.stopRunButton, r, 0, 1, 3)
        r += 2
        
        #LABEL TO DISPLAY X/Y/I VALUES ON MOUSEOVER
        self.mouseValues = QLabel("X:- Y:- I:-")
        self.mouseValues.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mouseValues.setFont(titleFont)
        mainGrid.addWidget(self.mouseValues, r, 0, 1, 3)
        r += 1
        
        mainGrid.addItem(self.spacer, r, 0, 1, 3)
        r += 1
        
        #SMOOTHING ON IMAGE OR NOT:
        self.smoothingGroup = QGroupBox("Image Smoothing")
        self.smoothingGroup.setFont(titleFont)
        self.smoothingGroup.setCheckable(False)
        self.smoothingGroup.setEnabled(False)
        self.enables.append(self.smoothingGroup)
        self.smoothingGroup.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainGrid.addWidget(self.smoothingGroup, r, 0, 2, 3)
        r += 1
        
        self.hbox = QHBoxLayout()
        self.smoothingGroup.setLayout(self.hbox)
        
        self.smoothingYes = QRadioButton('Yes')
        self.smoothingYes.setFont(buttonFont)
        self.smoothingYes.setToolTip("Clicking 'Yes' will smooth the pixel edges into one another via a low pass image filter.")
        self.smoothingYes.clicked.connect(lambda: self.imageUpdate())
        self.hbox.addWidget(self.smoothingYes)
        
        self.smoothingNo = QRadioButton('No')
        self.smoothingNo.setFont(buttonFont)
        self.smoothingNo.setChecked(True)
        self.smoothingNo.setToolTip("Clicking 'No' will display raw pixel data.")
        self.smoothingNo.clicked.connect(lambda: self.imageUpdate())
        self.hbox.addWidget(self.smoothingNo)
        
        r += 1
        
        # BUTTON TO SAVE AN IMAGE IN .JPG FORMAT
        self.saveJpgButton = QPushButton('Save JPG')
        self.saveJpgButton.setFont(buttonFont)
        self.saveJpgButton.setEnabled(False)
        self.enables.append(self.saveJpgButton)
        self.saveJpgButton.clicked.connect(lambda: self.saveJpg())
        mainGrid.addWidget(self.saveJpgButton, r, 0, 1, 3)
        
        # #ADC TEST MODE COMBOBOX
        # self.testAdc = QComboBox()
        # self.testAdc.addItem('Normal')
        # self.testAdc.addItem('Midscale Value')
        # self.testAdc.addItem('Checkerboard')
        # self.testAdc.addItem('1 / 0 Words')
        # self.testAdc.addItem('1 / 0 Bits')
        # self.testAdc.addItem('+ Full Scale')
        # self.testAdc.addItem('- Full Scale')
        # self.testAdc.setFont(buttonFont)
        # self.testAdc.setEnabled(False)
        # self.enables.append(self.testAdc)
        # self.testAdc.currentIndexChanged.connect(self.uiTestModeIndexChanged)
        # mainGrid.addWidget(self.testAdc, r, 0, 1, 3)
        
        #IMAGE FOR DISPLAYING RESULTS
        self.displayImg = QLabel()
        self.displayImg.setMouseTracking(True)
        self.displayImg.installEventFilter(self)
        mainGrid.addWidget(self.displayImg, 1, 3, r, 8)
        
        #PLOT FOR LINE PROFILES
        self.horizontalLineProfile = pyqtgraph.plot()
        self.horizontalLineProfile.showGrid(x = True, y = True, alpha=0.5)
        self.horizontalLineProfile.setLabel('left', 'Intensity', units = 'Counts')
        self.horizontalLineProfile.setLabel('bottom', 'Horizontal Pixels', units = '')
        self.horizontalLineProfile.setXRange(0,4096, padding=0.01)
        self.horizontalLineProfile.setYRange(0, 65535, padding=0.01)
        self.horizontalLineProfile.setLimits(xMin=0, minXRange=0, xMax=4095, maxXRange=4095,yMin=0,minYRange=0,yMax=65535,maxYRange=65535)
        # self.horizontalLineProfile.setWindowTitle('Horizontal Line Profile selected from image')
        self.horizontalLineProfile.setBackground('w')
        
        self.verticalLineProfile = pyqtgraph.plot()
        self.verticalLineProfile.showGrid(x = True, y = True, alpha=0.5)
        self.verticalLineProfile.setLabel('left', 'Intensity', units = 'Counts')
        self.verticalLineProfile.setLabel('bottom', 'Vertical Pixels', units = '')
        self.verticalLineProfile.setXRange(0,4096, padding=0.01)
        self.verticalLineProfile.setYRange(0, 65535, padding=0.01)
        self.verticalLineProfile.setLimits(xMin=0, minXRange=0, xMax=4095, maxXRange=4095,yMin=0,minYRange=0,yMax=65535,maxYRange=65535)
        # self.verticalLineProfile.setWindowTitle('Vertical Line Profile selected from image')
        self.verticalLineProfile.setBackground('w')
        
        #define the ranges for the plot
        self.plotX = np.array(range(0,4096))
        self.plotLeft = np.zeros_like(range(0,4096))
        self.plotRight = np.zeros_like(range(0,4096))
        
        #define the lines themselves
        self.lineLeft = self.horizontalLineProfile.plot(self.plotX, self.plotLeft, pen=pyqtgraph.mkPen('b', width=1), name='Left-click')
        self.lineRight = self.verticalLineProfile.plot(self.plotX, self.plotRight, pen=pyqtgraph.mkPen('r', width=1), name='Right-click')
        
        mainGrid.addWidget(self.horizontalLineProfile, 1, 11, int(r/2), 1)
        mainGrid.addWidget(self.verticalLineProfile, 1+int(r/2), 11, int(r/2), 1)

        mainGrid.setColumnStretch( 0,  0)
        mainGrid.setColumnStretch( 1,  0)
        mainGrid.setColumnStretch( 2,  0)
        mainGrid.setColumnStretch( 3,  1)
        mainGrid.setColumnStretch( 4,  1)
        mainGrid.setColumnStretch( 5,  1)
        mainGrid.setColumnStretch( 6,  1)
        mainGrid.setColumnStretch( 7,  1)
        mainGrid.setColumnStretch( 8,  1)
        mainGrid.setColumnStretch( 9,  1)
        mainGrid.setColumnStretch(10,  1)
        mainGrid.setColumnStretch(11,  0)
        
        #this will fire up the usb background class to communicate to the FPGA for us
        self.usb = UsbClass
        self.usb.initialize(self.usb)

        #instantiate a signals class from the usb module; this will throw events when new data arrives and the UI will catch them
        self.signals = self.usb.signals
        self.signals.modeUpdate.connect(self.updateMode)
        self.signals.integrationUpdate.connect(self.updateIntegration)
        self.signals.lineFlybackUpdate.connect(self.updateLineFlyback)
        self.signals.imageSizeUpdate.connect(self.updatePixels)
        self.signals.pixelMoveUpdate.connect(self.updatePixelMove)
        self.signals.newImageData.connect(self.imageUpdate)
        self.signals.imageDataComplete.connect(self.stopAcquisition)
        self.signals.fpgaConnected.connect(self.updateUI)
        self.signals.fpgaDisconnected.connect(self.disconnectUI)
        
        #set the layout into the widget
        self.setLayout(mainGrid)
                
        #show the main user interface
        # self.show()
        self.showMaximized()
    
    def resizeEvent(self, event):
        self.imageUpdate()
    
    #----------------------------------------------------------------------------------------------------------------------
    # UPDATES FROM FPGA HANDLED BELOW
    #----------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------
    #function to handle updates coming back from the FPGA on the mode status - typically only on startup of UI
    def updateMode(self):
        if not(self.usb.mode is None):
            print('Mode has been updated: ' + str(self.usb.mode))
            if int(self.usb.mode) == 1:
                self.rasterScanRadio.setChecked(True)
            elif int(self.usb.mode) == 2:
                self.rasterImageRadio.setChecked(True)
            elif int(self.usb.mode) == 3:
                self.randomScanRadio.setChecked(True)
            elif int(self.usb.mode) == 4:
                self.randomImageRadio.setChecked(True)
        else:
            self.testRadio.setChecked(True)
            print('Mode did not get retrieved correctly. Instead got: ' + str(self.usb.mode))
    #----------------------------------------------------------------------------------------------------------------------
    #function to handle updates coming back from the FPGA on the pixel integration time status - typically only on startup of UI
    def updateIntegration(self):
        if not(self.usb.integrationTime is None):
            print('integration time has been updated: ' + str(self.usb.integrationTime))
            self.integrationCycles.setCurrentIndex(int(self.usb.integrationTime))
        else:
            self.integrationCycles.setCurrentIndex(0)
            print('integration time did not get retrieved correctly. Instead got: ' + str(self.usb.integrationTime))
    #----------------------------------------------------------------------------------------------------------------------
    #function to handle updates coming back from the FPGA on the line flyback delay status - typically only on startup of UI
    def updateLineFlyback(self):
        if not(self.usb.lineFlybackTime is None):
            print('Line flyback time has been updated: ' + str(40*self.usb.lineFlybackTime))
            self.lineDelay.setValue(40*int(self.usb.lineFlybackTime))
        else:
            self.lineDelay.setValue(1000000)
            print('Line flyback time did not get retrieved correctly. Instead got: ' + str(self.usb.lineFlybackTime))
    #----------------------------------------------------------------------------------------------------------------------
    #function to handle updates coming back from the FPGA on the x pixel count status - typically only on startup of UI
    def updatePixels(self):
        if not(self.usb.imageSize is None):
            print('Total pixel count has been updated: ' + str(self.usb.imageSize))
            self.pixels.setCurrentIndex(self.pixelList.index(str(self.usb.imageSize) + ' x ' + str(self.usb.imageSize)))
            self.horizontalLineProfile.setXRange(0, self.usb.imageSize-1, padding=0.01)
            self.horizontalLineProfile.setLimits(xMin=0, minXRange=0, xMax=self.usb.imageSize-1, maxXRange=self.usb.imageSize-1, yMin=0, minYRange=0, yMax=65535, maxYRange=65535)
            self.verticalLineProfile.setXRange(0, self.usb.imageSize-1, padding=0.01)
            self.verticalLineProfile.setLimits(xMin=0, minXRange=0, xMax=self.usb.imageSize-1, maxXRange=self.usb.imageSize-1, yMin=0, minYRange=0, yMax=65535, maxYRange=65535)
            self.plotX = np.array(range(0, self.usb.imageSize))
            self.plotLeft = np.zeros_like(range(0, self.usb.imageSize))
            self.plotRight = np.zeros_like(range(0, self.usb.imageSize))
            self.leftClickPos = None
            self.rightClickPos = None
            self.imageUpdate()
        else:
            self.pixels.setCurrentIndex(0)
            print('Total pixel count did not get retrieved correctly. Instead got: ' + str(self.usb.imageSize))
    #----------------------------------------------------------------------------------------------------------------------
    #function to handle updates coming back from the FPGA on the pixel move delay status - typically only on startup of UI
    def updatePixelMove(self):
        print('Pixel-to-pixel move time has been updated: ' + str(40*self.usb.pixelWaitTime))
        if not(self.usb.pixelWaitTime is None):
            self.pixelDelay.setValue(40*int(self.usb.pixelWaitTime))
        else:
            self.pixelDelay.setValue(1000000)
            print('Pixel-to-pixel move time did not get retrieved correctly. Instead got: ' + str(self.usb.pixelWaitTime))
    
    #----------------------------------------------------------------------------------------------------------------------
    # UPDATES FROM UI HANDLED BELOW
    #----------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------
    # This function handles UI changes of the integration time. It converts a value from the drop-down combobox to a simple integer representing a power of 2 in 40ns increments.
    def uiIntegrationIndexChanged(self, index):
    #       (integration time in nanoseconds) / 40 = 2 ^ (output integer to FPGA)
    #       Hence a 40ns integration would be a 0, a 80ns integration is a 1, a 320ns integration is a 3, etc etc
        if self.closing:
            return
        if self.initFromFPGA == True:
            self.usb.setIntegration(self.usb, index)
    #----------------------------------------------------------------------------------------------------------------------
    #this function checks, scales and sends the pixel delay time
    def uiPixelDelayChanged(self):
        if self.closing:
            return
        if self.initFromFPGA == True:
            value = self.pixelDelay.value()
            if value > 10000000:
                value = 10000000
            elif value < 40:
                value = 40
            else:
                value = 40*round(value/40)
            self.pixelDelay.setValue(value)
            self.usb.setPixelMoveDelay(self.usb, value)
    #----------------------------------------------------------------------------------------------------------------------
    #this function checks, scales and sends the line delay time
    def uiLineDelayChanged(self):
        if self.closing:
            return
        if self.initFromFPGA == True:
            value = self.lineDelay.value()
            if value > 10000000:
                value = 10000000
            elif value < 40:
                value = 40
            else:
                value = 40*round(value/40)
            self.lineDelay.setValue(value)
            self.usb.setLineMoveDelay(self.usb, value)
    #----------------------------------------------------------------------------------------------------------------------
    #this function sends the pixel values, aka the x and y total size of the image
    def uiPixelCountChanged(self):
        if self.closing:
            return
        if self.initFromFPGA == True:
            strValue = self.pixels.currentText()
            xValuePosition = strValue.find(' x ')
            x = int(strValue[0:xValuePosition])
            self.usb.setPixels(self.usb, x)
            self.horizontalLineProfile.setXRange(0, x-1, padding=0.01)
            self.horizontalLineProfile.setLimits(xMin=0, minXRange=0, xMax=x-1, maxXRange=x-1, yMin=0, minYRange=0, yMax=65535, maxYRange=65535)
            self.verticalLineProfile.setXRange(0, x-1, padding=0.01)
            self.verticalLineProfile.setLimits(xMin=0, minXRange=0, xMax=x-1, maxXRange=x-1, yMin=0, minYRange=0, yMax=65535, maxYRange=65535)
            self.plotX = np.array(range(0, x))
            self.plotLeft = np.zeros_like(range(0, x))
            self.plotRight = np.zeros_like(range(0, x))
            self.leftClickPos = None
            self.rightClickPos = None
            self.imageUpdate()
    #----------------------------------------------------------------------------------------------------------------------
    #this function sets the mode of the acquisition
    def uiModeChanged(self, value):
        if self.closing:
            return
        if self.initFromFPGA == True:
            self.usb.setMode(self.usb, value)

    #----------------------------------------------------------------------------------------------------------------------
    #this function is called to display the image in one location
    def imageUpdate(self):
        if self.closing:
            return
        if self.initFromFPGA == True:
            #converts a numpy array into a qImage using 8-bit scaling
            imageData = self.usb.displayData
            xpix = self.usb.imageSize
            if self.displayImg.height() > self.displayImg.width():
                dimension = self.displayImg.width()
            else:
                dimension = self.displayImg.height()
            
            if self.smoothingYes.isChecked() == 1:
                self.qImg = QImage(imageData, xpix, xpix, QImage.Format.Format_Grayscale8).scaled(dimension, dimension, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)
            else:
                self.qImg = QImage(imageData, xpix, xpix, QImage.Format.Format_Grayscale8).scaled(dimension, dimension, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.FastTransformation)
            
            #creates a pixelmap out of the qImage
            self.pixmap = QPixmap.fromImage(self.qImg)
            
            #update the lines on the image for profiling
            if type(self.leftClickPos) != type(None) or type(self.rightClickPos) != type(None):
                qp = QPainter(self.pixmap)
                xPixelDiameter = self.pixmap.width()/self.usb.imageSize
                yPixelDiameter = self.pixmap.height()/self.usb.imageSize
                yOffset = int(self.displayImg.height()/2-self.pixmap.height()/2)
                xOffset = int(self.displayImg.width()/2-self.pixmap.width()/2)
                
                #if the left click has been clicked on the image, display a line across the image horizontally
                if type(self.leftClickPos) != type(None):
                    qp.setPen(QPen(Qt.GlobalColor.blue, 1))
                    yPix = int(int((self.leftClickPos.y()-yOffset) * (self.usb.imageSize)/(self.pixmap.height())) * yPixelDiameter)
                    xPix = int(int((0-xOffset) * (self.usb.imageSize)/(self.pixmap.width())) * xPixelDiameter)
                    qp.drawRoundedRect(xPix, yPix + int(yPixelDiameter/2), self.displayImg.width(), 1, xPixelDiameter/40, yPixelDiameter/40)
                    
                    #update the plot of the data on the graph
                    singleLine = self.usb.imageData[self.horizontalPixel, :]
                    self.lineLeft.setData(self.plotX, singleLine)
                    
                #if the right click has been clicked on the image, display a line across the image vertically
                if type(self.rightClickPos) != type(None):
                    qp.setPen(QPen(Qt.GlobalColor.red, 1))
                    yPix = int(int((0-yOffset) * (self.usb.imageSize)/(self.pixmap.height())) * yPixelDiameter)
                    xPix = int(int((self.rightClickPos.x()-xOffset) * (self.usb.imageSize)/(self.pixmap.width())) * xPixelDiameter)
                    qp.drawRoundedRect(xPix + int(xPixelDiameter/2), yPix, 1, self.displayImg.height(), xPixelDiameter/40, yPixelDiameter/40)
                    
                    #update the plot of the data on the graph
                    singleLine = self.usb.imageData[:, self.verticalPixel]
                    self.lineRight.setData(self.plotX, singleLine)
            
                qp.end()
            
            #the qLabel displayImg will show the pixelmap
            self.displayImg.setPixmap(self.pixmap)
            self.displayImg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            #update the label holding the image
            self.displayImg.show()
    
    #----------------------------------------------------------------------------------------------------------------------
    #this function is called when the "start" or "stop" buttons are pressed, and it will send commands to the FPGA to start/stop an image acquition
    def run(self, state):
    
        if self.closing:
            return
        if self.initFromFPGA == True:
            #turn it off by default, just in case it was on or something needed resetting or you're actually turning it off
            self.usb.setRun(self.usb, 0)
            if state == True:
                print('Beginning image scan acquisition')
                self.EnableDisable(False)
                self.usb.setRun(self.usb, 1)
            else:
                self.EnableDisable(True)
    
    #----------------------------------------------------------------------------------------------------------------------
    # this function is called when the usb connection receives "f1" which means the image has been fully updated and is done
    def stopAcquisition(self):
        print('. . . . . . . . . . . . . . . .')
        print('. Image acquisition complete  .')
        print('. . . . . . . . . . . . . . . .')
        self.EnableDisable(True)
    
    #----------------------------------------------------------------------------------------------------------------------
    #function to enable to disable the UI
    def EnableDisable(self, state):
        if self.closing:
            return
        for btn in self.enables:
            btn.setEnabled(state)
        for obj in self.invertedEnables:
            obj.setEnabled(not state)
        
    #----------------------------------------------------------------------------------------------------------------------
    #function called on startup only, gets initial values from the FPGA upon FPGA connection event
    def updateUI(self):
        self.connectText.setText("USB: Connected")
        self.EnableDisable(True)
        self.initFromFPGA = True
        
    #----------------------------------------------------------------------------------------------------------------------
    #function called on startup only, gets initial values from the FPGA upon FPGA connection event
    def disconnectUI(self):

        self.connectText.setText("USB: Disconnected")
        self.EnableDisable(False)
    
    #------------------------------------------------------------------------------------------------------------------
    #function to save the displayed 8-bit image in JPG format
    def saveJpg(self):
        
        #remove the colored squares from the image before saving
        leftClickPosTemp = self.leftClickPos
        rightClickPosTemp = self.rightClickPos
        
        self.leftClickPos = None
        self.rightClickPos = None
        
        self.imageUpdate()
        
        saveFileName, _ = QFileDialog.getSaveFileName(self, "Save file as JPG", "", "Image files(*.jpg)")
        if saveFileName:
            if str.lower(saveFileName[-4:]) != '.jpg':
                saveFileName = saveFileName + '.jpg'
            self.pixmap.save((saveFileName), 'JPG', 100)
            
        #add the colored squares back into the image after the save is complete
        self.leftClickPos = leftClickPosTemp
        self.rightClickPos = rightClickPosTemp
        
        self.imageUpdate()
        
    #----------------------------------------------------------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseMove and self.displayImg is obj:
            self.mouseOver(event.pos())
        if event.type() == QEvent.Type.MouseButtonPress and self.displayImg is obj:
            self.mouseClick(event.pos(), QApplication.instance().mouseButtons())
        return super(MainWindow, self).eventFilter(obj, event)
        
    #----------------------------------------------------------------------------------------------------------------------
    #when the mouse moves over the image, readout the current pixel location in x-y coordinates and the 14-bit data value at that pixel
    def mouseOver(self, pos):
        if self.closing:
            return
        if self.initFromFPGA == False or type(self.pixmap) == type(None):
            return
        if self.displayImg.height() > self.displayImg.width():
            dimension = self.displayImg.width()
        else:
            dimension = self.displayImg.height()
        yPix = int((pos.y()-(dimension/2 - self.pixmap.height()/2)) * (self.usb.imageSize)/(self.pixmap.height()))
        xPix = int((pos.x()-(dimension/2 - self.pixmap.width()/2))  * (self.usb.imageSize)/(self.pixmap.width()))
        if yPix < 0 or yPix >= self.usb.imageSize or xPix < 0 or xPix >= self.usb.imageSize:
            return
        try:
            value = self.usb.imageData[yPix,xPix]
        except:
            print('Value error: y = ' + str(yPix) + ' or x = ' + str(xPix) + ' are too big?')
        else:
            self.mouseValues.setText("X: " + str(xPix) + ", Y: " + str(yPix) + ", I: " + str(value))
    #------------------------------------------------------------------------------------------------------------------
    #when the mouse clicks on the image, will highlight the pixel it was over, and display a plot of the spectra in the processing page
    def mouseClick(self, position, button):
        if self.closing:
            return
        
        if self.initFromFPGA == False or type(self.pixmap) == type(None):
            return
        
        if self.displayImg.height() > self.displayImg.width():
            dimension = self.displayImg.width()
        else:
            dimension = self.displayImg.height()
            
        #if left clicked, plot a horizontal line across the image
        if button == Qt.MouseButton.LeftButton:
            tempValue = int((position.y()-(dimension/2 - self.pixmap.height()/2)) * (self.usb.imageSize)/(self.pixmap.height()))
            if tempValue < 0 or tempValue >= self.usb.imageSize:
                return
            self.horizontalPixel = tempValue
            self.leftClickPos = position
            self.imageUpdate()
        
        #if right clicked, plot a vertical line across the image
        elif button == Qt.MouseButton.RightButton:
            tempValue = int((position.x()-(dimension/2-self.pixmap.width()/2)) * (self.usb.imageSize)/(self.pixmap.width()))
            if tempValue < 0 or tempValue >= self.usb.imageSize:
                return
            self.verticalPixel = tempValue
            self.rightClickPos = position
            self.imageUpdate()
            
        #no other clicks allowed here
        else:
            return
    
    #----------------------------------------------------------------------------------------------------------------------
    #make a clean shutdown, only if intended though!
    def closeEvent(self,event):
        #generate a popup message box asking the user if they REALLY meant to shut down the software
        #note that unless they've saved variable presets etc, they would lose a lot of data if they accidentally shut down the program
        reply = QMessageBox.question(self,'Closing?', 'Are you sure you want to shut down the program?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        #respond according to the user reply
        if reply == QMessageBox.StandardButton.Yes:
            #if shutting down, close the USB connection and the UI
            self.usb.closing(self.usb)
            self.closing = True
            event.accept()
        else:
            event.ignore()

def main():
    #instantiate the application
    app = QApplication(sys.argv)
    
    #link the window to a variable, set the window to be visible
    screen = MainWindow()
    screen.show()
    
    #halt execution here until the window is closed
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
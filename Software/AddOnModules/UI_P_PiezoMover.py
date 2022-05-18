
import sys
from threading import Timer

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QGridLayout, QComboBox, QLineEdit, QGroupBox, QSpacerItem, QSizePolicy, QRadioButton, QCheckBox, QSlider
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#import UsbInterface.py
from AddOnModules.HardwareFiles.UsbInterface import usbClass

buttonName = 'Piezo Mover'                #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope




#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#***************************************************************************************************************

    usb = None
    receiveTimer = None
    pollTimer = None
    stopPolling = False
    closing = False
    enables = []
    invertedEnables = []
    pcEnables = []
    connected = False
    connectBtn = None
    currentStepX = 0
    currentStepY = 0
    currentStepZ = 0
    totalStepsX = 0
    totalStepsY = 0
    totalStepsZ = 0


    #function to create the user interface, and load in external modules for equipment control
    def initUI(self):

        #define a font for the title of the UI
        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(12)

        #define a font for the buttons of the UI
        self.buttonFont = QFont()
        self.buttonFont.setBold(False)
        self.buttonFont.setPointSize(10)

        self.boldButtonFont = QFont()
        self.boldButtonFont.setBold(True)
        self.boldButtonFont.setPointSize(12)

        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWid = 1000
        wid = 700
        wid2 = windowWid-wid
        windowHeight = 600
        self.setGeometry(50, 50, windowWid, windowHeight)
        self.setFixedSize(windowWid, windowHeight)

        #number of columns on main inputs
        col = 4
        #width of one column
        oneCol = int(wid/col-5*col)

        #width of two columns
        twoCol = int(2*wid/col-5*col/2)

        #name the window
        self.setWindowTitle('Piezo Mover Interface')

        #determine the grid pattern
        mainGrid = QGridLayout()
        mainGrid.setSpacing(10)
        mainGrid.setAlignment(Qt.AlignTop)

        #create a label at the top of the window so we know what the software does
        topTextLabel = QLabel('Piezo Mover Interface', self)
        topTextLabel.setAlignment(Qt.AlignCenter)
        topTextLabel.setFixedWidth(wid-10)
        topTextLabel.setWordWrap(True)
        topTextLabel.setFont(titleFont)
        mainGrid.addWidget(topTextLabel, 0, 0, 1, col+3)

        self.usb = usbClass
        self.usb.init(self.usb)
        # self.usb.newData.connect(self.newData)
        self.setTimer()

        self.devices = QComboBox()
        self.devices.setFont(self.buttonFont)
        self.devices.setFixedWidth(oneCol)
        self.invertedEnables.append(self.devices)
        mainGrid.addWidget(self.devices, 1, 0, 1, 1)

        self.connectBtn = QPushButton('Connect')
        self.connectBtn.setFont(self.buttonFont)
        self.connectBtn.clicked.connect(lambda: self.connectToUsb(self.devices.currentIndex()))
        self.connectBtn.setFixedWidth(oneCol)
        mainGrid.addWidget(self.connectBtn, 1, 1, 1, 1)

        #-------------------------------------------------------------
        #remote settings (feedback only):
        #-------------------------------------------------------------

        self.fpgaBncStatus = QLabel('Mode: ')
        self.fpgaBncStatus.setFont(self.buttonFont)
        self.fpgaBncStatus.setFixedWidth(twoCol)
        mainGrid.addWidget(self.fpgaBncStatus, 1, 2, 1, 2)

        self.remoteAmpStatus = QLabel('Remote amplitude [V]: ')
        self.remoteAmpStatus.setFont(self.buttonFont)
        self.remoteAmpStatus.setFixedWidth(twoCol)
        mainGrid.addWidget(self.remoteAmpStatus, 2, 0, 1, 2)

        self.remoteFreqStatus = QLabel('Remote frequency [Hz]: ')
        self.remoteFreqStatus.setFont(self.buttonFont)
        self.remoteFreqStatus.setFixedWidth(twoCol)
        mainGrid.addWidget(self.remoteFreqStatus, 2, 2, 1, 2)

        self.jogButtonStatus = QLabel('Currently jogging: ')
        self.jogButtonStatus.setFont(self.buttonFont)
        self.jogButtonStatus.setFixedWidth(twoCol)
        mainGrid.addWidget(self.jogButtonStatus, 3, 0, 1, 2)

        self.bankStatus = QLabel('Current bank: ')
        self.bankStatus.setFont(self.buttonFont)
        self.bankStatus.setFixedWidth(oneCol)
        mainGrid.addWidget(self.bankStatus, 3, 2, 1, 1)

        self.usbError = QLabel('USB error: ')
        self.usbError.setFont(self.buttonFont)
        self.usbError.setFixedWidth(oneCol)
        mainGrid.addWidget(self.usbError, 3, 3, 1, 1)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainGrid.addItem(self.spacer, 4, 0, 1, 4)

        #-------------------------------------------------------------
        #PC settings (set and get):
        #-------------------------------------------------------------

        self.stepValidator = QIntValidator(1, 65535)

        #RUN NUMBER OF STEPS IN X DIRECTION
        self.xLabel = QLabel('X Axis:')
        self.xLabel.setFixedWidth(oneCol)
        self.xLabel.setFont(self.buttonFont)
        mainGrid.addWidget(self.xLabel, 5, 0, 1, 1)

        self.xRun = QLabel('Stopped')
        self.xRun.setFixedWidth(oneCol)
        self.xRun.setFont(self.buttonFont)
        mainGrid.addWidget(self.xRun, 5, 1, 1, 1)

        self.xStepLabel = QLabel('X Steps:')
        self.xStepLabel.setFont(self.buttonFont)
        self.xStepLabel.setFixedWidth(oneCol)
        mainGrid.addWidget(self.xStepLabel, 6, 0, 1, 1)

        self.xStepCount = QLineEdit()
        self.xStepCount.setValidator(self.stepValidator)
        self.xStepCount.setText('-')
        self.xStepCount.setFont(self.buttonFont)
        self.xStepCount.setEnabled(False)
        self.enables.append(self.xStepCount)
        self.xStepCount.setFixedWidth(oneCol)
        # self.xStepCount.editingFinished.connect(lambda: self.usb.set(self.usb, 0x35, int(self.xStepCount.text())))
        self.xStepCount.textChanged.connect(lambda: self.validateInput(0x35, 1, 0))
        mainGrid.addWidget(self.xStepCount, 6, 1, 1, 1)

        self.startRunXP = QPushButton('Start X+')
        self.startRunXP.setFont(self.buttonFont)
        self.startRunXP.setEnabled(False)
        self.enables.append(self.startRunXP)
        self.startRunXP.setFixedWidth(oneCol)
        self.startRunXP.clicked.connect(lambda: self.usb.set(self.usb, 0x32, 0x01))
        mainGrid.addWidget(self.startRunXP, 5, 2, 1, 1)

        self.startRunXN = QPushButton('Start X-')
        self.startRunXN.setFont(self.buttonFont)
        self.startRunXN.setEnabled(False)
        self.enables.append(self.startRunXN)
        self.startRunXN.setFixedWidth(oneCol)
        self.startRunXN.clicked.connect(lambda: self.usb.set(self.usb, 0x32, 0x02))
        mainGrid.addWidget(self.startRunXN, 5, 3, 1, 1)

        self.stepStatusX = QLabel('Step Status:')
        self.stepStatusX.setFont(self.buttonFont)
        self.stepStatusX.setFixedWidth(oneCol)
        mainGrid.addWidget(self.stepStatusX, 6, 2, 1, 1)

        self.statusX = QLabel('- / -')
        self.statusX.setFont(self.buttonFont)
        self.statusX.setFixedWidth(oneCol)
        mainGrid.addWidget(self.statusX, 6, 3, 1, 1)

        mainGrid.addItem(self.spacer, 7, 0, 1, 4)

        #RUN NUMBER OF STEPS IN Y DIRECTION
        self.yLabel = QLabel('Y Axis: ')
        self.yLabel.setFixedWidth(oneCol)
        self.yLabel.setFont(self.buttonFont)
        mainGrid.addWidget(self.yLabel, 8, 0, 1, 1)

        self.yRun = QLabel('Stopped')
        self.yRun.setFixedWidth(oneCol)
        self.yRun.setFont(self.buttonFont)
        mainGrid.addWidget(self.yRun, 8, 1, 1, 1)

        self.yStepLabel = QLabel('Y Steps:')
        self.yStepLabel.setFont(self.buttonFont)
        self.yStepLabel.setFixedWidth(oneCol)
        mainGrid.addWidget(self.yStepLabel, 9, 0, 1, 1)

        self.yStepCount = QLineEdit()
        self.yStepCount.setValidator(self.stepValidator)
        self.yStepCount.setText('-')
        self.yStepCount.setFont(self.buttonFont)
        self.yStepCount.setEnabled(False)
        self.enables.append(self.yStepCount)
        self.yStepCount.setFixedWidth(oneCol)
        # self.yStepCount.editingFinished.connect(lambda: self.usb.set(self.usb, 0x36, int(self.yStepCount.text())))
        self.yStepCount.textChanged.connect(lambda: self.validateInput(0x36, 1, 0))
        mainGrid.addWidget(self.yStepCount, 9, 1, 1, 1)

        self.startRunYP = QPushButton('Start Y+')
        self.startRunYP.setFont(self.buttonFont)
        self.startRunYP.setEnabled(False)
        self.enables.append(self.startRunYP)
        self.startRunYP.setFixedWidth(oneCol)
        self.startRunYP.clicked.connect(lambda: self.usb.set(self.usb, 0x33, 1))
        mainGrid.addWidget(self.startRunYP, 8, 2, 1, 1)

        self.startRunYN = QPushButton('Start Y-')
        self.startRunYN.setFont(self.buttonFont)
        self.startRunYN.setEnabled(False)
        self.enables.append(self.startRunYN)
        self.startRunYN.setFixedWidth(oneCol)
        self.startRunYN.clicked.connect(lambda: self.usb.set(self.usb, 0x33, 2))
        mainGrid.addWidget(self.startRunYN, 8, 3, 1, 1)

        self.stepStatusY = QLabel('Step Status:')
        self.stepStatusY.setFont(self.buttonFont)
        self.stepStatusY.setFixedWidth(oneCol)
        mainGrid.addWidget(self.stepStatusY, 9, 2, 1, 1)

        self.statusY = QLabel('- / -')
        self.statusY.setFont(self.buttonFont)
        self.statusY.setFixedWidth(oneCol)
        mainGrid.addWidget(self.statusY, 9, 3, 1, 1)

        mainGrid.addItem(self.spacer, 10, 0, 1, 4)

        #RUN NUMBER OF STEPS IN Z DIRECTION
        self.zLabel = QLabel('Z Axis: ')
        self.zLabel.setFixedWidth(oneCol)
        self.zLabel.setFont(self.buttonFont)
        mainGrid.addWidget(self.zLabel, 11, 0, 1, 1)

        self.zRun = QLabel('Stopped')
        self.zRun.setFixedWidth(oneCol)
        self.zRun.setFont(self.buttonFont)
        mainGrid.addWidget(self.zRun, 11, 1, 1, 1)

        self.zStepLabel = QLabel('Z Steps:')
        self.zStepLabel.setFont(self.buttonFont)
        self.zStepLabel.setFixedWidth(oneCol)
        mainGrid.addWidget(self.zStepLabel, 12, 0, 1, 1)

        self.zStepCount = QLineEdit()
        self.zStepCount.setValidator(self.stepValidator)
        self.zStepCount.setText('-')
        self.zStepCount.setFont(self.buttonFont)
        self.zStepCount.setEnabled(False)
        self.enables.append(self.zStepCount)
        self.zStepCount.setFixedWidth(oneCol)
        self.zStepCount.textChanged.connect(lambda: self.validateInput(0x37, 1, 0))
        # self.zStepCount.editingFinished.connect(lambda: self.usb.set(self.usb, 0x37, int(self.zStepCount.text())))
        mainGrid.addWidget(self.zStepCount, 12, 1, 1, 1)

        self.startRunZP = QPushButton('Start Z+')
        self.startRunZP.setFont(self.buttonFont)
        self.startRunZP.setEnabled(False)
        self.enables.append(self.startRunZP)
        self.startRunZP.setFixedWidth(oneCol)
        self.startRunZP.clicked.connect(lambda: self.usb.set(self.usb, 0x34, 1))
        mainGrid.addWidget(self.startRunZP, 11, 2, 1, 1)

        self.startRunZN = QPushButton('Start Z-')
        self.startRunZN.setFont(self.buttonFont)
        self.startRunZN.setEnabled(False)
        self.enables.append(self.startRunZN)
        self.startRunZN.setFixedWidth(oneCol)
        self.startRunZN.clicked.connect(lambda: self.usb.set(self.usb, 0x34, 2))
        mainGrid.addWidget(self.startRunZN, 11, 3, 1, 1)

        self.stepStatusZ = QLabel('Step Status:')
        self.stepStatusZ.setFont(self.buttonFont)
        self.stepStatusZ.setFixedWidth(oneCol)
        mainGrid.addWidget(self.stepStatusZ, 12, 2, 1, 1)

        self.statusZ = QLabel('- / -')
        self.statusZ.setFont(self.buttonFont)
        self.statusZ.setFixedWidth(oneCol)
        mainGrid.addWidget(self.statusZ, 12, 3, 1, 1)

        mainGrid.addItem(self.spacer, 13, 0, 1, 4)

        #PC SETTINGS, IN CASE REMOTE IS MISSING/BROKEN

        self.ampLabel = QLabel('PC Amplitude [V]: ')
        self.ampLabel.setFont(self.buttonFont)
        self.ampLabel.setFixedWidth(oneCol)
        mainGrid.addWidget(self.ampLabel, 14, 0, 1, 1)

        self.pcAmp = QLineEdit('-')
        amplitudeValidator = QDoubleValidator(100, 400, 2)
        self.pcAmp.setValidator(amplitudeValidator)
        self.pcAmp.setFont(self.buttonFont)
        self.pcAmp.setFixedWidth(oneCol)
        self.pcAmp.setEnabled(False)
        self.pcEnables.append(self.pcAmp)
        self.pcAmp.textChanged.connect(lambda: self.validateInput(0x30, 4072/300, -1357.3))
        # self.pcAmp.editingFinished.connect(lambda: self.usb.set(self.usb, 0x30, 4072/300*int(self.pcAmp.text())-1357.3))
        mainGrid.addWidget(self.pcAmp, 14, 1, 1, 1)

        self.freqLabel = QLabel('PC Frequency [Hz]: ')
        self.freqLabel.setFont(self.buttonFont)
        self.freqLabel.setFixedWidth(oneCol)
        mainGrid.addWidget(self.freqLabel, 14, 2, 1, 1)

        self.pcFreq = QLineEdit('-')
        frequencyValidator = QDoubleValidator(300, 20000, 2)
        self.pcFreq.setValidator(frequencyValidator)
        self.pcFreq.setFont(self.buttonFont)
        self.pcFreq.setFixedWidth(oneCol)
        self.pcFreq.setEnabled(False)
        self.pcEnables.append(self.pcFreq)
        self.pcFreq.textChanged.connect(lambda: self.validateInput(0x31, 4072/47985, -56.92))
        # self.pcFreq.editingFinished.connect(lambda: self.usb.set(self.usb, 0x31, 4072/47985*int(self.pcFreq.text())-56.92))
        mainGrid.addWidget(self.pcFreq, 14, 3, 1, 1)

        self.pcBank1 = QRadioButton('Bank 1')
        self.pcBank1.setFont(self.buttonFont)
        self.pcBank1.setFixedWidth(oneCol)
        self.pcBank1.setChecked(True)
        self.pcBank1.setEnabled(False)
        self.pcEnables.append(self.pcBank1)
        self.pcBank1.toggled.connect(lambda: self.usb.set(self.usb, 0x38, 1))
        mainGrid.addWidget(self.pcBank1, 15, 0, 1, 1)

        self.pcBank2 = QRadioButton('Bank 2')
        self.pcBank2.setFont(self.buttonFont)
        self.pcBank2.setFixedWidth(oneCol)
        self.pcBank2.setChecked(False)
        self.pcBank2.setEnabled(False)
        self.pcEnables.append(self.pcBank2)
        self.pcBank2.toggled.connect(lambda: self.usb.set(self.usb, 0x38, 2))
        mainGrid.addWidget(self.pcBank2, 15, 1, 1, 1)

        self.pcBank3 = QRadioButton('Bank 3')
        self.pcBank3.setFont(self.buttonFont)
        self.pcBank3.setFixedWidth(oneCol)
        self.pcBank3.setChecked(False)
        self.pcBank3.setEnabled(False)
        self.pcEnables.append(self.pcBank3)
        self.pcBank3.toggled.connect(lambda: self.usb.set(self.usb, 0x38, 3))
        mainGrid.addWidget(self.pcBank3, 15, 2, 1, 1)

        self.pcBank4 = QRadioButton('Bank 4')
        self.pcBank4.setFont(self.buttonFont)
        self.pcBank4.setFixedWidth(oneCol)
        self.pcBank4.setChecked(False)
        self.pcBank4.setEnabled(False)
        self.pcEnables.append(self.pcBank4)
        self.pcBank4.toggled.connect(lambda: self.usb.set(self.usb, 0x38, 4))
        mainGrid.addWidget(self.pcBank4, 15, 3, 1, 1)

        mainGrid.addItem(self.spacer, 16, 0, 1, 4)

        self.fpgaTemperature = QLabel('-')
        self.fpgaTemperature.setFont(self.buttonFont)
        self.fpgaTemperature.setFixedWidth(oneCol)
        mainGrid.addWidget(self.fpgaTemperature, 17, 0, 1, 1)

        self.vccInt = QLabel('-')
        self.vccInt.setFont(self.buttonFont)
        self.vccInt.setFixedWidth(oneCol)
        mainGrid.addWidget(self.vccInt, 17, 1, 1, 1)

        self.vccAux = QLabel('-')
        self.vccAux.setFont(self.buttonFont)
        self.vccAux.setFixedWidth(oneCol)
        mainGrid.addWidget(self.vccAux, 17, 2, 1, 1)

        self.vccBram = QLabel('-')
        self.vccBram.setFont(self.buttonFont)
        self.vccBram.setFixedWidth(oneCol)
        mainGrid.addWidget(self.vccBram, 17, 3, 1, 1)

        #holding X position portion
        self.holdXVoltage = QSlider(Qt.Vertical)
        self.holdXVoltage.setMinimum(0)
        self.holdXVoltage.setMaximum(65535)
        self.holdXVoltage.setSingleStep(1)
        self.holdXVoltage.setValue(32768)
        self.holdXVoltage.setFixedWidth(int(wid2/3)-10)
        self.holdXVoltage.setTickPosition(QSlider.NoTicks)
        self.holdXVoltage.setEnabled(False)
        self.holdXVoltage.valueChanged.connect(lambda: self.usb.set(self.usb, 0x42, self.holdXVoltage.value()))
        mainGrid.addWidget(self.holdXVoltage, 2, 4, 13, 1)

        self.holdXEnable = QCheckBox('Cmd X', self)
        self.holdXEnable.setFont(self.buttonFont)
        self.holdXEnable.setFixedWidth(int(wid2/3)-10)
        self.enables.append(self.holdXEnable)
        self.holdXEnable.setEnabled(False)
        self.holdXEnable.toggled.connect(lambda: self.usb.set(self.usb, 0x39, int(self.holdXEnable.isChecked())))
        self.holdXEnable.toggled.connect(lambda: self.holdXVoltage.setEnabled(self.holdXEnable.isChecked()))
        mainGrid.addWidget(self.holdXEnable, 1, 4, 1, 1)

        #holding Y position portion
        self.holdYVoltage = QSlider(Qt.Vertical)
        self.holdYVoltage.setMinimum(0)
        self.holdYVoltage.setMaximum(65535)
        self.holdYVoltage.setSingleStep(1)
        self.holdYVoltage.setValue(32768)
        self.holdYVoltage.setFixedWidth(int(wid2/3)-10)
        self.holdYVoltage.setTickPosition(QSlider.NoTicks)
        self.holdYVoltage.setEnabled(False)
        self.holdYVoltage.valueChanged.connect(lambda: self.usb.set(self.usb, 0x43, self.holdYVoltage.value()))
        mainGrid.addWidget(self.holdYVoltage, 2, 5, 13, 1)

        self.holdYEnable = QCheckBox('Cmd Y', self)
        self.holdYEnable.setFont(self.buttonFont)
        self.holdYEnable.setFixedWidth(int(wid2/3)-10)
        self.enables.append(self.holdYEnable)
        self.holdYEnable.setEnabled(False)
        self.holdYEnable.toggled.connect(lambda: self.usb.set(self.usb, 0x40, int(self.holdYEnable.isChecked())))
        self.holdYEnable.toggled.connect(lambda: self.holdYVoltage.setEnabled(self.holdYEnable.isChecked()))
        mainGrid.addWidget(self.holdYEnable, 1, 5, 1, 1)

        #holding Z position portion
        self.holdZVoltage = QSlider(Qt.Vertical)
        self.holdZVoltage.setMinimum(0)
        self.holdZVoltage.setMaximum(65535)
        self.holdZVoltage.setSingleStep(1)
        self.holdZVoltage.setValue(32768)
        self.holdZVoltage.setFixedWidth(int(wid2/3)-10)
        self.holdZVoltage.setTickPosition(QSlider.NoTicks)
        self.holdZVoltage.setEnabled(False)
        self.holdZVoltage.valueChanged.connect(lambda: self.usb.set(self.usb, 0x44, self.holdZVoltage.value()))
        mainGrid.addWidget(self.holdZVoltage, 2, 6, 13, 1)

        self.holdZEnable = QCheckBox('Cmd Z', self)
        self.holdZEnable.setFont(self.buttonFont)
        self.holdZEnable.setFixedWidth(int(wid2/3)-10)
        self.enables.append(self.holdZEnable)
        self.holdZEnable.setEnabled(False)
        self.holdZEnable.toggled.connect(lambda: self.usb.set(self.usb, 0x41, int(self.holdZEnable.isChecked())))
        self.holdZEnable.toggled.connect(lambda: self.holdZVoltage.setEnabled(self.holdZEnable.isChecked()))
        mainGrid.addWidget(self.holdZEnable, 1, 6, 1, 1)


        #set the layout into the widget
        self.setLayout(mainGrid)



    def validateInput(self, register, slope, intercept):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#ffffff'
            self.usb.set(self.usb, register, round(slope*float(sender.text())+intercept,0))
            # print('data sent: ' + str(round(slope*float(sender.text())+intercept,0)))
        else:
            if sender.text():
                if int(sender.text()) > validator.top():
                    sender.setText(str(validator.top()))
                    self.usb.set(self.usb, register, round(slope*float(sender.text())+intercept,0))
                    color = '#ffffff'
                else:
                    color = '#f6989d'
            else:
                color = '#f6989d'
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def connectToUsb(self, index):
        if self.connected == False:
            if self.usb.connectUsb(self.usb, index) == 0:
                self.EnableDisable(True)
                self.connectBtn.setText('Disconnect')
                self.connected = True
                self.usb.poll(self.usb)
                self.stopPolling = False
                self.firstRun = True
            else:
                self.EnableDisable(False)
                self.connectBtn.setText('Connect')
                self.connected = False
                self.stopPolling = True
        else:
            self.usb.disconnectRequest = True
            self.EnableDisable(False)
            self.connectBtn.setText('Connect')
            self.connected = False
            self.stopPolling = True

    def EnableDisable(self, state):
        for btn in self.enables:
            btn.setEnabled(state)
        for obj in self.invertedEnables:
            obj.setEnabled(not state)

    def checkInfoReceived(self):
        while self.usb.readLock:
            pass

        if self.usb.haveNewData == True:
            self.usb.haveNewData = False
            readValue = self.usb.readValue.lower()
            try:
                while readValue:
                    #if things are being shut down, get out of there
                    if self.stopPolling == True:
                        return
                    #retrieve the register being accessed
                    register = int(readValue[0:2])
                    #retrive the operation being done - 'a' == get; 'b' == set; 'c' == poll
                    operation = readValue[2]
                    if operation == 'c':
                        #polling data is a long string separated by 'e' characters until the last one, which has an 'f'
                        lastIndex = readValue.find('e')
                        if lastIndex == -1:
                            lastIndex = readValue.find('f')
                            if lastIndex != -1:
                                self.pollTimer = Timer(0.100, self.pollUsb)
                                self.pollTimer.start()
                    else:
                        lastIndex = readValue.find('f')
                    if lastIndex == -1:
                        print('Inappropriate return on a get. Try again.')
                        return
                    value = int(readValue[3:lastIndex])
                    readValue = readValue.replace(readValue[0:lastIndex+1],'')
                    #operation was a get - update the status on-screen
                    if operation == 'a' or operation == 'c':

                        #FPGA/BNC control switch status
                        if register == 0:
                            if value == 0:
                                self.fpgaBncStatus.setText('Mode: BNC')
                            elif value == 1:
                                self.fpgaBncStatus.setText('Mode: FPGA')

                        #remote amplitude knob status
                        elif register == 1:
                            self.remoteAmpStatus.setText('Remote amplitude: ' + str(round(300/4096*value+100,0)) + 'V')

                        #remote frequency knob status
                        elif register == 2:
                            self.remoteFreqStatus.setText('Remote frequency: ' + str(round(49350/4096*value+650,0)) + 'Hz')
                            # self.remoteFreqStatus.setText('Remote frequency: ' + str(value) + 'Hz')

                        #remote directional jog buttons
                        elif register == 3 or register == 4 or register == 5 or register == 6 or register == 7 or register == 8:
                            if register == 3:
                                txt = 'X+ '
                            elif register == 4:
                                txt = 'X- '
                            elif register == 5:
                                txt = 'Y+ '
                            elif register == 6:
                                txt = 'Y- '
                            elif register == 7:
                                txt = 'Z+ '
                            elif register == 8:
                                txt = 'Z- '
                            jogStr = str(self.jogButtonStatus.text())
                            if value == 1:
                                if jogStr.find(txt) == -1:
                                    self.jogButtonStatus.setText(jogStr + txt)
                            elif value == 0:
                                if jogStr.find(txt) > 0:
                                    self.jogButtonStatus.setText(jogStr.replace(txt, ''))

                        #remote jog bank selection (1-4)
                        elif register == 9:
                            self.bankStatus.setText('Current bank: ' + str(value))

                        #FPGA's usb error status
                        elif register == 10:
                            self.usbError.setText('USB error: ' + str(value))

                        #X-axis running status
                        elif register == 11:
                            if value == 0:
                                #self.startRunXP.setEnabled(True) <-These Lines Were Causing the Program to Crash
                                #self.startRunXN.setEnabled(True)
                                self.xRun.setText('Stopped')
                            elif value == 1 or value == 2:
                                #self.startRunXP.setEnabled(False)
                                #self.startRunXN.setEnabled(False)
                                if value == 1:
                                    self.xRun.setText('Running forward')
                                elif value == 2:
                                    self.xRun.setText('Running reverse')
                        #Y-axis running status
                        elif register == 12:
                            if value == 0:
                                #self.startRunYP.setEnabled(True)
                                #self.startRunYN.setEnabled(True)
                                self.yRun.setText('Stopped')
                            elif value == 1 or value == 2:
                                #self.startRunYP.setEnabled(False)
                                #self.startRunYN.setEnabled(False)
                                if value == 1:
                                    self.yRun.setText('Running forward')
                                elif value == 2:
                                    self.yRun.setText('Running reverse')
                        #Z-axis running status
                        elif register == 13:
                            if value == 0:
                                #self.startRunZP.setEnabled(True)
                                #self.startRunZN.setEnabled(True)
                                self.zRun.setText('Stopped')
                            elif value == 1 or value == 2:
                                #self.startRunZP.setEnabled(False)
                                #self.startRunZN.setEnabled(False)
                                if value == 1:
                                    self.zRun.setText('Running forward')
                                elif value == 2:
                                    self.zRun.setText('Running reverse')

                        #X-axis current step
                        elif register == 14:
                            self.currentStepX = value
                        #Y-axis current step
                        elif register == 15:
                            self.currentStepY = value
                        #Z-axis current step
                        elif register == 16:
                            self.currentStepZ = value

                        #X-axis total steps for this move
                        elif register == 17:
                            self.totalStepsX = value
                            self.statusX.setText(str(self.currentStepX) + ' / ' + str(self.totalStepsX))
                            if self.firstRun:
                                self.xStepCount.setText(str(value))
                        #Y-axis total steps for this move
                        elif register == 18:
                            self.totalStepsY = value
                            self.statusY.setText(str(self.currentStepY) + ' / ' + str(self.totalStepsY))
                            if self.firstRun:
                                self.yStepCount.setText(str(value))
                        #Z-axis total steps for this move
                        elif register == 19:
                            self.totalStepsZ = value
                            self.statusZ.setText(str(self.currentStepZ) + ' / ' + str(self.totalStepsZ))
                            if self.firstRun:
                                self.zStepCount.setText(str(value))

                        #X-axis error status
                        elif register == 20:
                            pass
                            # if value == 0:
                                # self.xLabel.setText('X-axis: ')
                                # self.xLabel.setFont(self.buttonFont)
                            # elif value == 1:
                                # self.xLabel.setText('X-axis: Fwd Max')
                                # self.xLabel.setFont(self.boldButtonFont)
                            # elif value == 2:
                                # self.xLabel.setText('X-axis: Fwd Min')
                                # self.xLabel.setFont(self.boldButtonFont)
                            # elif value == 3:
                                # self.xLabel.setText('X-axis: Rev Max')
                                # self.xLabel.setFont(self.boldButtonFont)
                            # elif value == 4:
                                # self.xLabel.setText('X-axis: Rev Min')
                                # self.xLabel.setFont(self.boldButtonFont)
                        #Y-axis error status
                        elif register == 21:
                            pass
                            # if value == 0:
                                # self.yLabel.setText('Y-axis: ')
                                # self.yLabel.setFont(self.buttonFont)
                            # elif value == 1:
                                # self.yLabel.setText('Y-axis: Fwd Max')
                                # self.yLabel.setFont(self.boldButtonFont)
                            # elif value == 2:
                                # self.yLabel.setText('Y-axis: Fwd Min')
                                # self.yLabel.setFont(self.boldButtonFont)
                            # elif value == 3:
                                # self.yLabel.setText('Y-axis: Rev Max')
                                # self.yLabel.setFont(self.boldButtonFont)
                            # elif value == 4:
                                # self.yLabel.setText('Y-axis: Rev Min')
                                # self.yLabel.setFont(self.boldButtonFont)
                        #Z-axis error status
                        elif register == 22:
                            pass
                            # if value == 0:
                                # self.zLabel.setText('Z-axis: ')
                                # self.zLabel.setFont(self.buttonFont)
                            # elif value == 1:
                                # self.zLabel.setText('Z-axis: Fwd Max')
                                # self.zLabel.setFont(self.boldButtonFont)
                            # elif value == 2:
                                # self.zLabel.setText('Z-axis: Fwd Min')
                                # self.zLabel.setFont(self.boldButtonFont)
                            # elif value == 3:
                                # self.zLabel.setText('Z-axis: Rev Max')
                                # self.zLabel.setFont(self.boldButtonFont)
                            # elif value == 4:
                                # self.zLabel.setText('Z-axis: Rev Min')
                                # self.zLabel.setFont(self.boldButtonFont)

                        #use the PC settings because the remote is missing or broken because people suck
                        elif register == 23:
                            for obj in self.pcEnables:
                                obj.setEnabled(bool(value))

                        #PC amplitude settings, read only on first run
                        elif register == 24:
                            if self.firstRun:
                                self.pcAmp.setText(str(round(300/4072*value+99.41,0)))

                        #PC frequency setting, read only on first run
                        elif register == 25:
                            if self.firstRun:
                                self.pcFreq.setText(str(round(47985/4072*value+670.7,0)))

                        #FPGA temperature for display
                        elif register == 26:
                            if self.firstRun:
                                self.fpgaTemperature.setText('FPGA Temp: ' + str(round(value,4)) + '\u00B0C')

                        #Vcc Int voltage - multiply by 3, divide by 4096 to get pure voltage
                        elif register == 27:
                            if self.firstRun:
                                self.vccInt.setText('Vcc Int: ' + str(round(value*3/4096,3)) + 'V')

                        #Vcc Auxiliary voltage - multiply by 3, divide by 4096 to get pure voltage
                        elif register == 28:
                            if self.firstRun:
                                self.vccAux.setText('Vcc Aux: ' + str(round(value*3/4096,3)) + 'V')

                        #Vcc block RAM voltage - multiply by 3, divide by 4096 to get pure voltage
                        elif register == 29:
                            if self.firstRun:
                                self.vccBram.setText('Vcc BRAM: ' + str(round(value*3/4096,3)) + 'V')

                        else:
                            print('Unknown register request: ' + str(register))
                    elif operation == 'b':
                        if value == 0:
                            print('Failed setting register ' + str(register))
                if self.firstRun == True:
                    self.firstRun = False
            except:
                print('Something went wrong with communications. Data sent was: ' + readValue)
        #if no new data was observed, check for new connections (USB devices)
        elif self.usb.haveNewConnections == True:
            self.usb.haveNewConnections = False
            self.devices.clear()
            self.devices.addItems(self.usb.FPGAs)
        self.setTimer()

    def setTimer(self):
        if not self.closing:
            #start the timer to run
            self.receiveTimer = Timer(0.100, self.checkInfoReceived)
            self.receiveTimer.start()
        else:
            self.receiveTimer = None

    def pollUsb(self):
        self.usb.poll(self.usb)

    #make a clean shutdown, only if intended though!
    def closeEvent(self,event):
        #generate a popup message box asking the user if they REALLY meant to shut down the software
        #note that unless they've saved variable presets etc, they would lose a lot of data if they accidentally shut down the program
        reply = QMessageBox.question(self,'Closing?', 'Are you sure you want to shut down the program?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        #respond according to the user reply
        if reply == QMessageBox.Yes:
            #if shutting down, close the USB connection and the UI
            self.usb.closing(self.usb)
            self.closing = True
            event.accept()
        else:
            event.ignore()

    def getValues(self):
        return {}


#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************
    #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()

    #this function handles the closing of the pop-up window - it doesn't actually close, simply hides visibility.
    #this functionality allows for permanance of objects in the background
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    #this function is called on main window shutdown, and it forces the popup to close+
    def shutdown():
        return sys.exit(True)


#the main program will instantiate the window once
#if it has been instantiated, it simply puts focus on the window instead of making a second window
#modifying this function can break the main window functionality

def main():
    global windowHandle
    windowHandle = popWindow()
    return windowHandle


#the showPopUp program will show the instantiated window (which was either hidden or visible)
def showPopUp():
    windowHandle.show()

if __name__ == '__main__':
    main()

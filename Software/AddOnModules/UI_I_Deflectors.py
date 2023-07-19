import sys  # import sys module for system-level functions
import glob
import os                         # allow us to access other files
# import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QListWidget, QTableWidget, QTableWidgetItem, QGroupBox, QDoubleSpinBox, QComboBox, QHBoxLayout, QCheckBox
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
from AddOnModules import Hardware, UI_U_DataSets
import pyqtgraph as pg
import datetime
import importlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
import copy
import time

# name of the button on the main window that links to this code
buttonName = 'Deflectors'
windowHandle = None  # a handle to the window on a global scope

# this class handles the main window interactions, mainly initialization


class popWindow(QWidget):

    # ****************************************************************************************************************
    # BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
    # ****************************************************************************************************************

    # a function that users can modify to create their user interface
    def initUI(self):
        QWidget.__init__(self)
        # set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 400
        windowHeight = 300
        self.setGeometry(350, 50, windowWidth, windowHeight)

        # name the window
        self.setWindowTitle('Deflectors')

        self.mainGrid = QGridLayout()

        self.tabList = []
        self.adTabList = []
        # list that saving x, y, color, mode for every tab
        self.currentData = []
        # def the tabs
        self.tabs = QTabWidget()
        # Get Analog output pins list from hardware module
        self.AOList = list(Hardware.IO.AoNames.keys())
        # insert an empty element as new deflector default
        self.AOList.insert(0, '')

        # set up layout for deflector tabs
        self.deflectorLayout = QGridLayout()

        # set x and y input
        self.XnY = QGroupBox()
        self.xLabel = QLabel("X", self)  # Add a label called X

        self.Bx = QDoubleSpinBox()
        self.Bx.setMinimum(-10)
        self.Bx.setMaximum(10)
        self.Bx.setValue(0)
        self.Bx.setSingleStep(5)
        self.Bx.valueChanged.connect(lambda: self.updateBx())

        self.BxIncrement = QComboBox()
        self.BxIncrement.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.BxIncrement.setCurrentIndex(8)
        self.BxIncrement.currentIndexChanged.connect(self.BxIncrementChange)
        self.wobbleX = QCheckBox('wobble')
        self.wobbleX.stateChanged.connect(self.wobbleXtoggle)
        self.vbox = QHBoxLayout()
        self.vbox.addWidget(self.xLabel)
        self.vbox.addWidget(self.Bx)
        self.vbox.addWidget(self.BxIncrement)
        self.vbox.addWidget(self.wobbleX)
        self.vbox.addStretch()

        self.label6 = QLabel("Y", self)  # Add a label called Y

        self.By = QDoubleSpinBox()
        self.By.setMinimum(-10)
        self.By.setMaximum(10)
        self.By.setValue(0)
        self.By.setSingleStep(5)
        self.By.valueChanged.connect(lambda: self.updateBy())

        self.ByIncrement = QComboBox()
        self.ByIncrement.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.ByIncrement.setCurrentIndex(8)
        self.ByIncrement.currentIndexChanged.connect(self.ByIncrementChange)
        self.wobbleY = QCheckBox('wobble')
        self.wobbleY.stateChanged.connect(self.wobbleYtoggle)
        self.vbox.addWidget(self.label6)
        self.vbox.addWidget(self.By)
        self.vbox.addWidget(self.ByIncrement)
        self.vbox.addWidget(self.wobbleY)
        self.XnY.setLayout(self.vbox)

        self.deflectorLayout.addWidget(self.XnY, 0, 0)  # First slider for Bx1

        #set up ui for the wobbling mode
        self.wob = QGroupBox()
        self.feqLable = QLabel("Wobble Frequency:", self)
        self.feq = QDoubleSpinBox()
        self.feq.setMinimum(0.5)
        self.feq.setMaximum(10)
        self.feq.setSingleStep(0.1)
        self.feq.setSuffix("Hz")
        self.feq.setValue(0)
        self.feq.valueChanged.connect(self.updateFrequency)

        self.perLable = QLabel("Wobble Percentage:", self)
        self.percentage = QDoubleSpinBox()
        self.percentage.setMinimum(1)
        self.percentage.setMaximum(50)
        self.percentage.setSingleStep(1)
        self.percentage.setSuffix("%")
        self.percentage.setValue(10)
        self.percentage.valueChanged.connect(self.updatePercentage)
        


        self.wobBox = QHBoxLayout()
        self.wobBox.addWidget(self.feqLable)
        self.wobBox.addWidget(self.feq)
        self.wobBox.addStretch()
        self.wobBox.addWidget(self.perLable)
        self.wobBox.addWidget(self.percentage)
        self.wob.setLayout(self.wobBox)
        self.deflectorLayout.addWidget(self.wob, 1,0)

        # set up ui for the lower plate control
        self.lowerControl = QGroupBox("Lower Plate Control")
        self.lowerControl.setCheckable(True)
        self.lowerControl.clicked.connect(lambda: self.controlLower())
        self.x2Label = QLabel("X2", self)  # Add a label called X

        self.Bx2 = QDoubleSpinBox()
        self.Bx2.setMinimum(-10)
        self.Bx2.setMaximum(10)
        self.Bx2.setValue(0)
        self.Bx2.setSingleStep(5)
        self.Bx2.valueChanged.connect(lambda: self.updateBx2())

        self.Bx2Increment = QComboBox()
        self.Bx2Increment.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.Bx2Increment.setCurrentIndex(8)
        self.Bx2Increment.currentIndexChanged.connect(self.Bx2IncrementChange)
        self.XnY2 = QHBoxLayout()
        self.XnY2.addWidget(self.x2Label)
        self.XnY2.addWidget(self.Bx2)
        self.XnY2.addWidget(self.Bx2Increment)
        self.XnY2.addStretch()

        self.y2Label = QLabel("Y2", self)  # Add a label called Y

        self.By2 = QDoubleSpinBox()
        self.By2.setMinimum(-10)
        self.By2.setMaximum(10)
        self.By2.setValue(0)
        self.By2.setSingleStep(5)
        self.By2.valueChanged.connect(lambda: self.updateBy2())

        self.By2Increment = QComboBox()
        self.By2Increment.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.By2Increment.setCurrentIndex(8)
        self.By2Increment.currentIndexChanged.connect(self.By2IncrementChange)
        self.XnY2.addWidget(self.y2Label)
        self.XnY2.addWidget(self.By2)
        self.XnY2.addWidget(self.By2Increment)
        self.lowerControlLayout = QGridLayout()
        self.lowerControlLayout.addLayout(self.XnY2, 0, 0)

        #two buttons for save ratio
        self.save2shift = QPushButton("Save to Shift")
        self.save2shift.clicked.connect(lambda: self.saveToShift())
        self.save2tilt = QPushButton("Save To Tilt")
        self.save2tilt.clicked.connect(lambda: self.saveToTilt())
        self.saveRatioLayout = QHBoxLayout()
        self.saveRatioLayout.addWidget(self.save2shift)
        self.saveRatioLayout.addStretch()
        self.saveRatioLayout.addWidget(self.save2tilt)

        self.lowerControlLayout.addLayout(self.saveRatioLayout, 1, 0)
        self.lowerControl.setLayout(self.lowerControlLayout)
        self.lowerControl.setCheckable(True)


        self.deflectorLayout.addWidget(self.lowerControl, 2, 0)
        
        # set up ui for shift mode and tile mode toggle buttons
        self.SnT = QGroupBox()
        self.shiftMode = QPushButton('Shift Mode')
        self.shiftMode.setCheckable(True)
        self.shiftMode.setChecked(False)
        self.shiftMode.clicked.connect(lambda: self.shiftOnClick())
        self.tileMode = QPushButton('Tilt Mode')
        self.tileMode.setCheckable(True)
        self.tileMode.setChecked(False)
        self.tileMode.clicked.connect(lambda: self.tileOnClick())
        self.SnTBox = QHBoxLayout()
        self.SnTBox.addWidget(self.shiftMode)
        self.SnTBox.addStretch()
        self.SnTBox.addWidget(self.tileMode)
        self.SnT.setLayout(self.SnTBox)

        self.deflectorLayout.addWidget(self.SnT, 3, 0)

        # Empty layout for when no deflector founded in xml config file
        self.noDeflectorLayout = QGridLayout()
        self.noDeflectorLabel = QLabel('No deflector found, please create one')
        self.noDeflectorLayout.addWidget(self.noDeflectorLabel, 0, 0)

        # set up plot
        self.plotGroupBox = QGroupBox()
        self.plot = pg.PlotWidget()
        self.plot.getPlotItem().mouseDragEvent = self.mouseDragEvent
        # X and Y range, will be updated to the max voltage when loading deflectors
        self.plot.setXRange(-10, 10)
        self.plot.setYRange(-10, 10)
        # plot size
        self.plot.setFixedSize(500, 500)
        # disable mouse draging/zooming
        self.plot.setMouseEnabled(x=False, y=False)
        self.vboxPlot = QHBoxLayout()
        self.vboxPlot.addWidget(self.plot, alignment=QtCore.Qt.AlignHCenter)
        self.vboxPlot.addStretch(4)
        self.plotGroupBox.setLayout(self.vboxPlot)
        # show axis for 4 sides
        self.plot.getPlotItem().showAxis('top')
        self.plot.getPlotItem().showAxis('right')
        # show grid
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        # call updatePlot to initialize the plot
        self.updatePlot()

        # actually add the main overall grid to the popup window
        self.mainGrid.addWidget(self.tabs, 0, 0)
        self.mainGrid.addWidget(self.plotGroupBox, 1, 0)
        self.advanceBtn = QPushButton('Advanced')
        self.advanceBtn.clicked.connect(lambda: self.advancedSettings())
        self.mainGrid.addWidget(self.advanceBtn, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.mainGrid)

        # ****************************************************************************************************************
        # UI for the advanced setting window
        # ****************************************************************************************************************
        # def the window of the advance settings
        self.advancedWindows = QtWidgets.QWidget()
        self.advancedWindows.setGeometry(850, 50, windowWidth, windowHeight)
        self.advancedWindows.setWindowTitle("Deflectors Advanced Setting")
        # def the tabs for advanced settings
        self.adTabs = QTabWidget()
        # set up layout for advanced settings
        self.advancedLayout = QGridLayout()

        # set up ui for name and color
        self.nameNcolor = QGroupBox()
        self.nameLabel = QLabel("Name: ", self)  # Add a label called Name
        self.nameInput = QLineEdit()
        self.nameInput.textChanged.connect(lambda: self.updateName())

        self.nbox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.nbox.addWidget(self.nameLabel)
        self.nbox.addWidget(self.nameInput)
        self.nbox.addStretch()

        self.colorLabel = QLabel("Colour: ", self)  # Add a label called Color

        self.colorBox = QComboBox()
        self.colorList = ['', 'green', 'blue', 'gray',
                          'red', 'yellow', 'cyan', 'magenta', 'darkRed']
        self.colorBox.addItems(self.colorList)
        self.colorBox.setCurrentIndex(0)
        self.colorBox.currentIndexChanged.connect(lambda: self.updateColour())

        self.nbox.addWidget(self.colorLabel)
        self.nbox.addWidget(self.colorBox)
        self.nameNcolor.setLayout(self.nbox)

        self.advancedLayout.addWidget(self.nameNcolor, 0, 0)

        # set up ui for two offsets
        self.offsets = QGroupBox()
        self.xOffLabel = QLabel("X Offset: ", self)  # Add a label for x offset
        self.xOffInput = QLineEdit()
        self.xOffInput.textChanged.connect(lambda: self.updateXOffset())

        self.offsetsBox = QHBoxLayout()
        self.offsetsBox.addWidget(self.xOffLabel)
        self.offsetsBox.addWidget(self.xOffInput)
        self.offsetsBox.addStretch()

        self.yOffLabel = QLabel("Y Offset: ", self)  # Add a label for y offset
        self.yOffInput = QLineEdit()
        self.yOffInput.textChanged.connect(lambda: self.updateYOffset())

        self.offsetsBox.addWidget(self.yOffLabel)
        self.offsetsBox.addWidget(self.yOffInput)
        self.offsets.setLayout(self.offsetsBox)

        self.advancedLayout.addWidget(self.offsets, 1, 0)

        # set ui for votage and slope
        self.VnS = QGroupBox()
        # Add a label for x offset
        self.voltageLabel = QLabel("Votage: ", self)
        self.voltageInput = QLineEdit()
        self.voltageInput.textChanged.connect(lambda: self.updateVoltage())

        self.VnSBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.VnSBox.addWidget(self.voltageLabel)
        self.VnSBox.addWidget(self.voltageInput)
        self.VnSBox.addStretch()

        self.slopeLabel = QLabel("Slope: ", self)  # Add a label for y offset
        self.slopeInput = QLineEdit()
        self.slopeInput.textChanged.connect(lambda: self.updateSlope())

        self.VnSBox.addWidget(self.slopeLabel)
        self.VnSBox.addWidget(self.slopeInput)
        self.VnS.setLayout(self.VnSBox)

        self.advancedLayout.addWidget(self.VnS, 2, 0)

        # set up ui for upper plates
        # set pins for x
        self.upperPins = QGroupBox('Upper Plate')
        self.x1Label = QLabel("x1: ")  # Add a label called Name
        self.x1Drawer = QComboBox()
        self.x1Drawer.addItems(self.AOList)
        self.x1Drawer.setCurrentIndex(0)
        self.x1Drawer.currentIndexChanged.connect(lambda: self.updatex1())

        self.upperPinBox = QHBoxLayout()
        self.upperPinBox.addWidget(self.x1Label)
        self.upperPinBox.addWidget(self.x1Drawer)
        self.upperPinBox.addStretch()

        self.y1Label = QLabel("y1: ")  # Add a label called Color

        self.y1Drawer = QComboBox()
        self.y1Drawer.addItems(self.AOList)
        self.y1Drawer.setCurrentIndex(0)
        self.y1Drawer.currentIndexChanged.connect(lambda: self.updatey1())

        self.upperPinBox.addWidget(self.y1Label)
        self.upperPinBox.addWidget(self.y1Drawer)
        self.upperPins.setLayout(self.upperPinBox)

        self.advancedLayout.addWidget(self.upperPins, 3, 0)

        # Lower deflector pins
        # set pins for x
        self.lowerPins = QGroupBox('Lower Plate')
        self.lowerPins.setCheckable(True)
        self.lowerPins.clicked.connect(lambda: self.selectLower())
        self.x2Label = QLabel("x2: ")
        self.x2Drawer = QComboBox()
        self.x2Drawer.addItems(self.AOList)
        self.x2Drawer.setCurrentIndex(0)
        self.x2Drawer.currentIndexChanged.connect(lambda: self.updatex2())

        # box containing the first slider for controlling Bx1
        self.lowerPinBox = QHBoxLayout()
        self.lowerPinBox.addWidget(self.x2Label)
        self.lowerPinBox.addWidget(self.x2Drawer)
        self.lowerPinBox.addStretch()

        self.y2Label = QLabel("y2: ", self)  # Add a label called Color

        self.y2Drawer = QComboBox()
        self.y2Drawer.addItems(self.AOList)
        self.y2Drawer.setCurrentIndex(0)
        self.y2Drawer.currentIndexChanged.connect(lambda: self.updatey2())

        self.lowerPinBox.addWidget(self.y2Label)
        self.lowerPinBox.addWidget(self.y2Drawer)
        self.lowerPins.setLayout(self.lowerPinBox)

        self.advancedLayout.addWidget(self.lowerPins, 4, 0)
        self.lowerPins.setChecked(False)

        # set up ui for shift and tiled ratio
        self.ratios = QGroupBox()
        self.shiftXLabel = QLabel("Shift X ratio:")
        self.shiftXInput = QLineEdit()
        self.shiftXInput.textChanged.connect(lambda: self.updateShiftX())

        self.shiftBox = QHBoxLayout()
        self.shiftBox.addWidget(self.shiftXLabel)
        self.shiftBox.addWidget(self.shiftXInput)
        self.shiftBox.addStretch()

        self.shiftYLabel = QLabel("Shift Y ratio:")
        self.shiftYInput = QLineEdit()
        self.shiftYInput.textChanged.connect(lambda: self.updateShiftY())

        self.shiftBox.addWidget(self.shiftYLabel)
        self.shiftBox.addWidget(self.shiftYInput)

        self.tiltXLabel = QLabel("Tilt X ratio: ")  
        self.tiltXInput = QLineEdit()
        self.tiltXInput.textChanged.connect(lambda: self.updateTiltX())

        self.tiltBox = QHBoxLayout()
        self.tiltBox.addWidget(self.tiltXLabel)
        self.tiltBox.addWidget(self.tiltXInput)
        self.tiltBox.addStretch()

        self.tiltYLabel = QLabel("Tilt Y ratio: ")  
        self.tiltYInput = QLineEdit()
        self.tiltYInput.textChanged.connect(lambda: self.updateTiltY())

        self.tiltBox.addWidget(self.tiltYLabel)
        self.tiltBox.addWidget(self.tiltYInput)

        self.ratiosBox = QGridLayout()
        self.ratiosBox.addLayout(self.shiftBox, 0, 0)
        self.ratiosBox.addLayout(self.tiltBox, 1, 0)
        
        self.ratios.setLayout(self.ratiosBox)

        self.advancedLayout.addWidget(self.ratios, 5, 0)
        self.ratios.setDisabled(True)

        self.tabLayout = QGridLayout()
        self.tabLayout.addWidget(self.adTabs, 0, 0)

        # set up ui for back, save and add buttons
        self.backBtn = QPushButton('Back')
        self.backBtn.clicked.connect(lambda: self.back())
        self.saveBtn = QPushButton('Save')
        self.saveBtn.clicked.connect(lambda: self.saveSettings())
        self.addBtn = QPushButton('Add')
        self.addBtn.clicked.connect(lambda: self.createNewDeflector())
        self.tabLayout.addWidget(self.backBtn, 1, 0, QtCore.Qt.AlignLeft)
        self.tabLayout.addWidget(self.addBtn, 1, 0, QtCore.Qt.AlignHCenter)
        self.tabLayout.addWidget(self.saveBtn, 1, 0, QtCore.Qt.AlignRight)

        self.advancedWindows.setLayout(self.tabLayout)

        # read data from xml config file
        self.readDataFile()

        # set default for both windows
        self.tabs.setCurrentIndex(0)
        self.loadAdvancedData(0)
        # load only if there's at least one deflector, otherwise would cause bug
        if len(self.settings) > 0:
            self.loadData(0)
            self.adTabs.setCurrentIndex(0)
        # connect changing tab to update functions
        self.tabs.currentChanged.connect(
            lambda: self.loadData(self.tabs.currentIndex()))
        self.adTabs.currentChanged.connect(
            lambda: self.loadAdvancedData(self.adTabs.currentIndex()))
        self.updatePlot()

    def updateFrequency(self):
        self.currentData[self.tabs.currentIndex()]['frequency'] = self.feq.value()

    def updatePercentage(self):
        self.currentData[self.tabs.currentIndex()]['percentage'] = self.percentage.value()
    
    def wobbleXtoggle(self):
        if self.wobbleX.isChecked():
            self.wobbleXOn = True
            self.wobbleXThread = threading.Thread(name='wobbleX', target=lambda:self.wobble(self.Bx, lambda: self.wobbleXOn))
            self.xPreWobble = self.Bx.value()
            self.xPreWobbleIndex = self.tabs.currentIndex()
            self.wobbleXThread.start()
        else:
            self.wobbleXOn = False
            self.wobbleXThread.join(0)
            if self.tabs.currentIndex() == self.xPreWobbleIndex:
                self.Bx.setValue(self.xPreWobble)
            else:
                # get the value from bx and update currentdata list and plot
                self.currentData[self.xPreWobbleIndex]['x'] = self.xPreWobble
                self.updatePlot()
                # add real update from to pins
                print('update Bx for Deflector', self.xPreWobbleIndex, 'to', self.xPreWobble)
                x = round(float(self.xPreWobble), 2)

                # x times the ratio of 5(input)and real voltage then divide by slope and minus offset
                # x times the ratio of 5(input)and real voltage then divide by slope and minus offset
                x = x * 5/(int(self.settings[self.xPreWobbleIndex].find('voltage').text)) / float(
                    self.settings[self.xPreWobbleIndex].find('slope').text) - float(self.settings[self.xPreWobbleIndex].find('xOffset').text)
                Hardware.IO.setAnalog(
                    self.settings[self.xPreWobbleIndex].find('x1').text, -x)
                if self.settings[self.xPreWobbleIndex].find('hasLower').text == "True":
                    if self.shiftMode.isChecked():
                        shiftRatio = float(
                            self.settings[self.xPreWobbleIndex].find('shift').text)
                        x = x * shiftRatio
                    elif self.tileMode.isChecked():
                        tiledRatio = float(
                            self.settings[self.xPreWobbleIndex].find('tilt').text)
                        x = x * tiledRatio
                    Hardware.IO.setAnalog(
                        self.settings[self.xPreWobbleIndex].find('x2').text, -x)
                UI_U_DataSets.windowHandle.refreshDataSets()

    def wobbleYtoggle(self):
        if self.wobbleY.isChecked():
            self.wobbleYOn = True
            self.wobbleYThread = threading.Thread(name='wobbleY', target=lambda:self.wobble(self.By, lambda: self.wobbleYOn))
            self.yPreWobble = self.By.value()
            self.yPreWobbleIndex = self.tabs.currentIndex()
            self.wobbleYThread.start()
        else:
            self.wobbleYOn = False
            self.wobbleYThread.join(0)
            if self.tabs.currentIndex() == self.yPreWobbleIndex:
                self.By.setValue(self.yPreWobble)
            else:
                self.currentData[self.yPreWobbleIndex]['y'] = self.yPreWobble
                self.updatePlot()
                # add real update from to pins
                print('update By for Deflector', self.yPreWobbleIndex, 'to', self.yPreWobble)
                y = round(float(self.yPreWobble), 2)
                y = y * 5/(int(self.settings[self.yPreWobbleIndex].find('voltage').text)) / float(
                    self.settings[self.yPreWobbleIndex].find('slope').text) - float(self.settings[self.yPreWobbleIndex].find('yOffset').text)
                Hardware.IO.setAnalog(
                    self.settings[self.yPreWobbleIndex].find('y1').text, -y)
                if self.settings[self.yPreWobbleIndex].find('hasLower').text == "True":
                    if self.shiftMode.isChecked():
                        shiftRatio = float(
                            self.settings[self.yPreWobbleIndex].find('shift').text)
                        y = y * shiftRatio
                    elif self.tileMode.isChecked():
                        tiledRatio = float(
                            self.settings[self.yPreWobbleIndex].find('tilt').text)
                        y = y * tiledRatio
                    Hardware.IO.setAnalog(
                        self.settings[self.yPreWobbleIndex].find('y2').text, -y)
                UI_U_DataSets.windowHandle.refreshDataSets()

    def wobble(self, box, signal):
        data = self.settings[self.tabs.currentIndex()]
        v = int(data.find('voltage').text)
        current = box.value() 
        while signal():
            box.setValue(round(min(v,current + self.percentage.value()/100*v),2))
            time.sleep(1/self.feq.value())
            if signal():
                box.setValue(round(max(-v,current - self.percentage.value()/100*v),2))
                time.sleep(1/self.feq.value())

    '''
    Function that response to when the shift mode button is clicked
    '''

    def shiftOnClick(self):
        # if button is checked
        if self.shiftMode.isChecked():
            # update the mode in current data to shift
            self.currentData[self.tabs.currentIndex()]['mode'] = 'shift'
            # uncheck the tile mode button
            if self.tileMode.isChecked():
                self.tileMode.setChecked(False)
        else:
            # update the mode in current data to shift when the button is unchecked
            self.currentData[self.tabs.currentIndex()]['mode'] = None
        # since mode changed, needs to update Bx and By
        self.updateBx()
        self.updateBy()
    '''
    Function that response to when the tilt mode button is clicked
    '''

    def tileOnClick(self):
        # if button is checked
        if self.tileMode.isChecked():
            # update the mode in current data to tilt
            self.currentData[self.tabs.currentIndex()]['mode'] = 'tilt'
            # uncheck the shift mode button
            if self.shiftMode.isChecked():
                self.shiftMode.setChecked(False)
        else:
            # update the mode in current data to shift when the button is unchecked
            self.currentData[self.tabs.currentIndex()]['mode'] = None
        # since mode changed, needs to update Bx and By
        self.updateBx()
        self.updateBy()

    '''
    Function that response to when the check box of lower plate in advanced setting
    is checked
    '''

    def selectLower(self):
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        checked = self.lowerPins.isChecked()
        if not checked:
            # update xml file
            deflector.find('hasLower').text = 'False'
            # disable other lower y pins and ratio group box
            self.ratios.setDisabled(True)
        else:
            deflector.find('hasLower').text = 'True'
            self.ratios.setDisabled(False)

    def controlLower(self):
        checked = self.lowerControl.isChecked()
        self.currentData[self.tabs.currentIndex()]['lowerControl'] = checked
        if not checked:
            self.Bx2.setValue(self.Bx.value())
            self.By2.setValue(self.By.value())
            self.SnT.setDisabled(False)
        else:
            if self.tileMode.isChecked():
                self.tileMode.setChecked(False)
            if self.shiftMode.isChecked():
                self.shiftMode.setChecked(False)
            self.currentData[self.tabs.currentIndex()]['mode'] = None
            self.SnT.setDisabled(True)
    '''
    Function that response to when the advanced button is clicked
    '''

    def advancedSettings(self):
        # show the advanced window
        self.advancedWindows.show()
    '''
    Read xml config file, and return the root.
    '''

    def readDataFile(self):
        # check to see if the user data set file is present
        # Get the current working directory (cwd)
        cwd = os.getcwd() + '/AddOnModules/SaveFiles'
        files = os.listdir(cwd)  # Get all the files in that directory
        if not 'DeflectorSettings.xml' in files:
            print('No Setting files, will create one')
            tree = ET.Element('Settings')
            # format the entire xml file nicely so it is human readable and indented - encode it to a byte-string
            xmlString = ET.tostring(tree, 'utf-8', method='xml')
            # now decode it to an actual string
            xmlString = xmlString.decode()
            # remove all newlines because new additions don't have newlines
            xmlString = xmlString.replace('\n', '')
            # remove all double-spaces (aka portions of tabs) because new additions don't have spaces
            xmlString = xmlString.replace('  ', '')
            # use minidom (instead of elementTree) to parse in the string back into xml
            domTree = minidom.parseString(xmlString)
            # write to file
            with open(os.getcwd() + '/AddOnModules/SaveFiles/DeflectorSettings.xml', 'w') as pid:
                domTree.writexml(pid, encoding='utf-8',
                                 indent='', addindent='    ', newl='\n')
        tree = ET.parse(cwd + '/DeflectorSettings.xml')

        # get the root xml structure
        self.settings = tree.getroot()
        l = len(self.settings)
        self.tempSettings = copy.deepcopy(self.settings)
        self.loadTabs()
        # if have at least one deflector, load advanced setting, otherwise no(will create new deflector)
        if(l != 0):
            self.loadAdtabs()

    

    '''
    Function that load data into tab.
    index = the index of deflector you want to load
    '''

    def loadData(self, index):
        # if the current widget has layout, empty it
        if self.tabList[index].layout() == 0:
            QWidget().setLayout(self.tabList[index].layout())
        # set the layout
        self.tabList[index].setLayout(self.deflectorLayout)
        # get data from the xml root using the index
        data = self.settings[index]
        v = int(data.find('voltage').text)
        xOffset = float(data.find("xOffset").text)
        yOffset = float(data.find("yOffset").text)
        if self.wobbleX.isChecked():
            self.wobbleX.setChecked(False)
        if self.wobbleY.isChecked():
            self.wobbleY.setChecked(False)
        # if the last bx or by is greater than the current voltage, if we reset min and max will cause value change,
        # so we need to load the bx and by first, then set the minmax value
        x = self.currentData[index]['x']
        y = self.currentData[index]['y']
        x2 = self.currentData[index]['x2']
        y2 = self.currentData[index]['y2']
        print(x,y,x2,y2)
        self.Bx.valueChanged.disconnect()
        self.By.valueChanged.disconnect()
        self.Bx2.valueChanged.disconnect()
        self.By2.valueChanged.disconnect()
        self.Bx.setMinimum(max(round(-v + xOffset*v/5, 2), -v))
        self.By.setMinimum(max(round(-v + yOffset*v/5, 2), -v))
        self.Bx.setMaximum(min(round(v + xOffset*v/5, 2), v))
        self.By.setMaximum(min(round(v + yOffset*v/5, 2), v))
        self.Bx.setValue(x)
        self.By.setValue(y)
        self.Bx2.setMinimum(max(round(-v + xOffset*v/5, 2), -v))
        self.By2.setMinimum(max(round(-v + yOffset*v/5, 2), -v))
        self.Bx2.setMaximum(min(round(v + xOffset*v/5, 2), v))
        self.By2.setMaximum(min(round(v + yOffset*v/5, 2), v))
        self.Bx2.setValue(x2)
        self.By2.setValue(y2)
        self.feq.setValue(self.currentData[index]['frequency'])
        self.percentage.setValue(self.currentData[index]['percentage'])
        # check the setting has lower plate or not, if not disable toggle buttons
        if data.find('hasLower').text == 'True':
            self.lowerControl.setCheckable(True)
            self.lowerControl.setDisabled(False)
            if self.currentData[index]['lowerControl']:
                self.lowerControl.setChecked(True)
                self.SnT.setDisabled(True)
            else:
                self.lowerControl.setChecked(False)
                self.SnT.setDisabled(False) 
        else:
            self.lowerControl.setCheckable(False)
            self.lowerControl.setDisabled(True)
            self.SnT.setDisabled(True)
        # from the current value check the current mode and load it
        if self.currentData[index]['mode'] == 'shift':
            self.shiftMode.setChecked(True)
            self.tileMode.setChecked(False)
        elif self.currentData[index]['mode'] == 'tilt':
            self.shiftMode.setChecked(False)
            self.tileMode.setChecked(True)
        else:
            self.shiftMode.setChecked(False)
            self.tileMode.setChecked(False)
        
        self.Bx.valueChanged.connect(lambda: self.updateBx())
        self.By.valueChanged.connect(lambda: self.updateBy())
        self.Bx2.valueChanged.connect(lambda: self.updateBx2())
        self.By2.valueChanged.connect(lambda: self.updateBy2())


    '''
    Function that load data into advanced setting tab.
    index = the index of deflector you want to load
    '''

    def loadAdvancedData(self, index):
        self.adTabList[index].setLayout(self.advancedLayout)
        data = self.tempSettings[index]
        # load name
        self.nameInput.setText(data.tag)
        # load color if has
        if data.find('colour').text:
            self.colorBox.setCurrentIndex(
                self.colorList.index(data.find('colour').text))
        # load all other inputs
        self.xOffInput.setText(data.find('xOffset').text)
        self.yOffInput.setText(data.find('yOffset').text)
        self.voltageInput.setText(data.find('voltage').text)
        self.slopeInput.setText(data.find('slope').text)
        self.shiftXInput.setText(data.find('shiftX').text)
        self.tiltXInput.setText(data.find('tiltX').text)
        self.shiftYInput.setText(data.find('shiftY').text)
        self.tiltYInput.setText(data.find('tiltY').text)
        # if doesn't have pin, use the empty which index 0
        if not data.find('x1').text:
            self.x1Drawer.setCurrentIndex(0)
        # if has pin but not in the pin list, add -unfound
        elif data.find('x1').text not in self.AOList:
            self.AOList.append(data.find('x1').text + '-unfound')
            self.x1Drawer.clear()
            self.x1Drawer.addItems(self.AOList)
            self.x1Drawer.setCurrentIndex(len(self.AOList)-1)
        # load normally
        else:
            self.x1Drawer.setCurrentIndex(
                self.AOList.index(data.find('x1').text))
        # same thing for the rest of pins
        if not data.find('y1').text:
            self.y1Drawer.setCurrentIndex(0)
        elif data.find('y1').text not in self.AOList:
            self.AOList.append(data.find('y1').text + '-unfound')
            self.y1Drawer.clear()
            self.y1Drawer.addItems(self.AOList)
            self.y1Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.y1Drawer.setCurrentIndex(
                self.AOList.index(data.find('y1').text))

        if data.find('hasLower').text == 'True':
            self.lowerPins.setChecked(True)
            self.ratios.setDisabled(False)
        else:
            self.lowerPins.setChecked(False)
            self.ratios.setDisabled(True)

        if not data.find('x2').text:
            self.x2Drawer.setCurrentIndex(0)
        elif data.find('x2').text not in self.AOList:
            self.AOList.append(data.find('x2').text + '-unfound')
            self.x2Drawer.clear()
            self.x2Drawer.addItems(self.AOList)
            self.x2Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.x2Drawer.setCurrentIndex(
                self.AOList.index(data.find('x2').text))

        if not data.find('y2').text:
            self.y2Drawer.setCurrentIndex(0)
        elif data.find('y2').text not in self.AOList:
            self.AOList.append(data.find('y2').text + '-unfound')
            self.y2Drawer.clear()
            self.y2Drawer.addItems(self.AOList)
            self.y2Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.y2Drawer.setCurrentIndex(
                self.AOList.index(data.find('y2').text))

    '''
    Function that create a new deflector
    '''

    def createNewDeflector(self):
        # create a element under root
        newElement = ET.SubElement(self.tempSettings, 'New_Deflector')
        # create all attribs
        ET.SubElement(newElement, 'colour')
        ET.SubElement(newElement, 'xOffset')
        ET.SubElement(newElement, 'yOffset')
        ET.SubElement(newElement, 'voltage')
        ET.SubElement(newElement, 'slope')
        ET.SubElement(newElement, 'x1')
        ET.SubElement(newElement, 'y1')
        ET.SubElement(newElement, 'hasLower')
        ET.SubElement(newElement, 'x2')
        ET.SubElement(newElement, 'y2')
        ET.SubElement(newElement, 'shiftX')
        ET.SubElement(newElement, 'shiftY')
        ET.SubElement(newElement, 'tiltX')
        ET.SubElement(newElement, 'tiltY')
        # if len is 1, means the xml was empty, then didn;t load adtabs before, so call loadAdtabs
        if len(self.tempSettings) == 1:
            self.loadAdtabs()
        else:
            # manually add
            self.lowerPins.setChecked(False)
            newTab = QWidget()
            newTab.setLayout(self.advancedLayout)
            self.adTabList.append(newTab)
            self.adTabs.addTab(newTab, 'New_Deflector')
            self.adTabs.setCurrentIndex(len(self.adTabList)-1)
            self.clearAdvanceWindow()
            self.nameInput.setText('New_Deflector')
        print(self.tempSettings[0])
    '''
    Function that clean all fields of advanced window
    '''

    def clearAdvanceWindow(self):
        self.nameInput.clear()
        self.colorBox.setCurrentIndex(0)
        self.xOffInput.clear()
        self.yOffInput.clear()
        self.voltageInput.clear()
        self.slopeInput.clear()
        self.x1Drawer.setCurrentIndex(0)
        self.x2Drawer.setCurrentIndex(0)
        self.y1Drawer.setCurrentIndex(0)
        self.y2Drawer.setCurrentIndex(0)
        self.tiltXInput.clear()
        self.tiltYInput.clear()
        self.shiftXInput.clear()
        self.shiftYInput.clear()

    '''
    Function that save advanced settings and write it into xml
    '''

    def saveSettings(self):
        # call saveChecking to see if there's any illegal input, if so stop
        if not self.saveChecking():
            return
        reply = QMessageBox.question(
            self.advancedWindows, 'Save', "Saving new advanced setting will reset all your deflectors' data, press Yes to confirm", QMessageBox.Yes, QMessageBox.No)
        # reply = QMessageBox.Yes
        if reply == QMessageBox.Yes:
            self.saveToXML()
            self.refreshTabs()
            self.tabs.setCurrentIndex(self.tabs.currentIndex())
            self.loadData(self.tabs.currentIndex())

    def saveToXML(self):
        xmlString = ET.tostring(self.tempSettings, 'utf-8', method='xml')
        # now decode it to an actual string
        xmlString = xmlString.decode()
        # remove all newlines because new additions don't have newlines
        xmlString = xmlString.replace('\n', '')
        # remove all double-spaces (aka portions of tabs) because new additions don't have spaces
        xmlString = xmlString.replace('  ', '')
        # use minidom (instead of elementTree) to parse in the string back into xml
        domTree = minidom.parseString(xmlString)
        # write to file
        with open(os.getcwd() + '/AddOnModules/SaveFiles/DeflectorSettings.xml', 'w') as pid:
            domTree.writexml(pid, encoding='utf-8',
                                 indent='', addindent='    ', newl='\n')

        self.settings = copy.deepcopy(self.tempSettings)

    '''
    Function that check is there any illegal input before saving
    '''

    def saveChecking(self):
        colorList = []
        nameList = []

        for i in range(len(self.tempSettings)):
            name = self.tempSettings[i].tag
            color = self.tempSettings[i].find('colour').text
            slope = self.tempSettings[i].find('slope').text
            voltage = self.tempSettings[i].find('voltage').text
            xOffset = self.tempSettings[i].find('xOffset').text
            yOffset = self.tempSettings[i].find('yOffset').text
            shiftX = self.tempSettings[i].find('shiftX').text
            tiltX = self.tempSettings[i].find('tiltX').text
            shiftY = self.tempSettings[i].find('shiftY').text
            tiltY = self.tempSettings[i].find('tiltY').text
            hasLower = self.tempSettings[i].find('hasLower').text
            if len(name) > 20:
                reply = QMessageBox.question(self.advancedWindows, 'Invalid Name',
                                             "The name of deflector can't longer than 20 characters, please change the Invalid names", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if name in nameList:
                reply = QMessageBox.question(self.advancedWindows, 'Duplicate Names',
                                             "Every deflector should have a unique name, please change the duplicate names", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            else:
                nameList.append(name)
            if ' ' in name:
                reply = QMessageBox.question(self.advancedWindows, 'Invalid Name',
                                             "The name of deflector can't have space, please change the Invalid names", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if color == None or color == '':
                reply = QMessageBox.question(
                    self.advancedWindows, 'No Colours', "Every deflector should have a color, please select color for deflector has no color", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if color in colorList:
                reply = QMessageBox.question(self.advancedWindows, 'Duplicate Colours',
                                             "Every deflector should have a unique color, please change the duplicate colors", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            else:
                colorList.append(color)
            if not isnumber(slope):
                reply = QMessageBox.question(self.advancedWindows, 'Invalid Slope Input',
                                             "Slope should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if float(slope) > 2:
                reply = QMessageBox.question(self.advancedWindows, 'Invalid Slope Input',
                                             "Slope shouldn't be greater than 2, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not voltage or not isnumber(voltage):
                reply = QMessageBox.question(self.advancedWindows, 'Invalid Voltage Input',
                                             "Voltage should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not xOffset or not isnumber(xOffset):
                reply = QMessageBox.question(self.advancedWindows, 'Invalid X offset Input',
                                             "X Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not yOffset or not isnumber(yOffset):
                reply = QMessageBox.question(self.advancedWindows, 'Invalid Y offset Input',
                                             "Y Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if hasLower == True:
                if shiftX and not isnumber(shiftX):
                    reply = QMessageBox.question(self.advancedWindows, 'Invalid shift Input',
                                                "Shift X ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                    return 0
                if tiltX and not isnumber(tiltX):
                    reply = QMessageBox.question(self.advancedWindows, 'Invalid tilt Input',
                                                "Tilt X ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                    return 0
                if shiftY and not isnumber(shiftY):
                    reply = QMessageBox.question(self.advancedWindows, 'Invalid shift Input',
                                                "Shift Y ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                    return 0
                if tiltY and not isnumber(tiltY):
                    reply = QMessageBox.question(self.advancedWindows, 'Invalid tilt Input',
                                                "Tilt Y ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                    return 0

        return 1
    # ****************************************************************************************************************
    # Functions below are field updating functions
    # ****************************************************************************************************************

    def updateName(self):
        name = self.nameInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.tag = name
        self.refreshAdtabs()

    def updateColour(self):
        color = self.colorList[self.colorBox.currentIndex()]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('colour').text = color
        self.refreshAdtabs()

    def updatex1(self):
        x1 = self.AOList[self.x1Drawer.currentIndex()]
        if len(x1) > 9 and x1[-7:] == "unfound":
            x1 = x1[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('x1').text = x1

    def updatex2(self):
        x2 = self.AOList[self.x2Drawer.currentIndex()]
        if len(x2) > 9 and x2[-7:] == "unfound":
            x2 = x2[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('x2').text = x2

    def updatey1(self):
        y1 = self.AOList[self.y1Drawer.currentIndex()]
        if len(y1) > 9 and y1[-7:] == "unfound":
            y1 = y1[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('y1').text = y1

    def updatey2(self):
        y2 = self.AOList[self.y2Drawer.currentIndex()]
        if len(y2) > 9 and y2[-7:] == "unfound":
            y2 = y2[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('y2').text = y2

    def updateXOffset(self):
        x = self.xOffInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('xOffset').text = x

    def updateYOffset(self):
        y = self.yOffInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('yOffset').text = y

    def updateVoltage(self):
        v = self.voltageInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('voltage').text = v

    def updateSlope(self):
        s = self.slopeInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('slope').text = s

    def updateShiftX(self):
        s = self.shiftXInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('shiftX').text = s

    def updateShiftY(self):
        s = self.shiftYInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('shiftY').text = s
        
    def updateTiltX(self):
        t = self.tiltXInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('tiltX').text = t
    
    def updateTiltY(self):
        t = self.tiltYInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('tiltY').text = t

    def saveToTilt(self):
        if self.Bx.value() == 0:
            reply = QMessageBox.question(self.advancedWindows, 'Zero Bx',
                                             "The ratio can not be save since Bx is 0", QMessageBox.Ok, QMessageBox.Ok)
            return -1
        if self.By.value() == 0:
            reply = QMessageBox.question(self.advancedWindows, 'Zero By',
                                             "The ratio can not be save since By is 0", QMessageBox.Ok, QMessageBox.Ok) 
            return -1    
        x = round(self.Bx2.value()/self.Bx.value(), 2)
        y = round(self.By2.value()/self.By.value(), 2)

        self.tempSettings[self.tabs.currentIndex()].find("tiltX").text = str(x)
        self.tempSettings[self.tabs.currentIndex()].find("tiltY").text = str(y)
        self.saveToXML()
        if self.adTabs.currentIndex() == self.tabs.currentIndex():
            self.loadAdvancedData(self.adTabs.currentIndex())
    
    def saveToShift(self):
        if self.Bx.value() == 0:
            reply = QMessageBox.question(self.advancedWindows, 'Zero Bx',
                                             "The ratio can not be save since Bx is 0", QMessageBox.Ok, QMessageBox.Ok)
            return -1
        if self.By.value() == 0:
            reply = QMessageBox.question(self.advancedWindows, 'Zero By',
                                             "The ratio can not be save since By is 0", QMessageBox.Ok, QMessageBox.Ok) 
            return -1       
        x = round(self.Bx2.value()/self.Bx.value(), 2)
        y = round(self.By2.value()/self.By.value(), 2)

        self.tempSettings[self.tabs.currentIndex()].find("shiftX").text = str(x)
        self.tempSettings[self.tabs.currentIndex()].find("shiftY").text = str(y)
        self.saveToXML()
        if self.adTabs.currentIndex() == self.tabs.currentIndex():
            self.loadAdvancedData(self.adTabs.currentIndex())
    def updateBx(self):
        # get the value from bx and update currentdata list and plot
        v = self.Bx.value()
        self.currentData[self.tabs.currentIndex()]['x'] = v
        self.updatePlot()
        # add real update from to pins
        print('update Bx for Deflector', self.tabs.currentIndex(), 'to', v)
        x = round(float(v), 2)

        # x times the ratio of 5(input)and real voltage then divide by slope and minus offset
        # x times the ratio of 5(input)and real voltage then divide by slope and minus offset
        x = x * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(
            self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('xOffset').text)
        Hardware.IO.setAnalog(
            self.settings[self.tabs.currentIndex()].find('x1').text, -x)
        if self.settings[self.tabs.currentIndex()].find('hasLower').text == "True":
            if not self.currentData[self.tabs.currentIndex()]['lowerControl']:
                if self.shiftMode.isChecked():
                    shiftRatio = float(
                        self.settings[self.tabs.currentIndex()].find('shiftX').text)
                    v = v * shiftRatio
                elif self.tileMode.isChecked():
                    tiledRatio = float(
                        self.settings[self.tabs.currentIndex()].find('tiltX').text)
                    v = v * tiledRatio
                self.Bx2.setValue(v)
        UI_U_DataSets.windowHandle.refreshDataSets()

    def updateBy(self):
        v = self.By.value()
        self.currentData[self.tabs.currentIndex()]['y'] = v
        self.updatePlot()
        # add real update from to pins
        print('update By for Deflector', self.tabs.currentIndex(), 'to', v)
        y = round(float(v), 2)
        y = y * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(
            self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('yOffset').text)
        Hardware.IO.setAnalog(
            self.settings[self.tabs.currentIndex()].find('y1').text, -y)
        if self.settings[self.tabs.currentIndex()].find('hasLower').text == "True":
            if not self.currentData[self.tabs.currentIndex()]['lowerControl']:
                if self.shiftMode.isChecked():
                    shiftRatio = float(
                        self.settings[self.tabs.currentIndex()].find('shiftY').text)
                    v = v * shiftRatio
                elif self.tileMode.isChecked():
                    tiledRatio = float(
                        self.settings[self.tabs.currentIndex()].find('tiltY').text)
                    v = v * tiledRatio
                self.By2.setValue(v)
        UI_U_DataSets.windowHandle.refreshDataSets()

    def updateBx2(self):
        # get the value from bx and update currentdata list and plot
        v = self.Bx2.value()
        self.currentData[self.tabs.currentIndex()]['x2'] = v
        # add real update from to pins
        print('update Bx2 for Deflector', self.tabs.currentIndex(), 'to', v)
        x = round(float(v), 2)
        # x times the ratio of 5(input)and real voltage then divide by slope and minus offset
        x = x * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(
            self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('xOffset').text)
        Hardware.IO.setAnalog(
            self.settings[self.tabs.currentIndex()].find('x2').text, -x)
        UI_U_DataSets.windowHandle.refreshDataSets()

    def updateBy2(self):
        v = self.By2.value()
        self.currentData[self.tabs.currentIndex()]['y2'] = v
        # add real update from to pins
        print('update By2 for Deflector', self.tabs.currentIndex(), 'to', v)
        y = round(float(v), 2)
        y = y * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(
            self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('yOffset').text)
        Hardware.IO.setAnalog(
            self.settings[self.tabs.currentIndex()].find('y2').text, -y)
        UI_U_DataSets.windowHandle.refreshDataSets()

    def BxIncrementChange(self):
        # get the value from the spinner, turns into int then set single step of panX as it
        self.Bx.setSingleStep(float(self.BxIncrement.currentText()))

    def ByIncrementChange(self):
        # get the value from the spinner, turns into int then set single step of panY as it
        self.By.setSingleStep(float(self.ByIncrement.currentText()))

    def Bx2IncrementChange(self):
        # get the value from the spinner, turns into int then set single step of panX as it
        self.Bx2.setSingleStep(float(self.Bx2Increment.currentText()))

    def By2IncrementChange(self):
        # get the value from the spinner, turns into int then set single step of panY as it
        self.By2.setSingleStep(float(self.By2Increment.currentText()))

    def loadTabs(self):
        self.currentData.clear()
        self.tabs.clear()
        self.tabList.clear()
        maxVoltage = 0
        if len(self.settings) == 0:
            print('No Deflector found, please add one')
            emptyTab = QWidget()
            emptyTab.setLayout(self.noDeflectorLayout)
            self.tabList.append(emptyTab)
            self.tabs.addTab(emptyTab, 'No Deflector')
            self.createNewDeflector()
            return
        for i in range(len(self.settings)):
            name = self.settings[i].tag
            color = self.settings[i].find('colour').text
            maxVoltage = max(maxVoltage, int(
                self.settings[i].find('voltage').text))
            w = QWidget()
            self.currentData.append(
                {'x': 0, 'y': 0, 'x2': 0, 'y2':0, 'lowerControl': False,'colour': color, 'mode': None, 'frequency': 0.5, 'percentage': 10})
            self.tabList.append(w)
            self.tabs.addTab(w, name)
            self.tabs.tabBar().setTabTextColor(i, QtGui.QColor(color))
        self.plot.setXRange(-maxVoltage, maxVoltage)
        self.plot.setYRange(-maxVoltage, maxVoltage)

    def loadAdtabs(self):
        self.adTabs.clear()
        self.adTabList.clear()
        for i in range(len(self.tempSettings)):
            print('adtab no.'+str(i))
            name = self.tempSettings[i].tag
            color = self.tempSettings[i].find('colour').text
            aw = QWidget()
            self.adTabList.append(aw)
            self.adTabs.addTab(aw, name)
            self.adTabs.tabBar().setTabTextColor(i, QtGui.QColor(color))

    def refreshAdtabs(self):
        if (self.adTabs.count() < len(self.tempSettings)):
            while self.adTabs.count() != len(self.tempSettings):
                w = QWidget()
                self.adTabList.append(w)
                self.adTabs.addTab(w, 'temp')
        elif (self.adTabs.count() > len(self.tempSettings)):
            while self.adTabs.count() != len(self.tempSettings):
                self.adTabs.removeTab(self.adTabs.count()-1)
                self.adTabList.pop()
        for i in range(len(self.tempSettings)):
            name = self.tempSettings[i].tag
            color = self.tempSettings[i].find('colour').text
            self.adTabs.setTabText(i, name)
            self.adTabs.tabBar().setTabTextColor(i, QtGui.QColor(color))

    def refreshTabs(self):
        self.currentData.clear()
        maxVoltage = 0
        if (self.tabs.count() < len(self.settings)):
            while self.tabs.count() != len(self.settings):
                w = QWidget()
                self.tabList.append(w)
                self.tabs.addTab(w, 'temp')
                print("Adding")
        for i in range(len(self.settings)):
            name = self.settings[i].tag
            color = self.settings[i].find('colour').text
            maxVoltage = max(maxVoltage, int(
                self.settings[i].find('voltage').text))
            self.currentData.append(
                {'x': 0, 'y': 0, 'x2': 0, 'y2':0, 'lowerControl': False,'colour': color, 'mode': None, 'frequency': 0.5, 'percentage': 10})
            self.tabs.setTabText(i, name)
            self.tabs.tabBar().setTabTextColor(i, QtGui.QColor(color))
        self.plot.setXRange(-maxVoltage, maxVoltage)
        self.plot.setYRange(-maxVoltage, maxVoltage)

    def back(self):
        reply = QMessageBox.question(
            self.advancedWindows, 'Back', 'Go Back will lose all unsaved advance setting, press Yes to confirm', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.advancedWindows.close()
            self.tempSettings = copy.deepcopy(self.settings)
            if (len(self.tempSettings) == 0):
                self.createNewDeflector()
            self.refreshAdtabs()
            self.adTabs.setCurrentIndex(0)
            self.loadAdvancedData(0)

    def updatePlot(self):
        self.plot.clear()
        for i in self.currentData:
            i['plot'] = self.plot.plot([i['x']], [i['y']],
                           symbolBrush=QtGui.QColor(i['colour']), symbol='o')
    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            # We are already one step into the drag.
            # Find the point(s) at the mouse cursor when the button was first 
            # pressed:
            pos = ev.buttonDownScenePos()
            local_pos = self.plot.getPlotItem().getViewBox().mapSceneToView(pos)
            dragPoint = self.currentData[self.tabs.currentIndex()]['plot']
            new_pts = dragPoint.scatter.pointsAt(local_pos)
            if len(new_pts) == 1:
                # Store the drag point and the index of the point for future reference.
                self.dragPoint = new_pts[0]
                self.dragIndex = dragPoint.scatter.points().tolist().index(new_pts[0])
                self.dragOffset = new_pts[0].pos() - local_pos
                ev.accept()
            if len(new_pts) == 0:
                ev.ignore()
                return
            # self.dragPoint = pts[0]
            # ind = pts[0].data()[0]
            # self.dragOffset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.dragPoint = None
            self.dragIndex = -1
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return
        # We are dragging a point. Find the local position of the event.
        local_pos = self.plot.getPlotItem().getViewBox().mapSceneToView(ev.scenePos())

        # Update the point in the PlotDataItem using get/set data.
        # If we had more than one plotdataitem we would need to search/store which item
        # is has a point being moved. For this example we know it is the plot_item_control object.
        # Be sure to add in the initial drag offset to each coordinate to account for the initial mismatch.
        x = local_pos.x() + self.dragOffset.x()
        y = local_pos.y() + self.dragOffset.y()
        voltage = int(self.settings[self.tabs.currentIndex()].find('voltage').text)
        if x < -voltage:
            x = -voltage
        elif x > voltage:
            x = voltage
        self.currentData[self.tabs.currentIndex()]['x'] = x
        self.Bx.setValue(self.currentData[self.tabs.currentIndex()]['x'])
        
        if y < -voltage:
            y = -voltage
        elif y > voltage:
            y = voltage
        self.currentData[self.tabs.currentIndex()]['y'] = y
        self.By.setValue(self.currentData[self.tabs.currentIndex()]['y'])
        self.updatePlot()

        # ind = self.dragPoint.data()[0]
        # self.data['pos'][ind] = ev.pos() + self.dragOffset
        # self.updateGraph()
        ev.accept()
    # function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()

    # function to be able to load data to the user interface from the DataSets module
    def setValue(self, dname, name, value):
        for i in range(len(self.settings)):
            if(self.settings[i].tag == dname):
                self.currentData[i][name] = float(value)
                index = self.tabs.currentIndex()
                self.tabs.setCurrentIndex(i)
                self.loadData(i)
                if (i != index):
                    self.tabs.setCurrentIndex(index)
                    self.loadData(index)
                return 0
        return -1

    # function to get a value from the module
    def getValues(self):
        dic = {}
        for i in range(len(self.currentData)):
            dic[self.settings[i].tag] = {}
            dic[self.settings[i].tag]['x'] = str(
                round(self.currentData[i]['x'], 2))
            dic[self.settings[i].tag]['y'] = str(
                round(self.currentData[i]['y'], 2))
        return dic
    # this function handles the closing of the pop-up window - it doesn't actually close, simply hides visibility.
    # this functionality allows for permanance of objects in the background

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # this function is called on main window shutdown, and it forces the popup to close+
    def shutdown():
        return sys.exit(True)

# the main program will instantiate the window once
# if it has been instantiated, it simply puts focus on the window instead of making a second window
# modifying this function can break the main window functionality


def main():
    global windowHandle
    windowHandle = popWindow()
    return windowHandle


# the showPopUp program will show the instantiated window (which was either hidden or visible)


def showPopUp():
    windowHandle.show()


def isnumber(x):
    if x:
        try:
            # only integers and float converts safely
            num = float(x)
            return True
        except ValueError as e:  # not convertable to float
            return False
    return False


if __name__ == '__main__':
    main()

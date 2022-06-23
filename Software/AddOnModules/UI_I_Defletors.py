import sys  # import sys module for system-level functions
import glob
import os                         # allow us to access other files
# import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QListWidget, QTableWidget, QTableWidgetItem, QGroupBox, QDoubleSpinBox, QComboBox, QHBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
from AddOnModules import Hardware
import pyqtgraph as pg
import datetime
import importlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
import copy

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
        self.Bx.setSingleStep(0.01)
        self.Bx.valueChanged.connect(lambda: self.updateBx())

        self.BxIncrement = QComboBox()
        self.BxIncrement.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.BxIncrement.setCurrentIndex(0)
        self.BxIncrement.currentIndexChanged.connect(self.BxIncrementChange)

        self.vbox = QHBoxLayout()
        self.vbox.addWidget(self.xLabel)
        self.vbox.addWidget(self.Bx)
        self.vbox.addWidget(self.BxIncrement)
        self.vbox.addStretch()

        self.label6 = QLabel("Y", self)  # Add a label called Y

        self.By = QDoubleSpinBox()
        self.By.setMinimum(-10)
        self.By.setMaximum(10)
        self.By.setValue(0)
        self.By.setSingleStep(0.01)
        self.By.valueChanged.connect(lambda: self.updateBy())

        self.ByIncrement = QComboBox()
        self.ByIncrement.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.ByIncrement.setCurrentIndex(0)
        self.ByIncrement.currentIndexChanged.connect(self.ByIncrementChange)

        self.vbox.addWidget(self.label6)
        self.vbox.addWidget(self.By)
        self.vbox.addWidget(self.ByIncrement)
        # self.groupBox6.setLayout(self.vbox6)
        self.XnY.setLayout(self.vbox)

        self.deflectorLayout.addWidget(self.XnY, 0, 0)  # First slider for Bx1

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

        self.deflectorLayout.addWidget(self.SnT, 1, 0)

        # Empty layout for when no deflector founded in xml config file
        self.noDeflectorLayout = QGridLayout()
        self.noDeflectorLabel = QLabel('No deflector found, please create one')
        self.noDeflectorLayout.addWidget(self.noDeflectorLabel, 0, 0)

        # set up plot
        self.plotGroupBox = QGroupBox()
        self.plot = pg.PlotWidget()
        # X and Y range, will be updated to the max voltage when loading deflectors
        self.plot.setXRange(-10, 10)
        self.plot.setYRange(-10, 10)
        # plot size
        self.plot.setFixedSize(400, 400)
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

        self.lowerPinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
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
        self.shiftLable = QLabel("Shift ratio:")
        self.shiftInput = QLineEdit()
        self.shiftInput.textChanged.connect(lambda: self.updateShift())

        self.ratiosBox = QHBoxLayout()
        self.ratiosBox.addWidget(self.shiftLable)
        self.ratiosBox.addWidget(self.shiftInput)
        self.ratiosBox.addStretch()

        self.tileLabel = QLabel("Tilt ratio: ")  # Add a label for tile ratio
        self.tileInput = QLineEdit()
        self.tileInput.textChanged.connect(lambda: self.updateTile())

        self.ratiosBox.addWidget(self.tileLabel)
        self.ratiosBox.addWidget(self.tileInput)
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
        self.voltage = int(data.find('voltage').text)
        # if the last bx or by is greater than the current voltage, if we reset min and max will cause value change,
        # so we need to load the bx and by first, then set the minmax value
        if abs(self.Bx.value()) > self.voltage or abs(self.By.value()) > self.voltage:
            self.Bx.setValue(self.currentData[index]['x'])
            self.By.setValue(self.currentData[index]['y'])
            self.Bx.setMinimum(-self.voltage)
            self.By.setMinimum(-self.voltage)
            self.Bx.setMaximum(self.voltage)
            self.By.setMaximum(self.voltage)
        # otherwise, set the minmax first then set real value
        else:
            self.Bx.setMinimum(-self.voltage)
            self.By.setMinimum(-self.voltage)
            self.Bx.setMaximum(self.voltage)
            self.By.setMaximum(self.voltage)
            self.Bx.setValue(self.currentData[index]['x'])
            self.By.setValue(self.currentData[index]['y'])

        self.xOffset = float(data.find('xOffset').text)
        self.yOffset = float(data.find('yOffset').text)
        self.slope = float(data.find('slope').text)
        # set the increment index to 0 as default
        self.BxIncrement.setCurrentIndex(0)
        self.ByIncrement.setCurrentIndex(0)
        # check the setting has lower plate or not, if not disable toggle buttons
        if data.find('hasLower').text == 'True':
            self.SnT.setDisabled(False)
        else:
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
        self.shiftInput.setText(data.find('shift').text)
        self.tileInput.setText(data.find('tilt').text)
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
        ET.SubElement(newElement, 'shift')
        ET.SubElement(newElement, 'tilt')
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
            self.refreshTabs()
            self.tabs.setCurrentIndex(self.tabs.currentIndex())
            self.loadData(self.tabs.currentIndex())
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
            shift = self.tempSettings[i].find('shift').text
            print(shift)
            tilt = self.tempSettings[i].find('tilt').text
            hasLower = self.tempSettings[i].find('hasLower').text
            if len(name) > 20:
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Name',
                                             "The name of deflector can't longer than 20 characters, please change the illegal names", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if name in nameList:
                reply = QMessageBox.question(self.advancedWindows, 'Duplicate Names',
                                             "Every deflector should have a unique name, please change the duplicate names", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            else:
                nameList.append(name)
            if ' ' in name:
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Name',
                                             "The name of deflector can't have space, please change the illegal names", QMessageBox.Ok, QMessageBox.Ok)
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
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Slope Input',
                                             "Slope should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if float(slope) > 2:
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Slope Input',
                                             "Slope shouldn't be greater than 2, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not voltage or not isnumber(voltage):
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Voltage Input',
                                             "Voltage should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not xOffset or not isnumber(xOffset):
                reply = QMessageBox.question(self.advancedWindows, 'Illegal X offset Input',
                                             "X Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not yOffset or not isnumber(yOffset):
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Y offset Input',
                                             "Y Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0

            if shift and not isnumber(shift):
                reply = QMessageBox.question(self.advancedWindows, 'Illegal shift Input',
                                             "Shift ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if tilt and not isnumber(tilt):
                reply = QMessageBox.question(self.advancedWindows, 'Illegal tilt Input',
                                             "Tile ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
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

    def updateShift(self):
        s = self.shiftInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('shift').text = s

    def updateTile(self):
        t = self.tileInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('tilt').text = t

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
        x = x * 4.99/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(
            self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('xOffset').text)
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('x1').text, -round(x, 2))
        if self.settings[self.tabs.currentIndex()].find('hasLower').text == True:
            if self.shiftMode.isChecked():
                shiftRatio = float(
                    self.settings[self.tabs.currentIndex()].find('shift').text)
                x = x * shiftRatio
            elif self.tileMode.isChecked():
                tiledRatio = float(
                    self.settings[self.tabs.currentIndex()].find('tilt').text)
                x = x * tiledRatio
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('x2').text, -round(x, 2))

    def updateBy(self):
        v = self.By.value()
        self.currentData[self.tabs.currentIndex()]['y'] = v
        self.updatePlot()
        # add real update from to pins
        print('update By for Deflector', self.tabs.currentIndex(), 'to', v)
        y = y * 4.99/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(
            self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('yOffset').text)
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('y1').text, -round(y, 2))
        if self.settings[self.tabs.currentIndex()].find('hasLower').text == True:
            if self.shiftMode.isChecked():
                shiftRatio = float(
                    self.settings[self.tabs.currentIndex()].find('shift').text)
                y = y * shiftRatio
            elif self.tileMode.isChecked():
                tiledRatio = float(
                    self.settings[self.tabs.currentIndex()].find('tilt').text)
                y = y * tiledRatio
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('y2').text, -round(y, 2))

    def BxIncrementChange(self):
        # get the value from the spinner, turns into int then set single step of panX as it
        self.Bx.setSingleStep(float(self.BxIncrement.currentText()))

    def ByIncrementChange(self):
        # get the value from the spinner, turns into int then set single step of panY as it
        self.By.setSingleStep(float(self.ByIncrement.currentText()))

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
                {'x': 0, 'y': 0, 'colour': color, 'mode': None})
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
                {'x': 0, 'y': 0, 'colour': color, 'mode': None})
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
            print(i['colour'])
            self.plot.plot([i['x']], [i['y']],
                           symbolBrush=QtGui.QColor(i['colour']), symbol='o')

    # function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()

    # function to be able to load data to the user interface from the DataSets module
    def setValue(self, name, value):
        pass

    # function to get a value from the module
    def getValues(self):
        pass

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
        except ValueError as e: # not convertable to float
            return False
    return False

if __name__ == '__main__':
    main()

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
        #list that saving x, y, color, mode for every tab
        self.currentData = []
        # def the tabs
        self.tabs = QTabWidget()
        # Get Analog output pins list from hardware module
        self.AOList = list(Hardware.IO.AoNames.keys())
        #insert an empty element as new deflector default
        self.AOList.insert(0,'')

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

        #set up ui for shift mode and tile mode toggle buttons
        self.SnT = QGroupBox()
        self.shiftMode = QPushButton('Shift Mode')
        self.shiftMode.setCheckable(True)
        self.shiftMode.setChecked(False)
        self.shiftMode.clicked.connect(lambda: self.shiftOnClick())
        self.tileMode = QPushButton('Tile Mode')
        self.tileMode.setCheckable(True)
        self.tileMode.setChecked(False)
        self.tileMode.clicked.connect(lambda: self.tileOnClick())
        self.SnTBox = QHBoxLayout()
        self.SnTBox.addWidget(self.shiftMode)
        self.SnTBox.addStretch()
        self.SnTBox.addWidget(self.tileMode)
        self.SnT.setLayout(self.SnTBox)

        self.deflectorLayout.addWidget(self.SnT, 1, 0)

        #Empty layout for when no deflector founded in xml config file
        self.noDeflectorLayout = QGridLayout()
        self.noDeflectorLabel = QLabel('No deflector found, please create one')
        self.noDeflectorLayout.addWidget(self.noDeflectorLabel, 0, 0)

        #set up plot
        self.plotGroupBox = QGroupBox()
        self.plot = pg.PlotWidget()
        #X and Y range, will be updated to the max voltage when loading deflectors
        self.plot.setXRange(-10, 10)
        self.plot.setYRange(-10, 10)
        #plot size
        self.plot.setFixedSize(400, 400)
        #disable mouse draging/zooming
        self.plot.setMouseEnabled(x=False, y=False)
        self.vboxPlot = QHBoxLayout()
        self.vboxPlot.addWidget(self.plot, alignment=QtCore.Qt.AlignHCenter)
        self.vboxPlot.addStretch(4)
        self.plotGroupBox.setLayout(self.vboxPlot)
        #show axis for 4 sides
        self.plot.getPlotItem().showAxis('top')
        self.plot.getPlotItem().showAxis('right')
        #show grid
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        #call updatePlot to initialize the plot
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

        self.colorLabel = QLabel("Color: ", self)  # Add a label called Color

        self.colorBox = QComboBox()
        self.colorList = ['','green', 'blue', 'gray', 'red', 'yellow', 'cyan', 'magenta', 'darkRed']
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
        self.voltageLabel = QLabel("Votage: ", self)  # Add a label for x offset
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
        self.xPins = QGroupBox('Upper Plate')
        self.Bx1Label = QLabel("Bx1: ", self)  # Add a label called Name
        self.Bx1Drawer = QComboBox()
        self.Bx1Drawer.addItems(self.AOList)
        self.Bx1Drawer.setCurrentIndex(0)
        self.Bx1Drawer.currentIndexChanged.connect(lambda: self.updateBx1())

        self.xPinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.xPinBox.addWidget(self.Bx1Label)
        self.xPinBox.addWidget(self.Bx1Drawer)
        self.xPinBox.addStretch()

        self.Bx2Label = QLabel("Bx2: ", self)  # Add a label called Color

        self.Bx2Drawer = QComboBox()
        self.Bx2Drawer.addItems(self.AOList)
        self.Bx2Drawer.setCurrentIndex(0)
        self.Bx2Drawer.currentIndexChanged.connect(lambda: self.updateBx2())

        self.xPinBox.addWidget(self.Bx2Label)
        self.xPinBox.addWidget(self.Bx2Drawer)
        self.xPins.setLayout(self.xPinBox)

        self.advancedLayout.addWidget(self.xPins, 3, 0)

        # set pins for Y
        self.yPins = QGroupBox()
        self.By1Label = QLabel("By1: ", self)  # Add a label called Name
        self.By1Drawer = QComboBox()
        self.By1Drawer.addItems(self.AOList)
        self.By1Drawer.setCurrentIndex(0)
        self.By1Drawer.currentIndexChanged.connect(lambda: self.updateBy1())

        self.yPinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.yPinBox.addWidget(self.By1Label)
        self.yPinBox.addWidget(self.By1Drawer)
        self.yPinBox.addStretch()

        self.By2Label = QLabel("By2: ", self)  # Add a label called Color

        self.By2Drawer = QComboBox()
        self.By2Drawer.addItems(self.AOList)
        self.By2Drawer.setCurrentIndex(0)
        self.By2Drawer.currentIndexChanged.connect(lambda: self.updateBy2())

        self.yPinBox.addWidget(self.By2Label)
        self.yPinBox.addWidget(self.By2Drawer)
        self.yPins.setLayout(self.yPinBox)

        self.advancedLayout.addWidget(self.yPins, 4, 0)


        #Lower deflector pins
        # set pins for x
        self.LxPins = QGroupBox('Lower Plate')
        self.LxPins.setCheckable(True)
        self.LxPins.clicked.connect(lambda: self.selectLower())
        self.Bx3Label = QLabel("Bx3: ")
        self.Bx3Drawer = QComboBox()
        self.Bx3Drawer.addItems(self.AOList)
        self.Bx3Drawer.setCurrentIndex(0)
        self.Bx3Drawer.currentIndexChanged.connect(lambda: self.updateBx3())

        self.LxPinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.LxPinBox.addWidget(self.Bx3Label)
        self.LxPinBox.addWidget(self.Bx3Drawer)
        self.LxPinBox.addStretch()

        self.Bx4Label = QLabel("Bx4: ", self)  # Add a label called Color

        self.Bx4Drawer = QComboBox()
        self.Bx4Drawer.addItems(self.AOList)
        self.Bx4Drawer.setCurrentIndex(0)
        self.Bx4Drawer.currentIndexChanged.connect(lambda: self.updateBx4())

        self.LxPinBox.addWidget(self.Bx4Label)
        self.LxPinBox.addWidget(self.Bx4Drawer)
        self.LxPins.setLayout(self.LxPinBox)

        self.advancedLayout.addWidget(self.LxPins, 5, 0)
        self.LxPins.setChecked(False)

        # set pins for Y
        self.LyPins = QGroupBox()
        self.By3Label = QLabel("By3: ")  # Add a label called Name
        self.By3Drawer = QComboBox()
        self.By3Drawer.addItems(self.AOList)
        self.By3Drawer.setCurrentIndex(0)
        self.By3Drawer.currentIndexChanged.connect(lambda: self.updateBy3())

        self.LyPinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.LyPinBox.addWidget(self.By3Label)
        self.LyPinBox.addWidget(self.By3Drawer)
        self.LyPinBox.addStretch()

        self.By4Label = QLabel("By4: ")  # Add a label called Color

        self.By4Drawer = QComboBox()
        self.By4Drawer.addItems(self.AOList)
        self.By4Drawer.setCurrentIndex(0)
        self.By4Drawer.currentIndexChanged.connect(lambda: self.updateBy4())

        self.LyPinBox.addWidget(self.By4Label)
        self.LyPinBox.addWidget(self.By4Drawer)
        self.LyPins.setLayout(self.LyPinBox)

        self.advancedLayout.addWidget(self.LyPins, 6, 0)
        self.LyPins.setDisabled(True)

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

        self.advancedLayout.addWidget(self.ratios, 7, 0)
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

        #set default for both windows
        self.tabs.setCurrentIndex(0)
        self.loadAdvancedData(0)
        #load only if there's at least one deflector, otherwise would cause bug
        if len(self.settings) > 0:
            self.loadData(0)
            self.adTabs.setCurrentIndex(0)
        #connect changing tab to update functions
        self.tabs.currentChanged.connect(lambda: self.loadData(self.tabs.currentIndex()))
        self.adTabs.currentChanged.connect(lambda: self.loadAdvancedData(self.adTabs.currentIndex()))
        self.updatePlot()
    
    '''
    Function that response to when the shift mode button is clicked
    '''
    def shiftOnClick(self):
        # if button is checked
        if self.shiftMode.isChecked():
            #update the mode in current data to shift
            self.currentData[self.tabs.currentIndex()]['mode'] = 'shift'
            #uncheck the tile mode button
            if self.tileMode.isChecked():
                self.tileMode.setChecked(False)
        else:
            ##update the mode in current data to shift when the button is unchecked
           self.currentData[self.tabs.currentIndex()]['mode'] = None 
        #since mode changed, needs to update Bx and By
        self.updateBx()
        self.updateBy()
    '''
    Function that response to when the tilt mode button is clicked
    '''
    def tileOnClick(self):
        # if button is checked
        if self.tileMode.isChecked():
            #update the mode in current data to tilt
            self.currentData[self.tabs.currentIndex()]['mode'] = 'tile'
            #uncheck the shift mode button
            if self.shiftMode.isChecked():
                self.shiftMode.setChecked(False)
        else:
            ##update the mode in current data to shift when the button is unchecked
            self.currentData[self.tabs.currentIndex()]['mode'] = None
        #since mode changed, needs to update Bx and By 
        self.updateBx()
        self.updateBy()

    '''
    Function that response to when the check box of lower plate in advanced setting
    is checked
    ''' 
    def selectLower(self):
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        checked = self.LxPins.isChecked()
        if not checked:
            #update xml file 
            deflector.find('hasLower').text = 'False'
            #disable other lower y pins and ratio group box
            self.LyPins.setDisabled(True)
            self.ratios.setDisabled(True)
        else:
            deflector.find('hasLower').text = 'True'
            self.LyPins.setDisabled(False)
            self.ratios.setDisabled(False) 
        
    '''
    Function that response to when the advanced button is clicked
    ''' 
    def advancedSettings(self):
        #show the advanced window
        self.advancedWindows.show()
    '''
    Read xml config file, and return the root.
    '''
    def readDataFile(self):
        #check to see if the user data set file is present
        cwd = os.getcwd() + '/AddOnModules/SaveFiles'  # Get the current working directory (cwd)
        files = os.listdir(cwd)  # Get all the files in that directory
        if not 'DeflectorSettings.xml' in files:
            print('No Setting files, will create one')
            tree = ET.Element('Settings')
            #format the entire xml file nicely so it is human readable and indented - encode it to a byte-string
            xmlString = ET.tostring(tree, 'utf-8', method='xml')
            #now decode it to an actual string
            xmlString = xmlString.decode()
            #remove all newlines because new additions don't have newlines
            xmlString = xmlString.replace('\n','')
            #remove all double-spaces (aka portions of tabs) because new additions don't have spaces
            xmlString = xmlString.replace('  ','')
            #use minidom (instead of elementTree) to parse in the string back into xml
            domTree = minidom.parseString(xmlString)
            #write to file
            with open(os.getcwd() + '/AddOnModules/SaveFiles/DeflectorSettings.xml', 'w') as pid:
                domTree.writexml(pid, encoding='utf-8', indent='', addindent='    ', newl='\n')
        tree = ET.parse(cwd + '/DeflectorSettings.xml')
        
        #get the root xml structure
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
        #if the current widget has layout, empty it
        if self.tabList[index].layout() != 0:
            QWidget().setLayout(self.tabList[index].layout())
        #set the layout
        self.tabList[index].setLayout(self.deflectorLayout)
        #get data from the xml root using the index
        data = self.settings[index]
        self.voltage = int(data.find('voltage').text)
        #if the last bx or by is greater than the current voltage, if we reset min and max will cause value change,
        #so we need to load the bx and by first, then set the minmax value
        if abs(self.Bx.value()) > self.voltage or abs(self.By.value()) > self.voltage:
            self.Bx.setValue(self.currentData[index]['x'])
            self.By.setValue(self.currentData[index]['y'])
            self.Bx.setMinimum(-self.voltage)
            self.By.setMinimum(-self.voltage)
            self.Bx.setMaximum(self.voltage)
            self.By.setMaximum(self.voltage)
        #otherwise, set the minmax first then set real value
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
        #set the increment index to 0 as default
        self.BxIncrement.setCurrentIndex(0)
        self.ByIncrement.setCurrentIndex(0)
        #check the setting has lower plate or not, if not disable toggle buttons
        if data.find('hasLower').text == 'True':
            self.SnT.setDisabled(False)
        else:
            self.SnT.setDisabled(True)
        #from the current value check the current mode and load it
        if self.currentData[index]['mode'] == 'shift':
            self.shiftMode.setChecked(True)
            self.tileMode.setChecked(False)
        elif self.currentData[index]['mode'] == 'tile':
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
        #load name
        self.nameInput.setText(data.tag)
        #load color if has
        if data.find('colour').text:
            self.colorBox.setCurrentIndex(self.colorList.index(data.find('colour').text))
        #load all other inputs
        self.xOffInput.setText(data.find('xOffset').text)
        self.yOffInput.setText(data.find('yOffset').text)
        self.voltageInput.setText(data.find('voltage').text)
        self.slopeInput.setText(data.find('slope').text)
        self.shiftInput.setText(data.find('shift').text)
        self.tileInput.setText(data.find('tile').text)
        #if doesn't have pin, use the empty which index 0
        if not data.find('Bx1').text:
            self.Bx1Drawer.setCurrentIndex(0)
        #if has pin but not in the pin list, add -unfound
        elif data.find('Bx1').text not in self.AOList:
            self.AOList.append(data.find('Bx1').text + '-unfound')
            self.Bx1Drawer.clear()
            self.Bx1Drawer.addItems(self.AOList)
            self.Bx1Drawer.setCurrentIndex(len(self.AOList)-1)
        #load normally
        else:
            self.Bx1Drawer.setCurrentIndex(self.AOList.index(data.find('Bx1').text))
        #same thing for the rest of pins
        if not data.find('Bx2').text:
            self.Bx2Drawer.setCurrentIndex(0)
        elif data.find('Bx2').text not in self.AOList:
            self.AOList.append(data.find('Bx2').text + '-unfound')
            self.Bx2Drawer.clear()
            self.Bx2Drawer.addItems(self.AOList)
            self.Bx2Drawer.setCurrentIndex(len(self.AOList)-1)
        else:   
            self.Bx2Drawer.setCurrentIndex(self.AOList.index(data.find('Bx2').text))

        if not data.find('By1').text:
            self.By1Drawer.setCurrentIndex(0)
        elif data.find('By1').text not in self.AOList:
            self.AOList.append(data.find('By1').text + '-unfound')
            self.By1Drawer.clear()
            self.By1Drawer.addItems(self.AOList)
            self.By1Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.By1Drawer.setCurrentIndex(self.AOList.index(data.find('By1').text))

        if not data.find('By2').text:
            self.By2Drawer.setCurrentIndex(0)
        elif data.find('By2').text not in self.AOList:
            self.AOList.append(data.find('By2').text + '-unfound')
            self.By2Drawer.clear()
            self.By2Drawer.addItems(self.AOList)
            self.By2Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.By2Drawer.setCurrentIndex(self.AOList.index(data.find('By2').text))
        
        if data.find('hasLower').text == 'True':
            self.LxPins.setChecked(True)
            self.LyPins.setDisabled(False)
            self.ratios.setDisabled(False)
        else:
            self.LxPins.setChecked(False)
            self.LyPins.setDisabled(True)
            self.ratios.setDisabled(True)

        if not data.find('Bx3').text:
            self.Bx3Drawer.setCurrentIndex(0)
        elif data.find('Bx3').text not in self.AOList:
            self.AOList.append(data.find('Bx3').text + '-unfound')
            self.Bx3Drawer.clear()
            self.Bx3Drawer.addItems(self.AOList)
            self.Bx3Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.Bx3Drawer.setCurrentIndex(self.AOList.index(data.find('Bx3').text))

        if not data.find('Bx4').text:
            self.Bx4Drawer.setCurrentIndex(0)
        elif data.find('Bx4').text not in self.AOList:
            self.AOList.append(data.find('Bx4').text + '-unfound')
            self.Bx4Drawer.clear()
            self.Bx4Drawer.addItems(self.AOList)
            self.Bx4Drawer.setCurrentIndex(len(self.AOList)-1)
        else:   
            self.Bx4Drawer.setCurrentIndex(self.AOList.index(data.find('Bx4').text))

        if not data.find('By3').text:
            self.By3Drawer.setCurrentIndex(0)
        elif data.find('By3').text not in self.AOList:
            self.AOList.append(data.find('By3').text + '-unfound')
            self.By3Drawer.clear()
            self.By3Drawer.addItems(self.AOList)
            self.By3Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.By3Drawer.setCurrentIndex(self.AOList.index(data.find('By3').text))

        if not data.find('By4').text:
            self.By4Drawer.setCurrentIndex(0)
        elif data.find('By4').text not in self.AOList:
            self.AOList.append(data.find('By4').text + '-unfound')
            self.By4Drawer.clear()
            self.By4Drawer.addItems(self.AOList)
            self.By4Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.By4Drawer.setCurrentIndex(self.AOList.index(data.find('By2').text))

    '''
    Function that create a new deflector
    '''
    def createNewDeflector(self):
        #create a element under root
        newElement = ET.SubElement(self.tempSettings, 'New_Deflector')
        #create all attribs
        ET.SubElement(newElement, 'colour')
        ET.SubElement(newElement, 'xOffset')
        ET.SubElement(newElement, 'yOffset')
        ET.SubElement(newElement, 'voltage')
        ET.SubElement(newElement, 'slope')
        ET.SubElement(newElement, 'Bx1')
        ET.SubElement(newElement, 'Bx2')
        ET.SubElement(newElement, 'By1')
        ET.SubElement(newElement, 'By2')
        ET.SubElement(newElement, 'hasLower')
        ET.SubElement(newElement, 'Bx3')
        ET.SubElement(newElement, 'Bx4')
        ET.SubElement(newElement, 'By3')
        ET.SubElement(newElement, 'By4')
        ET.SubElement(newElement, 'shift')
        ET.SubElement(newElement, 'tile')
        #if len is 1, means the xml was empty, then didn;t load adtabs before, so call loadAdtabs
        if len(self.tempSettings) == 1:
            self.loadAdtabs()
        else:
            #manually add
            self.LxPins.setChecked(False)
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
        self.Bx1Drawer.setCurrentIndex(0)
        self.Bx2Drawer.setCurrentIndex(0)
        self.By1Drawer.setCurrentIndex(0)
        self.By2Drawer.setCurrentIndex(0)
        self.Bx3Drawer.setCurrentIndex(0)
        self.Bx4Drawer.setCurrentIndex(0)
        self.By3Drawer.setCurrentIndex(0)
        self.By4Drawer.setCurrentIndex(0)
    
    '''
    Function that save advanced settings and write it into xml
    '''

    def saveSettings(self):
        #call saveChecking to see if there's any illegal input, if so stop
        if not self.saveChecking():
            return
        reply = QMessageBox.question(self.advancedWindows, 'Save', "Saving new advanced setting will reset all your deflectors' data, press Yes to confirm", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            xmlString = ET.tostring(self.tempSettings, 'utf-8', method='xml')
            #now decode it to an actual string
            xmlString = xmlString.decode()
            #remove all newlines because new additions don't have newlines
            xmlString = xmlString.replace('\n','')
            #remove all double-spaces (aka portions of tabs) because new additions don't have spaces
            xmlString = xmlString.replace('  ','')
            #use minidom (instead of elementTree) to parse in the string back into xml
            domTree = minidom.parseString(xmlString)
            #write to file
            with open(os.getcwd() + '/AddOnModules/SaveFiles/DeflectorSettings.xml', 'w') as pid:
                domTree.writexml(pid, encoding='utf-8', indent='', addindent='    ', newl='\n')

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
            tile = self.tempSettings[i].find('tile').text
            hasLower = self.tempSettings[i].find('hasLower').text 
            if len(name) > 20:
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Name', "The name of deflector can't longer than 20 characters, please change the illegal names", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if name in nameList:
                reply = QMessageBox.question(self.advancedWindows, 'Duplicate Names', "Every deflector should have a unique name, please change the duplicate names", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            else:
                nameList.append(name)
            if ' ' in name:
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Name', "The name of deflector can't have space, please change the illegal names", QMessageBox.Ok, QMessageBox.Ok)
            if color == None or color == '':
               reply = QMessageBox.question(self.advancedWindows, 'No Colours', "Every deflector should have a color, please select color for deflector has no color", QMessageBox.Ok, QMessageBox.Ok)
               return 0
            if color in colorList:
                reply = QMessageBox.question(self.advancedWindows, 'Duplicate Colours', "Every deflector should have a unique color, please change the duplicate colors", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            else:
                colorList.append(color)
            if not slope.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Slope Input', "Slope should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if float(slope) > 2:
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Slope Input', "Slope shouldn't be greater than 2, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not voltage or not voltage.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Voltage Input', "Voltage should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not xOffset or not xOffset.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal X offset Input', "X Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not yOffset or not yOffset.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Y offset Input', "Y Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            
            if shift and not shift.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal shift Input', "Shift ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if tile and not tile.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal tile Input', "Tile ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
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

    def updateBx1(self):
        Bx1 = self.AOList[self.Bx1Drawer.currentIndex()]
        if len(Bx1) > 9 and Bx1[-7:] == "unfound":
            Bx1 = Bx1[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('Bx1').text = Bx1

    def updateBx2(self):
        Bx2 = self.AOList[self.Bx2Drawer.currentIndex()]
        if len(Bx2) > 9 and Bx2[-7:] == "unfound":
            Bx2 = Bx2[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('Bx2').text = Bx2

    def updateBy1(self):
        By1 = self.AOList[self.By1Drawer.currentIndex()]
        if len(By1) > 9 and By1[-7:] == "unfound":
            By1 = By1[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('By1').text = By1

    def updateBy2(self):
        By2 = self.AOList[self.By2Drawer.currentIndex()]
        if len(By2) > 9 and By2[-7:] == "unfound":
            By2 = By2[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('By2').text = By2
    
    def updateBx3(self):
        Bx3 = self.AOList[self.Bx1Drawer.currentIndex()]
        if len(Bx3) > 9 and Bx3[-7:] == "unfound":
            Bx3 = Bx3[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('Bx3').text = Bx3

    def updateBx4(self):
        Bx4 = self.AOList[self.Bx4Drawer.currentIndex()]
        if len(Bx4) > 9 and Bx4[-7:] == "unfound":
            Bx4 = Bx4[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('Bx4').text = Bx4

    def updateBy3(self):
        By3 = self.AOList[self.By1Drawer.currentIndex()]
        if len(By3) > 9 and By3[-7:] == "unfound":
            By3 = By3[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('By3').text = By3

    def updateBy4(self):
        By4 = self.AOList[self.By4Drawer.currentIndex()]
        if len(By4) > 9 and By4[-7:] == "unfound":
            By4 = By4[:-8]
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('By4').text = By4

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
        deflector.find('tile').text = t

    def updateBx(self):
        #get the value from bx and update currentdata list and plot
        v = self.Bx.value()
        self.currentData[self.tabs.currentIndex()]['x'] = v
        self.updatePlot()
        #add real update from to pins
        print('update Bx for Deflector', self.tabs.currentIndex(), 'to', v)
        #divide the value by two 
        x = round(round(float(v), 2)/2,2)
        #x times the ratio of 5(input)and real voltage then divide by slope and minus offset
        x = x * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('xOffset').text)
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx1').text, -round(x,2))
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx2').text, round(x,2))
        #check which mode currently is
        if self.shiftMode.isChecked():
            shiftRatio = float(self.settings[self.tabs.currentIndex()].find('shift').text)
            #apply shift ratio
            shiftedX = x * shiftRatio
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx3').text, -round(shiftedX,2))
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx4').text, round(shiftedX,2)) 
        elif self.tileMode.isChecked():
            tiledRatio = float(self.settings[self.tabs.currentIndex()].find('tile').text)
            #apply tilt ratio
            tiledX = x * tiledRatio
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx3').text, -round(tiledX,2))
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx4').text, round(tiledX,2))
        else:
            x = round(round(float(v), 2)/2,2)
            x = x * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('xOffset').text)
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx3').text, -round(x,2))
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx4').text, round(x,2))
            
    def updateBy(self):
        v = self.By.value()
        self.currentData[self.tabs.currentIndex()]['y'] = v
        self.updatePlot()
        #add real update from to pins
        print('update Bx for Deflector', self.tabs.currentIndex(), 'to', v)
        y = round(round(float(v), 2)/2,2)
        y = y * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(self.self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('yOffset').text)
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By1').text, -round(y,2))
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By2').text, round(y,2))
        if self.shiftMode.isChecked():
            shiftRatio = float(self.settings[self.tabs.currentIndex()].find('shift').text)
            shiftedY = y * shiftRatio
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By3').text, -round(shiftedY,2))
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By4').text, round(shiftedY,2)) 
        elif self.tileMode.isChecked():
            tiledRatio = float(self.settings[self.tabs.currentIndex()].find('tile').text)
            tiledY = y * tiledRatio
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By3').text, -round(tiledY,2))
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By4').text, round(tiledY,2))
        else:
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By3').text, -round(y,2))
            Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('By4').text, round(y,2))

    def BxIncrementChange(self):
        #get the value from the spinner, turns into int then set single step of panX as it
        self.Bx.setSingleStep(float(self.BxIncrement.currentText()))

    def ByIncrementChange(self):
        #get the value from the spinner, turns into int then set single step of panY as it
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
            maxVoltage = max(maxVoltage, int(self.settings[i].find('voltage').text))
            w = QWidget()
            self.currentData.append({'x':0, 'y': 0, 'colour': color, 'mode': None})
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
            while self.adtabs.count() != len(self.tempSettings):
                w = QWidget()
                self.adTabList.append(w)
                self.adTabs.addTab(w, 'temp')
        elif (self.adTabs.count() > len(self.tempSettings)):
            while self.adTabs.count() != len(self.tempSettings): 
                self.adTabs.removeTab(0)
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
        for i in range(len(self.settings)):
            name = self.settings[i].tag
            color = self.settings[i].find('colour').text
            maxVoltage = max(maxVoltage, int(self.settings[i].find('voltage').text))
            self.currentData.append({'x':0, 'y': 0, 'colour': color, 'mode': None})
            self.tabs.setTabText(i, name)
            self.tabs.tabBar().setTabTextColor(i, QtGui.QColor(color))

        


    def back(self):
        reply = QMessageBox.question(self.advancedWindows, 'Back', 'Go Back will lose all unsaved advance setting, press Yes to confirm', QMessageBox.Yes, QMessageBox.No)
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
            self.plot.plot([i['x']], [i['y']], symbolBrush=QtGui.QColor(i['colour']), symbol='o')

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


def reload_hardware():
    import hardware
    importlib.reload(hardware)

# the showPopUp program will show the instantiated window (which was either hidden or visible)


def showPopUp():
    windowHandle.show()


if __name__ == '__main__':
    main()

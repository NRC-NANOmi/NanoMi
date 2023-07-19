from audioop import reverse
import sys  # import sys module for system-level functions
import glob
import os                         # allow us to access other files
# import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QListWidget, QTableWidget, QTableWidgetItem, QGroupBox, QDoubleSpinBox, QComboBox, QHBoxLayout, QGraphicsEllipseItem
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.pyplot import angle_spectrum
from AddOnModules import Hardware, UI_U_DataSets
import pyqtgraph as pg
import datetime
import importlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
import copy
import math
# name of the button on the main window that links to this code
buttonName = 'Stigmators'
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
        windowHeight = 10
        self.setGeometry(350, 50, windowWidth, windowHeight)

        # name the window
        self.setWindowTitle('Stigmators')

        self.adTabList = []

        self.groupBoxs = []

        self.boxLayouts = []

        self.xSpinBoxs = []

        self.xIncrements = []

        self.ySpinBoxs = []

        self.yIncrements = []

        self.plots = []

        self.mainGrid = QGridLayout()
        self.setLayout(self.mainGrid)
        # Get Analog output pins list from hardware module
        self.AOList = list(Hardware.IO.AoNames.keys())
        # insert an empty element as new deflector default
        self.AOList.insert(0, '')

        # TODO:set up plot

        # actually add the main overall grid to the popup window
        self.advanceBtn = QPushButton('Advanced')
        self.advanceBtn.clicked.connect(lambda: self.advancedSettings())

        # ****************************************************************************************************************
        # UI for the advanced setting window
        # ****************************************************************************************************************
        # def the window of the advance settings
        self.advancedWindows = QtWidgets.QWidget()
        self.advancedWindows.setGeometry(850, 50, windowWidth, windowHeight)
        self.advancedWindows.setWindowTitle("Stigmators Advanced Setting")
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
        self.Pins = QGroupBox('Pins')
        self.x1Label = QLabel("x1: ", self)  # Add a label called Name
        self.x1Drawer = QComboBox()
        self.x1Drawer.addItems(self.AOList)
        self.x1Drawer.setCurrentIndex(0)
        self.x1Drawer.currentIndexChanged.connect(lambda: self.updatex1())

        self.PinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.PinBox.addWidget(self.x1Label)
        self.PinBox.addWidget(self.x1Drawer)
        self.PinBox.addStretch()

        self.y1Label = QLabel("y1: ", self)  # Add a label called Color

        self.y1Drawer = QComboBox()
        self.y1Drawer.addItems(self.AOList)
        self.y1Drawer.setCurrentIndex(0)
        self.y1Drawer.currentIndexChanged.connect(lambda: self.updatey1())

        self.PinBox.addWidget(self.y1Label)
        self.PinBox.addWidget(self.y1Drawer)
        self.Pins.setLayout(self.PinBox)

        self.advancedLayout.addWidget(self.Pins, 3, 0)

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
        self.loadAdvancedData(0)
        # load only if there's at least one deflector, otherwise would cause bug
        if len(self.settings) > 0:
            self.adTabs.setCurrentIndex(0)
        # connect changing tab to update functions
        self.adTabs.currentChanged.connect(
            lambda: self.loadAdvancedData(self.adTabs.currentIndex()))
        self.updatePlot()

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
        if not 'StigmatorSettings.xml' in files:
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
            with open(os.getcwd() + '/AddOnModules/SaveFiles/StigmatorSettings.xml', 'w') as pid:
                domTree.writexml(pid, encoding='utf-8',
                                 indent='', addindent='    ', newl='\n')
        tree = ET.parse(cwd + '/StigmatorSettings.xml')

        # get the root xml structure
        self.settings = tree.getroot()
        l = len(self.settings)
        self.tempSettings = copy.deepcopy(self.settings)
        self.loadTabs()
        # if have at least one deflector, load advanced setting, otherwise no(will create new deflector)
        if(l != 0):
            self.loadAdtabs()
        else:
            self.createNewDeflector()

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
        # if doesn't have pin, use the empty which index 0
        if not data.find('x1').text:
            self.Bx1Drawer.setCurrentIndex(0)
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
    '''
    Function that create a new deflector
    '''

    def createNewDeflector(self):
        # create a element under root
        newElement = ET.SubElement(self.tempSettings, 'New_Stigmator')
        # create all attribs
        ET.SubElement(newElement, 'colour')
        ET.SubElement(newElement, 'xOffset')
        ET.SubElement(newElement, 'yOffset')
        ET.SubElement(newElement, 'voltage')
        ET.SubElement(newElement, 'slope')
        ET.SubElement(newElement, 'x1')
        ET.SubElement(newElement, 'y1')
        # if len is 1, means the xml was empty, then didn;t load adtabs before, so call loadAdtabs
        if len(self.tempSettings) == 1:
            self.loadAdtabs()
        else:
            # manually add
            newTab = QWidget()
            newTab.setLayout(self.advancedLayout)
            self.adTabList.append(newTab)
            self.adTabs.addTab(newTab, 'New_Stigmator')
            self.adTabs.setCurrentIndex(len(self.adTabList)-1)
            self.clearAdvanceWindow()
            self.nameInput.setText('New_Stigmator')
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
        self.y1Drawer.setCurrentIndex(0)

    '''
    Function that save advanced settings and write it into xml
    '''

    def saveSettings(self):
        # call saveChecking to see if there's any illegal input, if so stop
        # if not self.saveChecking():
        #     return
        # reply = QMessageBox.question(
        #     self.advancedWindows, 'Save', "Saving new advanced setting will reset all your deflectors' data, press Yes to confirm", QMessageBox.Yes, QMessageBox.No)
        reply = QMessageBox.Yes
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
            with open(os.getcwd() + '/AddOnModules/SaveFiles/StigmatorSettings.xml', 'w') as pid:
                domTree.writexml(pid, encoding='utf-8',
                                 indent='', addindent='    ', newl='\n')

            self.settings = copy.deepcopy(self.tempSettings)
            self.loadTabs()
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

        return 1
    # ****************************************************************************************************************
    # Functions below are field updating functions
    # ****************************************************************************************************************

    def updateName(self):
        name = self.nameInput.text()
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.tag = name
        self.refreshAdtabs()

    def updateColour(self):
        color = self.colorList[self.colorBox.currentIndex()]
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.find('colour').text = color
        self.refreshAdtabs()

    def updatex1(self):
        x1 = self.AOList[self.x1Drawer.currentIndex()]
        if len(x1) > 9 and x1[-7:] == "unfound":
            x1 = x1[:-8]
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.find('x1').text = x1

    def updatey1(self):
        y1 = self.AOList[self.y1Drawer.currentIndex()]
        if len(y1) > 9 and y1[-7:] == "unfound":
            y1 = y1[:-8]
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.find('y1').text = y1

    def updateXOffset(self):
        x = self.xOffInput.text()
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.find('xOffset').text = x

    def updateYOffset(self):
        y = self.yOffInput.text()
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.find('yOffset').text = y

    def updateVoltage(self):
        v = self.voltageInput.text()
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.find('voltage').text = v

    def updateSlope(self):
        s = self.slopeInput.text()
        stigmator = self.tempSettings[self.adTabs.currentIndex()]
        stigmator.find('slope').text = s


    def updateBx(self, index):
        # get the value from bx and update currentdata list and plot
        v = self.xSpinBoxs[index].value()
        self.updatePlot()
        # add real update from to pins
        x = round(float(v), 2)
        x = x * 5/(int(self.settings[index].find('voltage').text)) / float(
            self.settings[index].find('slope').text) - float(self.settings[index].find('xOffset').text)

        Hardware.IO.setAnalog(
            self.settings[index].find('x1').text, -x)
        UI_U_DataSets.windowHandle.refreshDataSets()

    def updateBy(self, index):
        v = self.ySpinBoxs[index].value()
        self.updatePlot()
        # add real update from to pins
        y = round(float(v), 2)
        y = y * 5/(int(self.settings[index].find('voltage').text)) / float(
            self.settings[index].find('slope').text) - float(self.settings[index].find('yOffset').text)
        Hardware.IO.setAnalog(self.settings[index].find('y1').text, -y)
        UI_U_DataSets.windowHandle.refreshDataSets()


    def BxIncrementChange(self, index):
        # get the value from the spinner, turns into int then set single step of panX as it
        self.xSpinBoxs[index].setSingleStep(
            float(self.xIncrements[index].currentText()))

    def ByIncrementChange(self, index):
        # get the value from the spinner, turns into int then set single step of panY as it
        self.ySpinBoxs[index].setSingleStep(
            float(self.yIncrements[index].currentText()))

    def lambdaGenerator(self, index, function):
        return lambda: function(index)

        

    def loadTabs(self):
        self.groupBoxCopy = self.groupBoxs.copy()
        self.groupBoxs.clear()
        self.boxLayouts.clear()
        self.xSpinBoxs.clear()
        self.xIncrements.clear()
        self.ySpinBoxs.clear()
        self.yIncrements.clear()
        self.plots.clear()
        if len(self.settings) == 0:
            gb = QGroupBox()
            boxLayout = QHBoxLayout()
            label = QLabel("No Stigmator found, please add one")
            boxLayout.addWidget(label)
            gb.setLayout(boxLayout)
            self.mainGrid.addWidget(gb, 0, 0)
            self.mainGrid.addWidget(
                self.advanceBtn, 1, 0, QtCore.Qt.AlignRight)
            return
        for i in range(len(self.settings)):
            self.groupBoxs.append(QGroupBox())
            nameLabel = QLabel(self.settings[i].tag)
            nameLabel.setStyleSheet(
                'color: ' + self.settings[i].find("colour").text)
            xLabel = QLabel("X", self)  # Add a label called X
            self.xSpinBoxs.append(QDoubleSpinBox())
            v = int(self.settings[i].find("voltage").text)
            xOffset = float(self.settings[i].find("xOffset").text)
            yOffset = float(self.settings[i].find("yOffset").text) 
            self.xSpinBoxs[i].setMinimum(max(round(-v + xOffset*v/5, 2), -v))
            self.xSpinBoxs[i].setMaximum(min(round(v+ xOffset*v/5, 2), v))
            self.xSpinBoxs[i].setValue(0)
            self.xSpinBoxs[i].setSingleStep(0.01)
            self.xSpinBoxs[i].valueChanged.connect(
                self.lambdaGenerator(i, self.updateBx))
            self.xIncrements.append(QComboBox())
            self.xIncrements[i].addItems(
                ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
            self.xIncrements[i].setCurrentIndex(0)

            self.xIncrements[i].currentIndexChanged.connect(
                self.lambdaGenerator(i, self.BxIncrementChange))
            self.boxLayouts.append(QHBoxLayout())
            self.boxLayouts[i].addWidget(nameLabel)
            self.boxLayouts[i].addWidget(xLabel)
            self.boxLayouts[i].addWidget(self.xSpinBoxs[i])
            self.boxLayouts[i].addWidget(self.xIncrements[i])
            self.boxLayouts[i].addStretch()

            yLabel = QLabel("Y", self)  # Add a label called Y

            self.ySpinBoxs.append(QDoubleSpinBox())
            self.ySpinBoxs[i].setMinimum(max(round(-v+ yOffset*v/5, 2), -v))
            self.ySpinBoxs[i].setMaximum(min(round(v + yOffset*v/5, 2), v))
            self.ySpinBoxs[i].setValue(0)
            self.ySpinBoxs[i].setSingleStep(0.01)
            self.ySpinBoxs[i].valueChanged.connect(
                self.lambdaGenerator(i, self.updateBy))

            self.yIncrements.append(QComboBox())
            self.yIncrements[i].addItems(
                ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
            self.yIncrements[i].setCurrentIndex(0)
            self.yIncrements[i].currentIndexChanged.connect(
                self.lambdaGenerator(i, self.ByIncrementChange))

            self.boxLayouts[i].addWidget(yLabel)
            self.boxLayouts[i].addWidget(self.ySpinBoxs[i])
            self.boxLayouts[i].addWidget(self.yIncrements[i])
            # self.groupBox6.setLayout(self.vbox6)
            self.groupBoxs[i].setLayout(self.boxLayouts[i])

            self.mainGrid.addWidget(self.groupBoxs[i], i, 0)
            self.plots.append(pg.PlotWidget())
            # X and Y range, will be updated to the max voltage when loading deflectors
            self.plots[i].setXRange(-int(self.settings[i].find("voltage").text),
                                    int(self.settings[i].find("voltage").text))
            self.plots[i].setYRange(-int(self.settings[i].find("voltage").text),
                                    int(self.settings[i].find("voltage").text))
            # plot size
            self.plots[i].setFixedSize(200, 200)
            # disable mouse draging/zooming
            self.plots[i].setMouseEnabled(x=False, y=False)
            # show axis for 4 sides
            self.plots[i].getPlotItem().showAxis('top')
            self.plots[i].getPlotItem().showAxis('right')
            # show grids
            self.plots[i].showGrid(x=True, y=True, alpha=0.3)
            # call updatePlot to initialize the plot
            self.mainGrid.addWidget(
                self.plots[i], i, 1, alignment=QtCore.Qt.AlignHCenter)
        self.mainGrid.addWidget(self.advanceBtn, len(
            self.settings), 1, QtCore.Qt.AlignRight)
        for i in range(len(self.groupBoxCopy)):
            self.groupBoxCopy[i].setParent(None)
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
                self.adTabs.removeTab(self.adTabs.count()-1)
                self.adTabList.pop()
        for i in range(len(self.tempSettings)):
            name = self.tempSettings[i].tag
            color = self.tempSettings[i].find('colour').text
            self.adTabs.setTabText(i, name)
            self.adTabs.tabBar().setTabTextColor(i, QtGui.QColor(color))

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
        for i in range(len(self.plots)):
            x = self.xSpinBoxs[i].value()
            y = self.ySpinBoxs[i].value()
            r = int(self.settings[i].find("voltage").text)/16
            if x > 0 and y > 0:
                angle = y/(x+y) * 45
                print("angle is", angle)
                # length of the box
                l = max(x, y)/(x+y) * max(x, y)
                print("Length is", l)
                e = QGraphicsEllipseItem(-l, -r, 2*l, 2*r)
                e.setRotation(angle)
            elif y == 0 and x > 0:
                e = QGraphicsEllipseItem(-x, -r, 2*x, 2*r)
            elif x == 0 and y > 0:
                e = QGraphicsEllipseItem(-y, -r, 2*y, 2*r)
                e.setRotation(45)
            elif y == 0 and x < 0:
                e = QGraphicsEllipseItem(-x, -r, 2*x, 2*r)
                e.setRotation(90)
            elif x == 0 and y < 0:
                e = QGraphicsEllipseItem(-y, -r, 2*y, 2*r)
                e.setRotation(135)
            elif x == 0 and y == 0:
                e = QGraphicsEllipseItem(-r, -r, 2*r, 2*r)
            elif x > 0 and y < 0:
                angle = 360 - abs(y)/(x+abs(y)) * 45
                print("angle is", angle)
                # length of the box
                l = max(x, abs(y))/(x+abs(y)) * max(x, abs(y))
                print("Length is", l)
                e = QGraphicsEllipseItem(-l, -r, 2*l, 2*r)
                e.setRotation(angle)
            elif x < 0 and y > 0:
                angle = 90 - y/(abs(x)+y) * 45
                print("angle is", angle)
                # length of the box
                l = max(abs(x), y)/(abs(x)+y) * max(abs(x), y)
                print("Length is", l)
                e = QGraphicsEllipseItem(-l, -r, 2*l, 2*r)
                e.setRotation(angle)
            elif x < 0 and y < 0:
                angle = 270 + abs(y)/(abs(x)+abs(y)) * 45
                print("angle is", angle)
                # length of the box
                l = max(abs(x), abs(y))/(abs(x)+abs(y)) * max(abs(x), abs(y))
                print("Length is", l)
                e = QGraphicsEllipseItem(-l, -r, 2*l, 2*r)
                e.setRotation(angle)
            e.setPen(QtGui.QColor(self.settings[i].find('colour').text))
            self.plots[i].clear()
            self.plots[i].addItem(e)

    # function to handle initialization - mainly calls a subfunction to create the user interface

    def __init__(self):
        super().__init__()
        self.initUI()

    # function to be able to load data to the user interface from the DataSets module
    def setValue(self, sname, name, value):
        for i in range(len(self.settings)):
            if(self.settings[i].tag == sname):
                if name == 'x':
                    self.xSpinBoxs[i].setValue(float(value))
                else:
                    self.ySpinBoxs[i].setValue(float(value))
                return 0
        return -1

    # function to get a value from the module
    def getValues(self):
        dic = {}
        for i in range(len(self.settings)):
            dic[self.settings[i].tag] = {}
            dic[self.settings[i].tag]['x'] = str(round(self.xSpinBoxs[i].value(),2))
            dic[self.settings[i].tag]['y'] = str(round(self.xSpinBoxs[i].value(),2))
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


def reload_hardware():
    import hardware
    importlib.reload(hardware)

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
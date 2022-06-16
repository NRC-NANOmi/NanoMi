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

        self.mainGrid = QGridLayout()

        self.adTabList = []

        self.groupBoxs = []

        self.boxLayouts = []

        self.xSpinBoxs = []
        
        self.xIncrements = []

        self.ySpinBoxs = []

        self.yIncrements = []
        # Get Analog output pins list from hardware module
        self.AOList = list(Hardware.IO.AoNames.keys())
        # insert an empty element as new deflector default
        self.AOList.insert(0, '')


        # TODO:set up plot

        # actually add the main overall grid to the popup window
        self.advanceBtn = QPushButton('Advanced')
        self.advanceBtn.clicked.connect(lambda: self.advancedSettings())
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
        self.xPins = QGroupBox('Pins')
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
            self.currentData[self.tabs.currentIndex()]['mode'] = 'tile'
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
        checked = self.LxPins.isChecked()
        if not checked:
            # update xml file
            deflector.find('hasLower').text = 'False'
            # disable other lower y pins and ratio group box
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
        if not data.find('Bx1').text:
            self.Bx1Drawer.setCurrentIndex(0)
        # if has pin but not in the pin list, add -unfound
        elif data.find('Bx1').text not in self.AOList:
            self.AOList.append(data.find('Bx1').text + '-unfound')
            self.Bx1Drawer.clear()
            self.Bx1Drawer.addItems(self.AOList)
            self.Bx1Drawer.setCurrentIndex(len(self.AOList)-1)
        # load normally
        else:
            self.Bx1Drawer.setCurrentIndex(
                self.AOList.index(data.find('Bx1').text))
        # same thing for the rest of pins
        if not data.find('Bx2').text:
            self.Bx2Drawer.setCurrentIndex(0)
        elif data.find('Bx2').text not in self.AOList:
            self.AOList.append(data.find('Bx2').text + '-unfound')
            self.Bx2Drawer.clear()
            self.Bx2Drawer.addItems(self.AOList)
            self.Bx2Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.Bx2Drawer.setCurrentIndex(
                self.AOList.index(data.find('Bx2').text))

        if not data.find('By1').text:
            self.By1Drawer.setCurrentIndex(0)
        elif data.find('By1').text not in self.AOList:
            self.AOList.append(data.find('By1').text + '-unfound')
            self.By1Drawer.clear()
            self.By1Drawer.addItems(self.AOList)
            self.By1Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.By1Drawer.setCurrentIndex(
                self.AOList.index(data.find('By1').text))

        if not data.find('By2').text:
            self.By2Drawer.setCurrentIndex(0)
        elif data.find('By2').text not in self.AOList:
            self.AOList.append(data.find('By2').text + '-unfound')
            self.By2Drawer.clear()
            self.By2Drawer.addItems(self.AOList)
            self.By2Drawer.setCurrentIndex(len(self.AOList)-1)
        else:
            self.By2Drawer.setCurrentIndex(
                self.AOList.index(data.find('By2').text))
    

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
        ET.SubElement(newElement, 'Bx1')
        ET.SubElement(newElement, 'Bx2')
        ET.SubElement(newElement, 'By1')
        ET.SubElement(newElement, 'By2')
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
        self.Bx1Drawer.setCurrentIndex(0)
        self.Bx2Drawer.setCurrentIndex(0)
        self.By1Drawer.setCurrentIndex(0)
        self.By2Drawer.setCurrentIndex(0)

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
            shift = self.tempSettings[i].find('shift').text
            tile = self.tempSettings[i].find('tile').text
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
            if not slope.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Slope Input',
                                             "Slope should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if float(slope) > 2:
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Slope Input',
                                             "Slope shouldn't be greater than 2, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not voltage or not voltage.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Voltage Input',
                                             "Voltage should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not xOffset or not xOffset.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal X offset Input',
                                             "X Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if not yOffset or not yOffset.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal Y offset Input',
                                             "Y Offset should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0

            if shift and not shift.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal shift Input',
                                             "Shift ratio should be a number, please check your input", QMessageBox.Ok, QMessageBox.Ok)
                return 0
            if tile and not tile.isnumeric():
                reply = QMessageBox.question(self.advancedWindows, 'Illegal tile Input',
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

    def updateBx(self, index):
        pass

    def updateBy(self, index):
        pass

    def BxIncrementChange(self, index):
        # get the value from the spinner, turns into int then set single step of panX as it
        self.xSpinBoxs[index].setSingleStep(float(self.xIncrements[index].currentText()))

    def ByIncrementChange(self, index):
        # get the value from the spinner, turns into int then set single step of panY as it
        self.ySpinBoxs[index].setSingleStep(float(self.xIncrements[index].currentText()))

    def loadTabs(self):
        self.groupBoxs.clear()
        self.boxLayouts.clear()
        self.xSpinBoxs.clear()
        self.xIncrements.clear()
        self.ySpinBoxs.clear()
        self.yIncrements.clear()
        if len(self.settings) == 0:
            gb = QGroupBox()
            boxLayout = QHBoxLayout()
            label = QLabel("No Stigmator found, please add one")
            boxLayout.addWidget(label)
            gb.setLayout(boxLayout)
            self.mainGrid.addWidget(gb, 0, 0)
            self.mainGrid.addWidget(self.advanceBtn, 2, 0, QtCore.Qt.AlignRight)
            return
        for i in range(len(self.settings)):
            self.groupBoxs.append(QGroupBox())
            nameLabel = QLabel(self.settings[i].tag)
            nameLabel.setStyleSheet('color: '+ self.settings[i].find("colour").text)
            xLabel = QLabel("X", self)  # Add a label called X
            self.xSpinBoxs.append(QDoubleSpinBox())
            self.xSpinBoxs[i].setMinimum(-int(self.settings[i].find("voltage").text))
            self.xSpinBoxs[i].setMaximum(int(self.settings[i].find("voltage").text))
            self.xSpinBoxs[i].setValue(0)
            self.xSpinBoxs[i].setSingleStep(0.01)
            self.xSpinBoxs[i].valueChanged.connect(lambda: self.updateBx(i))
            self.xIncrements.append(QComboBox())
            self.xIncrements[i].addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
            self.xIncrements[i].setCurrentIndex(0)
            self.xIncrements[i].currentIndexChanged.connect(lambda: self.BxIncrementChange(i))
            self.boxLayouts.append(QHBoxLayout())
            self.boxLayouts[i].addWidget(nameLabel)
            self.boxLayouts[i].addWidget(xLabel)
            self.boxLayouts[i].addWidget(self.xSpinBoxs[i])
            self.boxLayouts[i].addWidget(self.xIncrements[i])
            self.boxLayouts[i].addStretch()

            yLabel = QLabel("Y", self)  # Add a label called Y

            self.ySpinBoxs.append(QDoubleSpinBox())
            self.ySpinBoxs[i].setMinimum(-int(self.settings[i].find("voltage").text))
            self.ySpinBoxs[i].setMaximum(int(self.settings[i].find("voltage").text))
            self.ySpinBoxs[i].setValue(0)
            self.ySpinBoxs[i].setSingleStep(0.01)
            self.ySpinBoxs[i].valueChanged.connect(lambda: self.updateBy(i))

            self.yIncrements.append(QComboBox())
            self.yIncrements[i].addItems(
                ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
            self.yIncrements[i].setCurrentIndex(0)
            self.yIncrements[i].currentIndexChanged.connect(lambda: self.ByIncrementChange(i))

            self.boxLayouts[i].addWidget(yLabel)
            self.boxLayouts[i].addWidget(self.ySpinBoxs[i])
            self.boxLayouts[i].addWidget(self.yIncrements[i])
            # self.groupBox6.setLayout(self.vbox6)
            self.groupBoxs[i].setLayout(self.boxLayouts[i])

            self.mainGrid.addWidget(self.groupBoxs[i], i, 0)
        self.mainGrid.addWidget(self.advanceBtn, len(self.settings), 0, QtCore.Qt.AlignRight) 
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
            maxVoltage = max(maxVoltage, int(
                self.settings[i].find('voltage').text))
            self.currentData.append(
                {'x': 0, 'y': 0, 'colour': color, 'mode': None})
            self.tabs.setTabText(i, name)
            self.tabs.tabBar().setTabTextColor(i, QtGui.QColor(color))

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
        pass

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
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
        self.currentData = []
        # def the tabs
        self.tabs = QTabWidget()

        self.AOList = list(Hardware.IO.AoNames.keys())
        self.AOList.insert(0,'')
        # TODO: Writing loading from xml files, then create tabs depending on the number of deflectors
        # self.testTab = QWidget()
        # self.tabs.addTab(self.testTab, 'Deflector1')
        # TODO: write changing tabs function, then connect to this
        # self.tabs.currentChanged.connect(lambda: )

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
        # TODO: Add the updateX functionality
        self.Bx.valueChanged.connect(lambda: self.updateBx())

        self.BxIncrement = QComboBox()
        # TODO: Add changable size
        self.BxIncrement.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.BxIncrement.setCurrentIndex(0)
        self.BxIncrement.currentIndexChanged.connect(self.BxIncrementChange)

        self.vbox = QHBoxLayout()  # box containing the first slider for controlling Bx1
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

        # self.testTab.setLayout(self.deflectorLayout)

        self.noDeflectorLayout = QGridLayout()
        self.noDeflectorLabel = QLabel('No deflector found, please create one')
        self.noDeflectorLayout.addWidget(self.noDeflectorLabel, 0, 0)

        self.plotGroupBox = QGroupBox()
        self.plot = pg.PlotWidget()
        self.plot.setXRange(-10, 10)
        self.plot.setYRange(-10, 10)
        self.plot.setFixedSize(400, 400)
        self.plot.setMouseEnabled(x=False, y=False)
        self.vboxPlot = QHBoxLayout()
        self.vboxPlot.addWidget(self.plot, alignment=QtCore.Qt.AlignHCenter)
        self.vboxPlot.addStretch(4)
        self.plotGroupBox.setLayout(self.vboxPlot)

        self.plot.getPlotItem().showAxis('top')
        self.plot.getPlotItem().showAxis('right')
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

        # set name and color
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
        self.colorList = ['green', 'blue', 'gray', 'red', 'yellow', 'cyan', 'magenta', 'darkRed']
        self.colorBox.addItems(self.colorList)
        self.colorBox.setCurrentIndex(0)
        self.colorBox.currentIndexChanged.connect(lambda: self.updateColour())

        self.nbox.addWidget(self.colorLabel)
        self.nbox.addWidget(self.colorBox)
        self.nameNcolor.setLayout(self.nbox)

        self.advancedLayout.addWidget(self.nameNcolor, 0, 0)

        # set two offsets
        self.offsets = QGroupBox()
        self.xOffLabel = QLabel("X Offset: ", self)  # Add a label for x offset
        self.xOffInput = QLineEdit()
        self.xOffInput.textChanged.connect(lambda: self.updateXOffset())

        # box containing the first slider for controlling Bx1
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

        # set for votage and slope
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

        # self.pinsLabel = QLabel("Pins", self)
        # self.advancedLayout.addWidget(
        #     self.pinsLabel, 3, 0, QtCore.Qt.AlignHCenter)

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

        # set up for two buttons
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


        # read data
        self.readDataFile()
        self.loadTabs()
        self.loadAdtabs()

        #set default for both windows
        self.tabs.setCurrentIndex(0)
        if len(self.settings) > 0:
            self.loadData(0)
            self.loadAdvancedData(0)
            self.adTabs.setCurrentIndex(0)
        self.tabs.currentChanged.connect(lambda: self.loadData(self.tabs.currentIndex()))
        self.adTabs.currentChanged.connect(lambda: self.loadAdvancedData(self.adTabs.currentIndex()))
        self.updatePlot()
        

    def advancedSettings(self):
        self.advancedWindows.show()

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
        else:
            #pull out the xml structure from the user data sets file
            tree = ET.parse(cwd + '/DeflectorSettings.xml')
        
        #get the root xml structure
        self.settings = tree.getroot()
        self.tempSettings = copy.deepcopy(self.settings)
        if len(self.settings) == 0:
            print('No Deflector found, please add one')
            emptyTab = QWidget()
            emptyTab.setLayout(self.noDeflectorLayout)
            self.tabs.addTab(emptyTab, 'No Deflector')
            self.createNewDeflector()

    def loadData(self, index):
        print(index)
        self.tabList[index].setLayout(self.deflectorLayout)
        data = self.settings[index]
        self.voltage = int(data.find('voltage').text)
        if abs(self.Bx.value()) > self.voltage or abs(self.By.value()) > self.voltage:
            self.Bx.setValue(self.currentData[index]['x'])
            self.By.setValue(self.currentData[index]['y'])
            self.Bx.setMinimum(-self.voltage)
            self.By.setMinimum(-self.voltage)
            self.Bx.setMaximum(self.voltage)
            self.By.setMaximum(self.voltage)
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
        self.BxIncrement.setCurrentIndex(0)
        self.ByIncrement.setCurrentIndex(0)


    def loadAdvancedData(self, index):
        self.adTabList[index].setLayout(self.advancedLayout)
        data = self.tempSettings[index]
        self.nameInput.setText(data.tag)
        if data.find('colour').text:
            self.colorBox.setCurrentIndex(self.colorList.index(data.find('colour').text))
        self.xOffInput.setText(data.find('xOffset').text)
        self.yOffInput.setText(data.find('yOffset').text)
        self.voltageInput.setText(data.find('voltage').text)
        self.slopeInput.setText(data.find('slope').text)
        #check if it's new created
        if data.find('Bx1').text:
            #check if the saved pin exists
            if data.find('Bx1').text not in self.AOList:
                self.AOList.append(data.find('Bx1').text + '-unfound')
                self.Bx1Drawer.clear()
                self.Bx1Drawer.addItems(self.AOList)
                self.Bx1Drawer.setCurrentIndex(len(self.AOList)-1)
            else:
                self.Bx1Drawer.setCurrentIndex(self.AOList.index(data.find('Bx1').text))
            if data.find('Bx2').text not in self.AOList:
                self.AOList.append(data.find('Bx2').text + '-unfound')
                self.Bx2Drawer.clear()
                self.Bx2Drawer.addItems(self.AOList)
                self.Bx2Drawer.setCurrentIndex(len(self.AOList)-1)
            else:   
                self.Bx2Drawer.setCurrentIndex(self.AOList.index(data.find('Bx2').text))
            if data.find('By1').text not in self.AOList:
                self.AOList.append(data.find('By1').text + '-unfound')
                self.By1Drawer.clear()
                self.By1Drawer.addItems(self.AOList)
                self.By1Drawer.setCurrentIndex(len(self.AOList)-1)
            else:
                self.By1Drawer.setCurrentIndex(self.AOList.index(data.find('By1').text))
            if data.find('By2').text not in self.AOList:
                self.AOList.append(data.find('By2').text + '-unfound')
                self.By2Drawer.clear()
                self.By2Drawer.addItems(self.AOList)
                self.By2Drawer.setCurrentIndex(len(self.AOList)-1)
            else:
                self.By2Drawer.setCurrentIndex(self.AOList.index(data.find('By2').text))
        else:
           self.Bx1Drawer.setCurrentIndex(0)
           self.Bx2Drawer.setCurrentIndex(0) 
           self.By1Drawer.setCurrentIndex(0) 
           self.By2Drawer.setCurrentIndex(0) 

    def createNewDeflector(self):
        newElement = ET.SubElement(self.tempSettings, 'Deflector'+str(len(self.adTabList)))
        ET.SubElement(newElement, 'colour')
        ET.SubElement(newElement, 'xOffset')
        ET.SubElement(newElement, 'yOffset')
        ET.SubElement(newElement, 'voltage')
        ET.SubElement(newElement, 'slope')
        ET.SubElement(newElement, 'Bx1')
        ET.SubElement(newElement, 'Bx2')
        ET.SubElement(newElement, 'By1')
        ET.SubElement(newElement, 'By2')

        newTab = QWidget()
        newTab.setLayout(self.advancedLayout)
        self.adTabList.append(newTab)
        self.adTabs.addTab(newTab, 'Deflector'+str(len(self.adTabList)))
        self.adTabs.setCurrentIndex(len(self.adTabList)-1)
        self.clearAdvanceWindow()
        self.nameInput.setText('Deflector'+str(len(self.adTabList)))
        print(self.tempSettings[0])

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
        self.By1Drawer.setCurrentIndex(0)

    def saveSettings(self):
        reply = QMessageBox.question(self, 'Save', "Saving new advanced setting will reset all your deflectors' data, press Yes to confirm", QMessageBox.Yes, QMessageBox.No)

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
        s = self.voltageInput.text()
        deflector = self.tempSettings[self.adTabs.currentIndex()]
        deflector.find('slope').text = s

    def updateBx(self):
        v = self.Bx.value()
        self.currentData[self.tabs.currentIndex()]['x'] = v
        self.updatePlot()
        #add real update from to pins
        print('update Bx for Deflector', self.tabs.currentIndex(), 'to', v)
        x = round(round(float(v), 2)/2,2)
        x = x * 5/(int(self.settings[self.tabs.currentIndex()].find('voltage').text)) / float(self.self.settings[self.tabs.currentIndex()].find('slope').text) - float(self.settings[self.tabs.currentIndex()].find('xOffset').text)
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx1').text, -round(x,2))
        Hardware.IO.setAnalog(self.settings[self.tabs.currentIndex()].find('Bx2').text, round(x,2))

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
        for i in range(len(self.settings)):
            name = self.settings[i].tag
            color = self.settings[i].find('colour').text
            maxVoltage = max(maxVoltage, int(self.settings[i].find('voltage').text))
            w = QWidget()
            self.currentData.append({'x':0, 'y': 0, 'colour': color})
            self.tabList.append(w)
            self.tabs.addTab(w, name)
            self.tabs.tabBar().setTabTextColor(i, QtGui.QColor(color))
        self.plot.setXRange(-maxVoltage, maxVoltage)
        self.plot.setYRange(-maxVoltage, maxVoltage)
    
    def loadAdtabs(self):
        self.adTabs.clear()
        self.adTabList.clear()
        for i in range(len(self.tempSettings)):
            name = self.tempSettings[i].tag
            color = self.tempSettings[i].find('colour').text
            aw = QWidget()
            self.adTabList.append(aw)
            self.adTabs.addTab(aw, name)
            self.adTabs.tabBar().setTabTextColor(i, QtGui.QColor(color))


    def refreshAdtabs(self):
        if (self.adTabs.count() < len(self.tempSettings)):
            while self.tabs.count() != len(self.tempSettings):
                w = QWidget()
                self.adTabList.append(w)
                self.adTabs.addTab(w, 'temp')
        for i in range(len(self.settings)):
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
            self.currentData.append({'x':0, 'y': 0, 'colour': color})
            self.tabs.setTabText(i, name)
            self.tabs.tabBar().setTabTextColor(i, QtGui.QColor(color))

        


    def back(self):
        reply = QMessageBox.question(self, 'Back', 'Go Back will lose all unsaved advance setting, press Yes to confirm', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.advancedWindows.close()
            self.tempSettings = copy.deepcopy(self.settings)
            self.refreshAdtabs()
            index = self.adTabs.currentIndex()
            self.adTabs.setCurrentIndex(index)
            self.loadAdvancedData(index)

    def updatePlot(self):
        self.plot.clear()
        for i in self.currentData:
            self.plot.plot([i['x']], [i['y']], pen=i['colour'][0], symbol='o', symbolBrush=.5)
# ****************************************************************************************************************
# BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
# ****************************************************************************************************************
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
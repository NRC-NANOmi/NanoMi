import sys  # import sys module for system-level functions
import glob
import os                         # allow us to access other files
# import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QListWidget, QTableWidget, QTableWidgetItem, QGroupBox, QDoubleSpinBox, QComboBox, QHBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import datetime
import importlib
import xml.etree.ElementTree as ET
from xml.dom import minidom

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

        # def the tabs
        self.tabs = QTabWidget()
        # TODO: Writing loading from xml files, then create tabs depending on the number of deflectors
        self.testTab = QWidget()
        self.tabs.addTab(self.testTab, 'Deflector1')
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
        # self.Bx.valueChanged.connect(lambda: self.updateBx())

        self.BxIncrement = QComboBox()
        # TODO: Add changable size
        self.BxIncrement.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.BxIncrement.setCurrentIndex(0)
        # self.BxIncrement.currentIndexChanged.connect(self.BxIncrementChange)

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
        # self.By.valueChanged.connect(lambda: self.updateBy())

        self.ByIncrement = QComboBox()
        self.ByIncrement.addItems(
            ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.ByIncrement.setCurrentIndex(0)
        # self.ByIncrement.currentIndexChanged.connect(self.ByIncrementChange)

        self.vbox.addWidget(self.label6)
        self.vbox.addWidget(self.By)
        self.vbox.addWidget(self.ByIncrement)
        # self.groupBox6.setLayout(self.vbox6)
        self.XnY.setLayout(self.vbox)

        self.deflectorLayout.addWidget(self.XnY, 0, 0)  # First slider for Bx1

        self.testTab.setLayout(self.deflectorLayout)

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
        self.adTestTab = QWidget()
        self.adTabs.addTab(self.adTestTab, 'Deflector1')
        # set up layout for advanced settings
        self.advancedLayout = QGridLayout()

        # set name and color
        self.nameNcolor = QGroupBox()
        self.nameLabel = QLabel("Name: ", self)  # Add a label called Name
        self.nameInput = QLineEdit()

        self.nbox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.nbox.addWidget(self.nameLabel)
        self.nbox.addWidget(self.nameInput)
        self.nbox.addStretch()

        self.colorLabel = QLabel("Color: ", self)  # Add a label called Color

        self.colorBox = QComboBox()
        self.colorList = ['Green', 'Blue', 'Grey', 'Red', 'Yellow', 'Orange', 'White', 'Purple']
        self.colorBox.addItems(self.colorList)
        self.colorBox.setCurrentIndex(0)

        self.nbox.addWidget(self.colorLabel)
        self.nbox.addWidget(self.colorBox)
        self.nameNcolor.setLayout(self.nbox)

        self.advancedLayout.addWidget(self.nameNcolor, 0, 0)

        # set two offsets
        self.offsets = QGroupBox()
        self.xOffLabel = QLabel("X Offset: ", self)  # Add a label for x offset
        self.xOffInput = QLineEdit()

        # box containing the first slider for controlling Bx1
        self.offsetsBox = QHBoxLayout()
        self.offsetsBox.addWidget(self.xOffLabel)
        self.offsetsBox.addWidget(self.xOffInput)
        self.offsetsBox.addStretch()

        self.yOffLabel = QLabel("Y Offset: ", self)  # Add a label for y offset
        self.yOffInput = QLineEdit()

        self.offsetsBox.addWidget(self.yOffLabel)
        self.offsetsBox.addWidget(self.yOffInput)
        self.offsets.setLayout(self.offsetsBox)

        self.advancedLayout.addWidget(self.offsets, 1, 0)

        # set for votage and slope
        self.VnS = QGroupBox()
        self.votageLabel = QLabel("Votage: ", self)  # Add a label for x offset
        self.votageInput = QLineEdit()

        self.VnSBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.VnSBox.addWidget(self.votageLabel)
        self.VnSBox.addWidget(self.votageInput)
        self.VnSBox.addStretch()

        self.slopeLabel = QLabel("Slope: ", self)  # Add a label for y offset
        self.slopeInput = QLineEdit()

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
        self.Bx1Drawer.addItems(['test'])
        self.Bx1Drawer.setCurrentIndex(0)

        self.xPinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.xPinBox.addWidget(self.Bx1Label)
        self.xPinBox.addWidget(self.Bx1Drawer)
        self.xPinBox.addStretch()

        self.Bx2Label = QLabel("Bx2: ", self)  # Add a label called Color

        self.Bx2Drawer = QComboBox()
        self.Bx2Drawer.addItems(['test'])
        self.Bx2Drawer.setCurrentIndex(0)

        self.xPinBox.addWidget(self.Bx2Label)
        self.xPinBox.addWidget(self.Bx2Drawer)
        self.xPins.setLayout(self.xPinBox)

        self.advancedLayout.addWidget(self.xPins, 3, 0)

        # set pins for Y
        self.yPins = QGroupBox()
        self.By1Label = QLabel("By1: ", self)  # Add a label called Name
        self.By1Drawer = QComboBox()
        self.By1Drawer.addItems(['test'])
        self.By1Drawer.setCurrentIndex(0)

        self.yPinBox = QHBoxLayout()  # box containing the first slider for controlling Bx1
        self.yPinBox.addWidget(self.By1Label)
        self.yPinBox.addWidget(self.By1Drawer)
        self.yPinBox.addStretch()

        self.By2Label = QLabel("By2: ", self)  # Add a label called Color

        self.By2Drawer = QComboBox()
        self.By2Drawer.addItems(['test'])
        self.By2Drawer.setCurrentIndex(0)

        self.yPinBox.addWidget(self.By2Label)
        self.yPinBox.addWidget(self.By2Drawer)
        self.yPins.setLayout(self.yPinBox)

        self.advancedLayout.addWidget(self.yPins, 4, 0)

        self.adTestTab.setLayout(self.advancedLayout)

        self.tabLayout = QGridLayout()
        self.tabLayout.addWidget(self.adTabs, 0, 0)

        # set up for two buttons
        self.backBtn = QPushButton('Back')
        self.saveBtn = QPushButton('Save')
        self.addBtn = QPushButton('Add')
        self.tabLayout.addWidget(self.backBtn, 1, 0, QtCore.Qt.AlignLeft)
        self.tabLayout.addWidget(self.addBtn, 1, 0, QtCore.Qt.AlignHCenter)
        self.tabLayout.addWidget(self.saveBtn, 1, 0, QtCore.Qt.AlignRight)

        self.advancedWindows.setLayout(self.tabLayout)


        # read data
        self.readDataFile()
        self.tabList = []
        self.adTabList = []
        for i in range(len(self.settings)):
            name = self.settings[i].attrib['name']
            w = QWidget()
            aw = QWidget()
            w.setLayout(self.deflectorLayout)
            aw.setLayout(self.advancedLayout)
            self.tabList.append(w)
            self.adTabList.append(aw)
            self.tabs.addTab(w, name)
            self.adTabs.addTab(aw, name)

        #set default for both windows
        self.tabs.setCurrentIndex(0)
        self.adTabs.setCurrentIndex(0)
        self.loadData(0)
        self.loadAdvancedData(0)
        self.tabs.currentChanged.connect(lambda: self.loadData(self.tabs.currentIndex()))
        self.adTabs.currentChanged.connect(lambda: self.loadAdvancedData(self.adTabs.currentIndex()))
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
            return
        else:
            #pull out the xml structure from the user data sets file
            tree = ET.parse(cwd + '/DeflectorSettings.xml')
        
        #get the root xml structure
        self.settings = tree.getroot()
        if len(self.settings) == 0:
            print('No Deflector found, please add one')
            self.advancedWindows.show()

    def loadData(self, index):
        data = self.settings[index]
        self.voltage = int(data.get('voltage'))
        self.Bx.setMinimum(-self.voltage)
        self.By.setMinimum(-self.voltage)
        self.Bx.setMaximum(self.voltage)
        self.By.setMaximum(self.voltage)
        self.xOffset = float(data.get('xOffset'))
        self.yOffset = float(data.get('yOffset'))
        self.slope = float(data.get('slope'))

    def loadAdvancedData(self, index):
        data = self.settings[index]
        self.nameInput.setText(data.attrib['name'])
        self.colorBox.setCurrentIndex(self.colorList.index(data.get('Coulor')))
        self.xOffInput.setText(data.get('xOffset'))
        self.yOffInput.setText(data.get('yOffset'))
        self.votageInput.setText(data.get('voltage'))
        self.slopeInput.setText(data.get('slope'))
        # TODO: load for pins





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

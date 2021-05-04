'''

NANOmi Electron Microscope Apertures Module

This code handles the apertures function, including allowing for set travel points, step sizes, and a plot showing the linear location over time.

Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
*****************************************************************************************************************
Version:            2.0 - August 28, 2020
By:                 Adam Czarnecki
Notes:              Added hardware reload functionality
*****************************************************************************************************************
Version:            1.0 - May 27, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Set up the initial module for creating the user interface.
*****************************************************************************************************************
'''

import sys                              #import sys module for system-level functions

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit
from PyQt5 import QtCore, QtGui

#import hardware
import importlib

from AddOnModules import Hardware

buttonName = 'Apertures'                #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope

import time

#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************
        
    #these variables are settable/readable by the data sets module, and must be global in the initUI function
    global data
    data = []
    
    #a function that users can modify to create their user interface
    def initUI(self):
        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 800
        windowHeight = 800
        self.setGeometry(350, 50, windowWidth, windowHeight)
        
        #define a font for the title of the UI
        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(12)
        
        #define a font for the buttons of the UI
        buttonFont = QtGui.QFont()
        buttonFont.setBold(False)
        buttonFont.setPointSize(10)
        mainGrid = QGridLayout()
        self.setLayout(mainGrid)
        
        self.zoomInBtn = QPushButton('Zoom In')
        self.zoomInBtn.setFont(titleFont)
        self.zoomInBtn.setFixedHeight(50)
        self.zoomInBtn.clicked.connect(lambda: self.zoomIn())
        mainGrid.addWidget(self.zoomInBtn, 0, 0, 1, 2)
        
        self.zoomOutBtn = QPushButton('Zoom Out')
        self.zoomOutBtn.setFont(titleFont)
        self.zoomOutBtn.setFixedHeight(50)
        self.zoomOutBtn.clicked.connect(lambda: self.zoomOut())
        mainGrid.addWidget(self.zoomOutBtn, 0, 2, 1, 2)
        
        PanXLabel = QLabel('Pan X Setting [0-5V]')
        PanXLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(PanXLabel, 1, 0)
        self.panX = QLineEdit(self)
        self.panX.setText('0')
        self.panX.setFixedWidth(100)
        self.panX.setAlignment(QtCore.Qt.AlignCenter)
        self.panX.textChanged.connect(lambda: Hardware.IO.setAnalog('PanX', self.panX.text()))
        mainGrid.addWidget(self.panX, 1, 1)
        
        PanYLabel = QLabel('Pan Y Setting [0-5V]')
        PanYLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(PanYLabel, 1, 2)
        self.panY = QLineEdit(self)
        self.panY.setText('0')
        self.panY.setFixedWidth(100)
        self.panY.setAlignment(QtCore.Qt.AlignCenter)
        self.panY.textChanged.connect(lambda: Hardware.IO.setAnalog('PanY', self.panY.text()))
        mainGrid.addWidget(self.panY, 1, 3)
        
        #name the window
        self.setWindowTitle('Aperture Motion')
        
    def zoomIn(self):
        sl = 0.001
        #time.sleep(sl)
        Hardware.IO.setDigital("UpDown",1)
        Hardware.IO.setDigital("ChipSelect",1)
        Hardware.IO.setDigital("ChipSelect",0)
        Hardware.IO.setDigital("UpDown",0)
        Hardware.IO.setDigital("UpDown",1)
        Hardware.IO.setDigital("ChipSelect",1)
        
    
    def zoomOut(self):
        sl = 0.001
        #time.sleep(sl)
        Hardware.IO.setDigital("UpDown",0)
        Hardware.IO.setDigital("ChipSelect",1)
        Hardware.IO.setDigital("ChipSelect",0)
        Hardware.IO.setDigital("UpDown",1)
        Hardware.IO.setDigital("UpDown",0)
        Hardware.IO.setDigital("ChipSelect",1)
        
#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************
    #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()
    
    #function to be able to load data to the user interface from the DataSets module
    def setValue(self, name, value):
        for varName in data:
            if name in varName:
                eval(varName + '.setText("' + str(value) + '")')
                return 0
        return -1
        
    #function to get a value from the module
    def getValues(self):
        #return a dictionary of all variable names in data, and values for those variables
        varDict = {}
        for varName in data:
            value = eval(varName + '.text()')
            if 'Set' in varName:
                varName = varName.split('Set')[0]
            varDict[varName] = value
        return varDict
    
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

def reload_hardware():
    import hardware
    importlib.reload(hardware)

#the showPopUp program will show the instantiated window (which was either hidden or visible)
def showPopUp():
    windowHandle.show()

if __name__ == '__main__':
    main()

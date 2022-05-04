'''

NANOmi Electron Microscope Electron Gun Module

This code handles setting the electron gun values appropriately.

Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
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

import importlib
from AddOnModules import Hardware

buttonName = 'Electron Gun'             #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope


#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):
#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************
    
    #these variables are settable/readable by the data sets module, and must be global in the initUI function
    global data
    data = ['GunVoltageSet']
    
    #a function that users can modify to create their user interface
    def initUI(self):
        #global variables that are modified by DataSets module
        global GunVoltageSet
        
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
        
        GunVoltageSet = QLineEdit()
        GunVoltageSet.setText('0')
        GunVoltageSet.setFixedWidth(100)
        GunVoltageSet.setAlignment(QtCore.Qt.AlignCenter)
        GunVoltageSet.textChanged.connect(lambda:self.validateAnalogOutput('GunVoltage',GunVoltageSet.text()))
        
        mainGrid.addWidget(GunVoltageSet, 0, 0)
        
        #name the window
        self.setWindowTitle('Electron Gun Settings')
        
    #sends the analog output to the hardware board, but validates it first
    def validateAnalogOutput(self, name, strValue):
        value = None
        try:
            value = float(strValue)
            if value >= 0:
                Hardware.IO.setAnalog(name, value)
        except:
            QMessageBox.question(self,'Invalid input', 'The value for setting ' + name + ' is invalid.', QMessageBox.Ok, QMessageBox.Ok)
            self.sender().setText('0')

#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************
    
    #function to be able to load data to the user interface from the DataSets module
    def setValue(self, name, value):
        #find the variable name in the data array
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

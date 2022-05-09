###COPY VERSION###
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
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QSlider
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
        windowWidth = 200
        windowHeight = 300
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

        #self.zoomInBtn = QPushButton('Zoom In')
        #self.zoomInBtn.setFont(titleFont)
        #self.zoomInBtn.setFixedHeight(50)
        #self.zoomInBtn.clicked.connect(lambda: self.zoomIn())
        #mainGrid.addWidget(self.zoomInBtn, 0, 0, 1, 2)
        
        #self.zoomOutBtn = QPushButton('Zoom Out')
        #self.zoomOutBtn.setFont(titleFont)
        #self.zoomOutBtn.setFixedHeight(50)
        #self.zoomOutBtn.clicked.connect(lambda: self.zoomOut())
        ## mainGrid.addWidget(self.zoomOutBtn, 0, 2, 1, 2)
        
        PanXLabel = QLabel('Pan X Setting [0-5V]')
        PanXLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        #PanXLabel.setFixedSize(200, 100)
        mainGrid.addWidget(PanXLabel, 0, 2, 1, 1)
        self.panX = QLineEdit(self)
        self.panX.setText('0')
        self.panX.setFixedWidth(100)
        self.panX.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.panX.textChanged.connect(lambda: Hardware.IO.setAnalog('PanX', self.panX.text()))
        mainGrid.addWidget(self.panX, 1, 2, 1, 1)
        
        PanYLabel = QLabel('Pan Y Setting [0-5V]')
        PanYLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        #PanYLabel.setFixedSize(200, 100)
        mainGrid.addWidget(PanYLabel, 2, 2, 1, 1)
        self.panY = QLineEdit(self)
        self.panY.setText('0')
        self.panY.setFixedWidth(100)
        self.panY.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.panY.textChanged.connect(lambda: Hardware.IO.setAnalog('PanY', self.panY.text()))
        mainGrid.addWidget(self.panY, 3, 2, 1, 1)
        
        #name the window
        self.setWindowTitle('Aperture Motion')
        
        #Oct 14, 2021 : these are the changes we made; added slider below and created valChanged() to send slider position via serial; this is the copy version (
        self.slider = QSlider()
        self.slider.setMinimum(8)
        self.slider.setMaximum(255)
        self.slider.setValue(127)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(8)
        self.slider.setPageStep(8)
        self.slider.setSingleStep(1)
        mainGrid.addWidget(self.slider, 0, 0, 4, 1, alignment=QtCore.Qt.AlignHCenter)
        self.slider.valueChanged.connect(self.valChanged)

        PanYLabel = QLabel('<--- Zooming Out')
        PanYLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        mainGrid.addWidget(PanYLabel, 0, 1, 1, 1)
        PanYLabel = QLabel('<--- Zooming In')
        PanYLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        mainGrid.addWidget(PanYLabel, 3, 1, 1, 1)

        self.data = {
            "panX" : self.panX,
            "panY" : self.panY,
            "zoom" : self.slider
        }
    def valChanged(self):
        Hardware.IO.setDigital("ChipSelect", True) #CS
        Hardware.IO.setDigital("SCLK", False)
        position = [int(bit) for bit in list(bin(int(self.slider.value()))[2:])]
        while len(position) < 8:
            position.insert(0,0)
        dataX = [0]+position
        dataY = [1]+position
        #print(dataX)
        #print(int("".join(str(i) for i in dataX),2))
        #print(dataY)
        bit_n = 0

        #set X-axis potentiometer position
        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect", False) #CS
        time.sleep(0.05)
        while bit_n < len(dataX):
            #print("Bit " + str(bit_n) + " = " + str(dataX[bit_n]))
            Hardware.IO.setDigital("DATA", dataX[bit_n])
            time.sleep(0.01)
            bit_n = bit_n + 1
            Hardware.IO.setDigital("SCLK", True)
            time.sleep(0.01)
            Hardware.IO.setDigital("SCLK", False)
            time.sleep(0.01)

        #print()
        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect", True) #CS
        time.sleep(0.05)

        #set Y-axis potentiometer position
        Hardware.IO.setDigital("ChipSelect", False) #CS
        time.sleep(0.05)
        bit_n = 0
        while bit_n < len(dataY):
            Hardware.IO.setDigital("DATA", dataY[bit_n])
            time.sleep(0.01)
            bit_n = bit_n + 1
            Hardware.IO.setDigital("SCLK", True)
            time.sleep(0.01)
            Hardware.IO.setDigital("SCLK", False)
            time.sleep(0.01)

        Hardware.IO.setDigital("DATA", False)
        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect", True) #CS
        time.sleep(0.05)






    #def zoomIn(self):
        #sl = 0.001
        ##time.sleep(sl)
        #Hardware.IO.setDigital("UpDown",1)
        #Hardware.IO.setDigital("ChipSelect",1)
        #Hardware.IO.setDigital("ChipSelect",0)
        #Hardware.IO.setDigital("UpDown",0)
        #Hardware.IO.setDigital("UpDown",1)
        #Hardware.IO.setDigital("ChipSelect",1)
        
    
    #def zoomOut(self):
        #sl = 0.001
        ##time.sleep(sl)
        #Hardware.IO.setDigital("UpDown",0)
        #Hardware.IO.setDigital("ChipSelect",1)
        #Hardware.IO.setDigital("ChipSelect",0)
        #Hardware.IO.setDigital("UpDown",1)
        #Hardware.IO.setDigital("UpDown",0)
        #Hardware.IO.setDigital("ChipSelect",1)
        
#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************
    #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()
    
    #function to be able to load data to the user interface from the DataSets module
    def setValue(self, name, value):
        for varName in self.data:
            if name in varName:
                if name == "zoom":
                    self.data[name].setValue(int(value))
                else:
                    self.data[name].setText(str(value))
                return 0
        return -1
        
    #function to get a value from the module
    def getValues(self):
        #return a dictionary of all variable names in data, and values for those variables
        varDict = {}
        for var in self.data:
            if var == "zoom":
                value = str(self.data[var].value())
            else:
                value = self.data[var].text()
            if value != 0:
                varDict[var] = value
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

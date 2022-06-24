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
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QSlider, QSpinBox, QComboBox, QDoubleSpinBox
from PyQt5 import QtCore, QtGui, QtGui
#import hardware
import importlib

from AddOnModules import Hardware, UI_U_DataSets
import pyqtgraph as pg
buttonName = 'Scanner'                #name of the button on the main window that links to this code
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
        windowHeight = 500
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

        PanXLabel = QLabel('Pan X Setting [0-5V]')
        PanXLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        #PanXLabel.setFixedSize(200, 100)
        mainGrid.addWidget(PanXLabel, 0, 2)

        #setting up for panX
        self.panX = QDoubleSpinBox()
        #setting value bound
        self.panX.setMinimum(0)
        self.panX.setMaximum(5)
        #set initial value
        self.panX.setValue(0)
        #set inital increncrement
        self.panX.setSingleStep(0.01)
        self.panX.valueChanged.connect(lambda: self.updatePanX())
        self.panX.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        mainGrid.addWidget(self.panX, 1, 2)

        #set the increment value selecting spinner for panX
        self.panXIncrement = QComboBox()
        #setting up increment options
        self.panXIncrement.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1'])
        #select the initial as 0.01
        self.panXIncrement.setCurrentIndex(0)
        self.panXIncrement.currentIndexChanged.connect(self.panXIncrementChange)
        mainGrid.addWidget(self.panXIncrement, 1, 3, alignment=QtCore.Qt.AlignHCenter)
        
        PanYLabel = QLabel('Pan Y Setting [0-5V]')
        PanYLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        #PanYLabel.setFixedSize(200, 100)

        mainGrid.addWidget(PanYLabel, 2, 2)

        #setting up for panX
        self.panY = QDoubleSpinBox()
        self.panY.setMinimum(0)
        self.panY.setMaximum(5)
        self.panY.setValue(0)
        self.panY.setSingleStep(0.01)
        self.panY.valueChanged.connect(lambda: self.updatePanY())
        self.panY.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        mainGrid.addWidget(self.panY, 3, 2)
        
        self.panYIncrement = QComboBox()
        self.panYIncrement.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1'])
        self.panYIncrement.setCurrentIndex(0)
        self.panYIncrement.currentIndexChanged.connect(self.panYIncrementChange)
        mainGrid.addWidget(self.panYIncrement, 3, 3, alignment=QtCore.Qt.AlignHCenter)

        #name the window
        self.setWindowTitle('Scanner')
        
        #Setting up for zoom
        self.zoom = QSpinBox()
        self.zoom.setMinimum(8)
        self.zoom.setMaximum(255)
        self.zoom.setValue(127)
        self.zoom.setSingleStep(1)
        self.zoom.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        mainGrid.addWidget(self.zoom, 1, 0)
        self.zoom.valueChanged.connect(self.valChanged)

        ZoomLabel = QLabel('Zoom Setting')
        ZoomLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        mainGrid.addWidget(ZoomLabel, 0, 0)

        self.zoomIncrement = QComboBox()
        self.zoomIncrement.addItems(['1', '2', '5', '10', '20', '50', '100'])
        self.zoomIncrement.setCurrentIndex(0)
        self.zoomIncrement.currentIndexChanged.connect(self.zoomIncrementChange)
        mainGrid.addWidget(self.zoomIncrement, 1, 1, alignment=QtCore.Qt.AlignHCenter)

        self.plot = pg.PlotWidget()
        self.plot.setXRange(0,5)
        self.plot.setYRange(0,5)
        self.plot.setFixedSize(300,300)
        self.plot.setMouseEnabled(x=False,y=False)
        mainGrid.addWidget(self.plot, 4, 0, 4, 4)
        self.updatePlot()



        self.data = {
            "panX" : self.panX,
            "panY" : self.panY,
            "zoom" : self.zoom
        }

    def updatePlot(self):
        #get the coordinate of the beam
        x = self.panX.value()
        y = self.panY.value()
        ##set the beam to the plot
        #self.plot.plot([x], [y], clear=True, symbol='o', symbolBrush=.5)
        #get the length of the square
        length = (self.zoom.value()+1)/256 * 5

        #coords of left bottom node
        lbX = x - length/2
        lbY = y - length/2
        square_item = Square(QtCore.QRectF(lbX,lbY, length, length))
        self.plot.clear()
        self.plot.addItem(square_item)




    def zoomIncrementChange(self):
        #get the value from the spinner, turns into int then set single step of zoom as it
        self.zoom.setSingleStep(int(self.zoomIncrement.currentText()))

    def panXIncrementChange(self):
        #get the value from the spinner, turns into int then set single step of panX as it
        self.panX.setSingleStep(float(self.panXIncrement.currentText()))

    def panYIncrementChange(self):
        #get the value from the spinner, turns into int then set single step of panY as it
        self.panY.setSingleStep(float(self.panYIncrement.currentText()))

    def updatePanX(self):
        Hardware.IO.setAnalog('PanX', self.panX.value())
        self.updatePlot()
        UI_U_DataSets.windowHandle.refreshDataSets()

    def updatePanY(self):
        Hardware.IO.setAnalog('PanY', self.panY.value())
        self.updatePlot()
        UI_U_DataSets.windowHandle.refreshDataSets()

    def valChanged(self):
        self.updatePlot()
        Hardware.IO.setDigital("ChipSelect", True) #CS
        Hardware.IO.setDigital("SCLK", False)
        position = [int(bit) for bit in list(bin(int(self.zoom.value()))[2:])]
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
        UI_U_DataSets.windowHandle.refreshDataSets()


        
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
                self.data[name].setValue(float(value))
                return 0
        return -1
        
    #function to get a value from the module
    def getValues(self):
        #return a dictionary of all variable names in data, and values for those variables
        varDict = {}
        for var in self.data:
            value = str(round(self.data[var].value(),2))
            if value != '127':
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

class Square(pg.GraphicsObject):
    def __init__(self, rect, parent=None):
        super().__init__(parent)
        self.__rect = rect
        self.picture = QtGui.QPicture()
        self.__generate_picture()

    @property
    def rect(self):
        return self.__rect

    def __generate_picture(self):
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen('w'))
        painter.setBrush(pg.mkBrush('g'))
        painter.drawRect(self.rect)
        painter.end()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

if __name__ == '__main__':
    main()

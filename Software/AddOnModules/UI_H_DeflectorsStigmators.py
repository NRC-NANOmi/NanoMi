'''

NANOmi Electron Microscope Deflectors and Stigmators Module

This code handles setting the deflector and stigmator plates through the microscope column, as well as displaying feedback on current voltages. A linear plot is also available that will display chosen values over time.

Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
*****************************************************************************************************************
Version:            3.0 - January 26, 2021
By:                 Darren Homeniuk, P.Eng.
Notes:              Started using a deflector board for control; set up the first XY. Built a raster scan ability       
                    for slow image acquisition.
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
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QGraphicsView, QGraphicsScene
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QCategoryAxis
from PyQt5.QtCore import QPoint
from PyQt5 import QtCore, QtGui

from time import *
from datetime import datetime
from AddOnModules import UI_U_DataSets as DataSets
try:
    from numpy import *
except ImportError:
    print('NumPy is not installed.')

try:
    from PIL import Image
except ImportError:
    print('PIL not available.')
    
import matplotlib.pyplot as plt


import importlib
# import necessary aspects of the hardware module
from AddOnModules import Hardware

buttonName = 'Deflectors + Stigmators'  #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope

#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************
        
    #these variables are settable/readable by the data sets module, and must be global in the initUI function
    global data
    data = ['D1XSet', 'D1YSet', 'D2XSet', 'D2YSet']
    
    scanStatus = 0
    scanning = False
    array = None
    pEnables = []
    nEnables = []
    lineScanRunning = False


    
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
        
        #create a label at the top of the window so we know what the window does
        topTextLabel = QLabel('Deflector and Stigmator Control', self)
        topTextLabel.setAlignment(QtCore.Qt.AlignCenter)
        topTextLabel.setFixedHeight(50)
        topTextLabel.setWordWrap(True)
        topTextLabel.setFont(titleFont)
        mainGrid.addWidget(topTextLabel, 0, 0, 1, 4)
        
        #add labels for condenser 1, condenser 2, intermediate 1
        D1XLabel = QLabel('Deflector 1 X Setting (0-5)')
        D1XLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(D1XLabel, 1, 0)
        
        D1YLabel = QLabel('Deflector 1 Y Setting (0-5)')
        D1YLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(D1YLabel, 1, 2)
        
        D2XLabel = QLabel('Deflector 2 X Setting (0-5)')
        D2XLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(D2XLabel, 2, 0)
        
        D2YLabel = QLabel('Deflector 2 Y Setting (0-5)')
        D2YLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(D2YLabel, 2, 2)
        
        #add edit boxes to the right of the setting labels
        self.D1XSet = QLineEdit(self)
        self.D1XSet.setText('0')
        self.D1XSet.setFixedWidth(100)
        self.D1XSet.setAlignment(QtCore.Qt.AlignCenter)
        self.D1XSet.textChanged.connect(lambda: self.updateD1X())
        self.pEnables.append(self.D1XSet)
        mainGrid.addWidget(self.D1XSet, 1, 1)
        
        self.D1YSet = QLineEdit()
        self.D1YSet.setText('0')
        self.D1YSet.setFixedWidth(100)
        self.D1YSet.setAlignment(QtCore.Qt.AlignCenter)
        self.D1YSet.textChanged.connect(lambda: self.updateD1Y())
        self.pEnables.append(self.D1YSet)
        mainGrid.addWidget(self.D1YSet, 1, 3)
        
        self.D2XSet = QLineEdit()
        self.D2XSet.setText('0')
        self.D2XSet.setFixedWidth(100)
        self.D2XSet.setAlignment(QtCore.Qt.AlignCenter)
        self.D2XSet.textChanged.connect(lambda: self.updateD2X())
        self.pEnables.append(self.D2XSet)
        mainGrid.addWidget(self.D2XSet, 2, 1)
        
        self.D2YSet = QLineEdit()
        self.D2YSet.setText('0')
        self.D2YSet.setFixedWidth(100)
        self.D2YSet.setAlignment(QtCore.Qt.AlignCenter)
        self.D2YSet.textChanged.connect(lambda: self.updateD2Y())
        self.pEnables.append(self.D2YSet)
        mainGrid.addWidget(self.D2YSet, 2, 3)
        
        self.imgButton = QPushButton('Take Single Image')
        self.imgButton.setFont(titleFont)
        self.imgButton.setFixedHeight(50)
        self.imgButton.clicked.connect(lambda: self.scanInitialize(1))
        self.pEnables.append(self.imgButton)
        mainGrid.addWidget(self.imgButton, 3, 0, 1, 2)
        
        self.lineScanButton = QPushButton('Start Line Scan')
        self.lineScanButton.setFont(titleFont)
        self.lineScanButton.setFixedHeight(50)
        self.lineScanButton.clicked.connect(lambda: self.lineScanInitialize())
        self.pEnables.append(self.lineScanButton)
        mainGrid.addWidget(self.lineScanButton, 3, 2, 1, 2)
        
        pixelDwellLabel = QLabel('Pixel Dwell Time [milliseconds]')
        pixelDwellLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(pixelDwellLabel, 4, 0)
        
        self.pixelDwell = QLineEdit()
        self.pixelDwell.setText('3')
        self.pixelDwell.setFixedWidth(100)
        self.pixelDwell.setAlignment(QtCore.Qt.AlignCenter)
        self.pixelDwell.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.pixelDwell)
        mainGrid.addWidget(self.pixelDwell, 4, 1)
        
        pixelDebounceLabel = QLabel('Pixel Debounce Time [milliseconds]')
        pixelDebounceLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(pixelDebounceLabel, 4, 2)
        
        self.pixelDebounce = QLineEdit()
        self.pixelDebounce.setText('3')
        self.pixelDebounce.setFixedWidth(100)
        self.pixelDebounce.setAlignment(QtCore.Qt.AlignCenter)
        self.pixelDebounce.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.pixelDebounce)
        mainGrid.addWidget(self.pixelDebounce, 4, 3)
        
        xPixelsLabel = QLabel('Number of X Pixels')
        xPixelsLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(xPixelsLabel, 5, 0)
        
        self.xPixels = QLineEdit()
        self.xPixels.setText('32')
        self.xPixels.setFixedWidth(100)
        self.xPixels.setAlignment(QtCore.Qt.AlignCenter)
        self.xPixels.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.xPixels)
        mainGrid.addWidget(self.xPixels, 5, 1)
        
        yPixelsLabel = QLabel('Number of Y Pixels')
        yPixelsLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(yPixelsLabel, 5, 2)
        
        self.yPixels = QLineEdit()
        self.yPixels.setText('32')
        self.yPixels.setFixedWidth(100)
        self.yPixels.setAlignment(QtCore.Qt.AlignCenter)
        self.yPixels.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.yPixels)
        mainGrid.addWidget(self.yPixels, 5, 3)
        
        xStepLabel = QLabel('X Voltage Step [V]')
        xStepLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(xStepLabel, 6, 0)
        
        self.xStep = QLineEdit()
        self.xStep.setText('0.01')
        self.xStep.setFixedWidth(100)
        self.xStep.setAlignment(QtCore.Qt.AlignCenter)
        self.xStep.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.xStep)
        mainGrid.addWidget(self.xStep, 6, 1)
        
        yStepLabel = QLabel('Y Voltage Step [V]')
        yStepLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(yStepLabel, 6, 2)
        
        self.yStep = QLineEdit()
        self.yStep.setText('0.01')
        self.yStep.setFixedWidth(100)
        self.yStep.setAlignment(QtCore.Qt.AlignCenter)
        self.yStep.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.yStep)
        mainGrid.addWidget(self.yStep, 6, 3)
        
        xCenterLabel = QLabel('X Center Voltage [V]\nMoves scan window: \nup << X(2.5) >> down')
        xCenterLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(xCenterLabel, 7, 0)
        
        self.xCenter = QLineEdit()
        self.xCenter.setText('2.5')
        self.xCenter.setFixedWidth(100)
        self.xCenter.setAlignment(QtCore.Qt.AlignCenter)
        self.xCenter.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.xCenter)
        mainGrid.addWidget(self.xCenter, 7, 1)
        
        yCenterLabel = QLabel('Y Center Voltage [V]\nMoves scan window: \nleft << Y(2.5) >> right')
        yCenterLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(yCenterLabel, 7, 2)
        
        self.yCenter = QLineEdit()
        self.yCenter.setText('2.5')
        self.yCenter.setFixedWidth(100)
        self.yCenter.setAlignment(QtCore.Qt.AlignCenter)
        self.yCenter.textChanged.connect(lambda: self.updateInfo())
        self.pEnables.append(self.yCenter)
        mainGrid.addWidget(self.yCenter, 7, 3)
        
        self.scanStartButton = QPushButton('Start Live Scan')
        self.scanStartButton.setFont(titleFont)
        self.scanStartButton.setFixedHeight(50)
        self.scanStartButton.clicked.connect(lambda: self.scanInitialize(2))
        self.pEnables.append(self.scanStartButton)
        mainGrid.addWidget(self.scanStartButton, 8, 0, 1, 2)
        
        self.scanStopButton = QPushButton('Stop Live Scan')
        self.scanStopButton.setFont(titleFont)
        self.scanStopButton.setFixedHeight(50)
        self.scanStopButton.clicked.connect(lambda: self.scanInitialize(0))
        self.scanStopButton.setEnabled(False)
        self.nEnables.append(self.scanStopButton)
        mainGrid.addWidget(self.scanStopButton, 8, 2, 1, 2)
        
        
        additionalInfoLabel = QLabel('Additional Info: ')
        additionalInfoLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainGrid.addWidget(additionalInfoLabel, 8, 3)

        #additionalInfoLabel = QGraphicsView('Additional Info: ')
        #additionalInfoLabel.setAlignment(QtCore.Qt.AlignCenter)
        #mainGrid.addWidget(additionalInfoLabel, 8, 3)

        #actually add the main overall grid to the popup window
        self.setLayout(mainGrid)
        
        #name the window
        self.setWindowTitle('Deflectors and Stigmators Settings')

    #update functions for D1X to D2Y
    def updateD1X(self):
        DataSets.windowHandle.refreshDataSets()
        Hardware.IO.setAnalog('D1X', self.D1XSet.text())

    def updateD1Y(self):
        DataSets.windowHandle.refreshDataSets()
        Hardware.IO.setAnalog('D1Y', self.D1XSet.text())

    def updateD2X(self):
        DataSets.windowHandle.refreshDataSets()
        Hardware.IO.setAnalog('D2X', self.D1XSet.text())

    def updateD2Y(self):
        DataSets.windowHandle.refreshDataSets()
        Hardware.IO.setAnalog('D2Y', self.D1XSet.text())

    #function to enable/disable the UI (currently bugged, needs to run scanning code in another thread)
    def enableDisable(self, state):
        for obj in self.pEnables:
            obj.setEnabled(state)
        for obj in self.nEnables:
            obj.setEnabled(not state)
        windowHandle.update()
        
    #initialization function for the SEM scan generation - feed it 0, it stops; feed it 1, it takes a single image; feed it 2, it scans continuously
    def scanInitialize(self, mode):
        self.scanStatus = mode
        if mode > 0 and self.scanning == False:
            self.enableDisable(False)
            self.scanGeneration()
            self.enableDisable(True)
    
    #function to perform a line scan for focus assist
    def lineScanInitialize(self):
        if not self.lineScanRunning:
            self.lineScanRunning = True
            self.runLineScan()
        else:
            self.lineScanRunning = False
            
    def closeLineScan(self, event):
        self.lineScanRunning = False
    
    #function to perform a line scan for focus assist
    def runLineScan(self):
        fig = plt.figure(figsize=(12,8))
        fig.canvas.mpl_connect('close_event', self.closeLineScan)
        line = zeros( (int(self.xPixels.text()) ,1), dtype=uint8)
        
        axisZoomed = fig.add_subplot(121)
        axisZoomed.set_title('Zoomed Line Scan')
        axisZoomed.set_xlabel('Pixel Position')
        axisZoomed.set_ylabel('Intensity [Counts], 0-255')
        linePlotZoomed, = axisZoomed.plot(line)
        
        axisFull = fig.add_subplot(122)
        axisFull.set_yticks([0, 64, 128, 192, 255])
        axisFull.set_title('Full Scale Line Scan')
        axisFull.set_xlabel('Pixel Position')
        axisFull.set_ylabel('Intensity [Counts], 0-255')
        linePlotFull, = axisFull.plot(line)
        
        x = 0
        xStep = float(self.xStep.text())
        xDir = 1
        
        debounce = int(self.pixelDebounce.text())*1000000
        
        # dwell is the dwell time in NANOSECONDS per pixel
        dwell = float(self.pixelDwell.text())*1000000
        
        # xMiddle is the voltage corresponding to the center of the image
        xMiddle = float(self.xCenter.text())
        
        # xMax is the maximum number of pixels
        xMax = int(self.xPixels.text())
        
        #move to y-center position, hold there
        Hardware.IO.setAnalog('D1Y', float(self.yCenter.text()))
        
        while self.lineScanRunning:
                        
            #move to position
            xVolt = xMiddle + ((x - round(xMax/2)) * xStep)
            Hardware.IO.setAnalog('D1X', xVolt)
            
            #wait a short time for settling of the beam -> ~1 microsecond
            t1 = time_ns()
            while time_ns()-t1 < debounce:
                pass
                
            #acquire a single pixDataSets.windowHandle.refreshDataSets()el's data
            value = 0
            count = 0
            t1 = time_ns()
            while time_ns()-t1 < dwell:
                value = value + Hardware.IO.tempGetImage()
                count = count + 1
            if count > 0:
                value = (value/count)
                
            line[x] = round(value*-1/10*255)
            
            linePlotZoomed.set_ydata(line)
            axisZoomed.set_ylim([line.min()*0.9, line.max()*1.1])
            axisZoomed.set_xlim([0, xMax-1])
            
            linePlotFull.set_ydata(line)
            axisFull.set_ylim([0, 255])
            axisFull.set_xlim([0, xMax-1])
            
            plt.pause(0.05)
            
            x = x + xDir
            if x == xMax-1:
                xDir = -1
            
            if x == 0:
                xDir = 1
                
        Hardware.IO.setAnalog('D1X', float(self.xCenter.text()))
    
    #function to actually make the scan generation unit work
    def scanGeneration(self):
        #run a scan
        
        # *Max is the maximum number of pixels in the direction of *
        xMax = int(self.xPixels.text())
        yMax = int(self.yPixels.text())
        
        # *Step is the voltage step between two pixels in the direction of *
        xStep = float(self.xStep.text())
        yStep = float(self.yStep.text())
        
        # dwell is the dwell time in NANOSECONDS per pixel
        dwell = float(self.pixelDwell.text())*1000000
        
        # *Middle is the voltage corresponding to the center of the image in the direction of *
        xMiddle = float(self.xCenter.text())
        yMiddle = float(self.yCenter.text())
        
        #x/y pixel location, round integers only
        x = 0
        y = 0
        
        #direction variable to multiply by to toggle step direction (+1 / -1)
        xDir = 1
        yDir = 1
        
        print('entering while loop - xMax = ' + str(xMax) + ', yMax = ' + str(yMax))
        
        #data = zeros( (xMax,yMax), dtype=uint16)
        data = zeros( (xMax,yMax), dtype=uint8)
        
        debounce = int(self.pixelDebounce.text())*1000000
        
        r = 10  
        #off = 4
        
        test = 0
        
        self.scanning = True
        
        if test:
            
            print('setting X value to 2.5V')
            Hardware.IO.setAnalog('D1X', 2.5)
            #wait a long time for settling of the beam -> ~1 microsecond
            t1 = time_ns()
            while time_ns()-t1 < 1000000000:
                pass
            
            print('starting acquisition')
            #testing acquisition stability (debounce movements, etc)
            testArray = zeros( (100, 1), dtype=uint16)
            frame = 0
            while frame < 3:
                testArray[frame] = round((Hardware.IO.tempGetImage()+off)/r*65536)
                frame = frame + 1
            
            Hardware.IO.setAnalog('D1X', 2.51)
            #wait a short time (debounce) for the settling of the beam
            t1 = time_ns()
            while time_ns()-t1 < debounce:
                pass
            while frame < 100:
                testArray[frame] = round((Hardware.IO.tempGetImage()+off)/r*65536)
                frame = frame + 1
            
            print(testArray)
            
        else:
            startTime = time_ns()
            
            while y < yMax:
                
                #move to location
                xVolt = xMiddle + ((x - round(xMax/2)) * xStep)
                yVolt = yMiddle + ((y - round(yMax/2)) * yStep)
                Hardware.IO.setAnalog('D1X', xVolt)
                Hardware.IO.setAnalog('D1Y', yVolt)
                
                #wait a short time for settling of the beam -> ~1 microsecond
                t1 = time_ns()
                while time_ns()-t1 < debounce:
                    pass
                
                #acquire a single pixel's data
                value = 0
                count = 0
                t1 = time_ns()
                while time_ns()-t1 < dwell:
                    value = value + Hardware.IO.tempGetImage()
                    count = count + 1
                if count > 0:
                    value = (value/count)
                
                #data[x][y] = round(((value+off)/r)*65536)
                
                #data[x][y] = round(((value+off)/r)*255)
                data[x][y] = round((-1*value/r)*255)
                
                print('X: ' + str('%3d' % x) + ' -> ' + str('%.3f' % xVolt) + 'V, Y: ' + str('%3d' % y) + ' -> ' + str('%.3f' % yVolt) + 'V, pixel: ' + str(data[x][y]) + ' counts, pixel: ' + str(round(value,6)) + ' raw.')
                
                #adjust to allow for move to the next location
                x = x + xDir
                
                if x >= xMax:
                    x = xMax-1
                    y = y + yDir
                    xDir = -1
                
                if x < 0:
                    x = 0
                    y = y + yDir
                    xDir = 1
                    
                if self.scanStatus == 0:
                    Hardware.IO.setAnalog('D1X', xMiddle)
                    Hardware.IO.setAnalog('D1Y', yMiddle)
                    return
                
                
            stopTime = time_ns()
            
            print('Image time: ' + str((stopTime-startTime)/1000000000) + ' seconds.')

            im = Image.fromarray(uint8(data), 'L')
            dateTimeNow=datetime.now()
            imageFilename="./images/"+dateTimeNow.strftime("%Y%m%d_%H%M%S")+".png"
            im.save(imageFilename)
            print("Image saved as:"+imageFilename)
            #im.show()

            imInfo = open("./images/"+dateTimeNow.strftime("%Y%m%d_%H%M%S")+".txt", "w")

            imInfo.write("Num of pixels X (xMax)="+str(xMax)+"\nNum of pixels Y (yMax) = "+str(yMax)+"\nxStep = "+str(xStep)+"\nyStep = "+str(yStep)+"\ndwell time [ns] = "+str(dwell)+"\ndebounce time [ns]= "+str(debounce)+"\nxMiddle = "+str(xMiddle)+"\nyMiddle = "+str(yMiddle)+"\nFilament = "+str('')+"\nAnode = "+str('')+"\nC1 = "+str('')+"\nC2 = "+str('')+"\nC3 = "+str('')+"\nScintillator = "+str('')+"\nPMT+ = "+str('')+"\nPMT- = "+str('')+"\nPreamp Gain = "+str(''))
            #imInfo.close()
            
        Hardware.IO.setAnalog('D1X', xMiddle)
        Hardware.IO.setAnalog('D1Y', yMiddle)
            
        self.scanning = False
    
    #function to actually make the scan generation unit work
    def updateInfo(self):
        DataSets.windowHandle.refreshDataSets()
        # Udates displayed information about current scan
        willValidateInputFieldsHere=0
        #print("hi")
        


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
                eval('self.' + varName + '.setText("' + str(value) + '")')
                return 0
        return -1
        
    #function to get a value from the module
    def getValues(self):
        #return a dictionary of all variable names in data, and values for those variables
        varDict = {}
        for varName in data:
            value = eval('self.' + varName + '.text()')
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

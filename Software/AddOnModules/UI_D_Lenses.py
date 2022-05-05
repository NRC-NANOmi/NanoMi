'''
COPY VERSION
NANOmi Electron Microscope Lenses Module

This code handles setting values on the lenses, as well as displaying the feedback voltage values numerically and in a time plot for chosen values.

Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
*****************************************************************************************************************
Version:            8.0 - September 10, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Modified the code heavily. Integrated Adam and Ricky's work together, now have a fully
                    functional hardware module.
*****************************************************************************************************************
Version:            7.0 - August 28, 2020
By:                 Adam Czarnecki
Notes:              Added hardware reload functionality
*****************************************************************************************************************
Version:            6.0 - August 1, 2020
By:                 Adam Czarnecki
Notes:              Connected to hardware module
*****************************************************************************************************************
Version:            5.0 - July 23, 2020
By:                 Adam Czarnecki
Notes:              Added modular hardware functionality.
*****************************************************************************************************************
Version:            4.0 - July 10, 2020
By:                 Adam Czarnecki
Notes:              Main program does not crash if no hardware connected. Lens module is able to distinguish
                    which board is missing.
*****************************************************************************************************************
Version:            3.0 - July 6, 2020
By:                 Adam Czarnecki
Notes:              Added functionality to initialize and control AIOUSB boards
*****************************************************************************************************************
Version:            2.0 - June 3, 2020
By:                 Adam Czarnecki
Notes:              Added basic widgets (edit boxes, etc.), defined functions to connect to analog I/O
*****************************************************************************************************************
'''

import sys                              #import sys module for system-level functions

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QCheckBox, QSlider
from PyQt5 import QtCore, QtGui

import importlib
# import necessary aspects of the hardware module
from AddOnModules import Hardware
from AddOnModules.SoftwareFiles import TimePlot

buttonName = 'Lenses'                 #name of the button on the main window that links to this code
windowHandle = None                   #a handle to the window on a global scope






#def send_data(setup):
    #Hardware.IO.setDigital("SYNC", False)
    #SCK_state = True
    #if setup == True:
        #data = [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1]
    #else:
        #data = [0,0,0,0,0,0,1,1, 1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1]

##1,0,0,1,0,0,1,0,1,0,0,0,1,0,1,0
    #bit_n = 0
    #i = 0

    #while bit_n != 24:
        #if i%2 == 0:
            #Hardware.IO.setDigital("DATA", data[bit_n])
            #bit_n = bit_n + 1
        #SCK_state = not SCK_state
        #Hardware.IO.setDigital("SCLK", SCK_state)
        #i = i + 1
    #'''
    #y   =[int(bit) for bit in list(bin(36)[2:])]
    #while len(y) < 10:
    #y.insert(0,0)'''

        ##SCK_state = not SCK_state
        ##Hardware.IO.setDigital("SYNC", SCK_state)
        ##Hardware.IO.setDigital("DATA", True)
    #Hardware.IO.setDigital("SYNC", True)
    #Hardware.IO.setDigital("SCLK", True)



    #return






'''

def send_data():
    Hardware.IO.setDigital("SYNC", False) #CS
    SCK = False
    data = [0,0,0,0,0,0,0,0,   10_bit_data, 0,0,0,0,0,0]

    bit_n = 0
    i = 0

    while bit_n != 24:
        if i%2 == 0:
            Hardware.IO.setDigital("DATA", data[bit_n])
            bit_n = bit_n + 1
        SCK = not SCK
        Hardware.IO.setDigital("SCLK", SCK)
        i = i + 1

    Hardware.IO.setDigital("SCLK", False)
    Hardware.IO.setDigital("SYNC", True) #CS

'''
















#def myfunc():
    ##send_data(setup=True)
    ##send_data(setup=False)
    #Hardware.IO.setDigital("SYNC", False)
    #Hardware.IO.setDigital("SCLK", False)
    #Hardware.IO.setDigital("DATA", False)

    #return









#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):
    #empty variable for holding the time plot handle
    displayPlot = None
    #initialization of the local counter for the hardware module in leiu of event driven updating
    hardwareTick = 0

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************

    #these variables are settable/readable by the data sets module, and must be global in the initUI function
    data = ['C1Set', 'C2Set', 'I1Set']

    #a function that users can modify to create their user interface
    def initUI(self):
        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 800
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
        
        #create a label at the top of the window so we know what the window does
        topTextLabel = QLabel('Lenses Control', self)
        topTextLabel.setAlignment(QtCore.Qt.AlignCenter)
        topTextLabel.setFixedHeight(50)
        topTextLabel.setWordWrap(True)
        topTextLabel.setFont(titleFont)
        mainGrid.addWidget(topTextLabel, 0, 0, 1, 10)
        
        #add labels for condenser 1, condenser 2, intermediate 1
        C1SetLabel = QLabel('Condenser 1 Setting')
        mainGrid.addWidget(C1SetLabel, 1, 0)
        
        C2SetLabel = QLabel('Condenser 2 Setting')
        mainGrid.addWidget(C2SetLabel, 2, 0)
        
        I1SetLabel = QLabel('Intermediate 1 Setting')
        mainGrid.addWidget(I1SetLabel, 3, 0)
        
        C1GetLabel = QLabel('Condenser 1 Feedback')
        mainGrid.addWidget(C1GetLabel, 4, 0)
        
        C2GetLabel = QLabel('Condenser 2 Feedback')
        mainGrid.addWidget(C2GetLabel, 5, 0)
        
        I1GetLabel = QLabel('Intermediate 1 Feedback')
        mainGrid.addWidget(I1GetLabel, 6, 0)
        
        #add edit boxes to the right of the setting labels
        self.C1Set = QLineEdit(self)
        self.C1Set.setText('0')
        self.C1Set.setFixedWidth(100)
        self.C1Set.setAlignment(QtCore.Qt.AlignCenter)
        self.C1Set.textChanged.connect(lambda: Hardware.IO.setAnalog('C1', self.C1Set.text()))
        mainGrid.addWidget(self.C1Set, 1, 1)
        
        self.C2Set = QLineEdit()
        self.C2Set.setText('0')
        self.C2Set.setFixedWidth(100)
        self.C2Set.setAlignment(QtCore.Qt.AlignCenter)
        self.C2Set.textChanged.connect(lambda: Hardware.IO.setAnalog('C2', self.C2Set.text()))
        mainGrid.addWidget(self.C2Set, 2, 1)
        
        self.I1Set = QLineEdit()
        self.I1Set.setText('0')
        self.I1Set.setFixedWidth(100)
        self.I1Set.setAlignment(QtCore.Qt.AlignCenter)
        self.I1Set.textChanged.connect(lambda: Hardware.IO.setAnalog('I1', self.I1Set.text()))
        mainGrid.addWidget(self.I1Set, 3, 1)
        
        #add Feedback Labels and update them to display analog inputs from corresponding channels
        self.C1Get = QLineEdit('')
        self.C1Get.setReadOnly(True)
        self.C1Get.setFixedWidth(100)
        mainGrid.addWidget(self.C1Get, 4, 1)
        self.C1Get.adjustSize()
        
        self.C2Get = QLineEdit('')
        self.C2Get.setReadOnly(True)
        self.C2Get.setFixedWidth(100)
        mainGrid.addWidget(self.C2Get, 5, 1)
        self.C2Get.adjustSize()
        
        self.I1Get = QLineEdit('')
        self.I1Get.setReadOnly(True)
        self.I1Get.setFixedWidth(100)
        mainGrid.addWidget(self.I1Get, 6, 1)
        self.I1Get.adjustSize()
        
        self.DO1 = QCheckBox('Digital output 1')
        #DO1.stateChanged.connect(lambda: Hardware.IO.setDigital("DATA",DO1.isChecked()))
        #Hardware.IO.setDigital("SYNC", True)
        #Hardware.IO.setDigital("SCLK", True)
        #send_data(setup=True)
       # DO1.stateChanged.connect(lambda: send_data(setup=False))
        ##myfunc()


        mainGrid.addWidget(self.DO1, 7, 1)
        
        self.displayPlot = TimePlot.main()
        self.displayPlot.setupPlot(3, 'Lens Voltages', 'Voltage [V]', ['C1', 'C2', 'I1'])
        mainGrid.addWidget(self.displayPlot, 1, 2, 6, 5)
        
        #actually add the main overall grid to the popup window
        self.setLayout(mainGrid)
        
        #name the window
        self.setWindowTitle('Lens Settings')
        
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(lambda: self.updateFeedback([self.C1Get, self.C2Get, self.I1Get], ['C1','C2','I1']))
        self.updateTimer.start(10)
        
#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************0000000000000000000
 
    #feeds back the analog input values to the user interface
    def updateFeedback(self, labels, names):
        #if our local value is not the same as the hardware value, there is new data available
        if not Hardware.IO.AiNewValue == self.hardwareTick:
            values = []
            #iterate through all names in this module
            for name, label in zip(names, labels):
                try:
                    #if the key exists in the AiLiveValues array in the hardware module, use it's value
                    value = Hardware.IO.AiLiveValues[name]
                    label.setText("{0:1.4f}".format(value))
                    values.append(value)
                except KeyError:
                    print('key ' + name + ' does not exist.')
            #if some values were updated, add them to the time plot
            if values:
                self.displayPlot.addPoints(values)
            #update our local counter value to match the current hardware counter value
            self.hardwareTick = Hardware.IO.AiNewValue

   #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    #function to be able to load data to the user interface from the DataSets module
    def setValue(self, name, value):
        for varName in self.data:
            if name in varName:
                eval("self." + varName + '.setText("' + str(value) + '")')
                return 0
        return -1
        
    #function to get a value from the module, used by DataSets
    def getValues(self):
        #return a dictionary of all variable names in data, and values for those variables
        varDict = {}
        for varName in self.data:
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
    
#the showPopUp program will show the instantiated window (which was either hidden or visible)
def showPopUp():
    windowHandle.show()

if __name__ == '__main__':
    main()

'''

NANOmi Electron Microscope Hardware Module

This code acts as a middleman between the submodules and hardware. It translates updates to the hardware given by the modules to be understood by the hardware.

Initial Code:       Adam Czarnecki
Initial Date:       July 31, 2020
*****************************************************************************************************************
Version:            4.1 - September 10, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Filled out the class from 4.0 and made it functional.
                        -Users can now modify the I/O Assignments from a graphical user interface (which named IO point links to which pin on which board).
                        -Tested functionality with the Lenses module, and it works.
                        -Reorganized the file structure so that the UI modules are prefaced with "UI_xxxxx.py", and any other save files are placed in subfolders to the AddOnModules folder because Python doesn't like to jump up folders to the folder that runs the initial program.
                        -Reads in the IoAssignments.txt file on startup if hardware is found so that users don't have to set up the hardware profile each time they start up the software.
                        -Allows writing to IoAssignments.txt in a safe manner, with error catching etc.
*****************************************************************************************************************
Version:            4.0 - September 4, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Integrated Adam's hardware with the NANOmi.py layout.
                        -Moved hardware.py into /AddOnModules/Hardware.py
                        -Created a class to handle a set of dictionaries for analog inputs, analog outputs, and digital signals so that multiple boards can be used
*****************************************************************************************************************
Version:            3.0 - August 16, 2020
By:                 Adam Czarnecki
Notes:              Added digital i/o functionality
*****************************************************************************************************************
Version:            2.0 - August 7, 2020
By:                 Adam Czarnecki
Notes:              Checks for valid analog input values. The warning message should be improved
*****************************************************************************************************************
Version:            1.0 - July 31, 2020
By:                 Adam Czarnecki
Notes:              This version provides functionality with the AIOUSB library, and establishes basic
                    functionality for the submodules
*****************************************************************************************************************
'''

import sys                              #import sys module for system-level functions

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets

import datetime
from shutil import copyfile
import signal, os

import importlib
from AddOnModules.HardwareFiles import AIOUSB

buttonName = 'Hardware'                 #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope

#instantiate the IO class here
IO = None

#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):
    #define the Analog output table here so it is visible to the other class
    AoTable = QTableWidget()
    AoTable.setColumnCount(3)
    AoTable.setHorizontalHeaderItem(0, QTableWidgetItem('Name:'))
    AoTable.setHorizontalHeaderItem(1, QTableWidgetItem('Board Serial Number:'))
    AoTable.setHorizontalHeaderItem(2, QTableWidgetItem('Board Channel:'))
    AoTable.setRowCount(0)
    AoTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    AoTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    AoTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    
    #define the Analog input table here so it is visible to the other class
    AiTable = QTableWidget()
    AiTable.setColumnCount(3)
    AiTable.setHorizontalHeaderItem(0, QTableWidgetItem('Name:'))
    AiTable.setHorizontalHeaderItem(1, QTableWidgetItem('Board Serial Number:'))
    AiTable.setHorizontalHeaderItem(2, QTableWidgetItem('Board Channel:'))
    AiTable.setRowCount(0)
    AiTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    AiTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    AiTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    
    #define the Digital input/output table here so it is visible to the other class
    DxTable = QTableWidget()
    DxTable.setColumnCount(4)
    DxTable.setHorizontalHeaderItem(0, QTableWidgetItem('Name:'))
    DxTable.setHorizontalHeaderItem(1, QTableWidgetItem('Board Serial Number:'))
    DxTable.setHorizontalHeaderItem(2, QTableWidgetItem('Board Channel:'))
    DxTable.setHorizontalHeaderItem(3, QTableWidgetItem('I/O Direction:'))
    #DxTable.verticalHeader().setVisible(False)
    DxTable.setRowCount(0)
    DxTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    DxTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    DxTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    DxTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    
    #define a variable to tell the software that something has been changed, so query about saving
    doSave = False

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************
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
        
        AoLabel = QLabel('Analog Outputs')
        AoLabel.setAlignment(QtCore.Qt.AlignCenter)
        AoLabel.setFont(titleFont)
        mainGrid.addWidget(AoLabel, 0, 0, 1, 5)
        
        newAoButton = QPushButton('Add Analog Output')
        newAoButton.setFont(titleFont)
        newAoButton.clicked.connect(lambda: self.newAnalogOutput())
        mainGrid.addWidget(newAoButton, 0, 5, 1, 1)
        
        mainGrid.addWidget(self.AoTable, 1, 0, 1, 6)
        
        AiLabel = QLabel('Analog Inputs')
        AiLabel.setAlignment(QtCore.Qt.AlignCenter)
        AiLabel.setFont(titleFont)
        mainGrid.addWidget(AiLabel, 2, 0, 1, 5)
        
        newAiButton = QPushButton('Add Analog Input')
        newAiButton.setFont(titleFont)
        newAiButton.clicked.connect(lambda: self.newAnalogInput())
        mainGrid.addWidget(newAiButton, 2, 5, 1, 1)
        
        mainGrid.addWidget(self.AiTable, 3, 0, 1, 6)
        
        DxLabel = QLabel('Digital Inputs and Outputs')
        DxLabel.setAlignment(QtCore.Qt.AlignCenter)
        DxLabel.setFont(titleFont)
        mainGrid.addWidget(DxLabel, 4, 0, 1, 5)
        
        newDxButton = QPushButton('Add Digital I/O')
        newDxButton.setFont(titleFont)
        newDxButton.clicked.connect(lambda: self.newDigital())
        mainGrid.addWidget(newDxButton, 4, 5, 1, 1)
        
        mainGrid.addWidget(self.DxTable, 5, 0, 2, 6)
        
        rescanBtn = QPushButton('Rescan for Hardware')
        rescanBtn.setFont(titleFont)
        rescanBtn.clicked.connect(lambda: self.rescanHardware())
        mainGrid.addWidget(rescanBtn, 7, 0, 1, 3)
        
        saveBtn = QPushButton('Save Changes')
        saveBtn.setFont(titleFont)
        saveBtn.clicked.connect(lambda: self.saveChanges())
        mainGrid.addWidget(saveBtn, 7, 3, 1, 3)
        
        #name the window
        self.setWindowTitle('Hardware Functions')
        
        self.AoTable.itemChanged.connect(lambda: self.triggerSave())
        self.AiTable.itemChanged.connect(lambda: self.triggerSave())
        self.DxTable.itemChanged.connect(lambda: self.triggerSave())
    
    #scans for hardware, either for the first time automatically or on a button press from the hardware module
    def rescanHardware(self):
        self.AoTable.setRowCount(0)
        self.AiTable.setRowCount(0)
        self.DxTable.setRowCount(0)
        AIOUSB.AIOUSB_Exit()
        IO.hardwareScan()
        
    #saves the changes to the assignments file. Allows users to set up the I/O via the user interface.
    def saveChanges(self):
        if self.doSave == False:
            print('No changes were made, so saving is not necessary.')
            QMessageBox.question(self,'Save assignments', 'No changes were made, so saving is not necessary.', QMessageBox.Ok, QMessageBox.Ok)
        else:
            AoNameList = []
            AoSerialList = []
            AoChannelList = []
            AoDirectionList = []
            aoRows = self.AoTable.rowCount()
            for row in range(0,aoRows):
                name   = self.AoTable.item(row,0).text()
                serial = self.AoTable.item(row,1).text()
                channel= self.AoTable.item(row,2).text()
                if name == '':
                    QMessageBox.question(self,'Invalid data', 'The analog output name "' + name + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                try:
                    serialNum = int(serial)
                except:
                    QMessageBox.question(self,'Invalid data', 'The analog output serial number "' + serial + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                try:
                    channelNum = int(channel)
                    if channelNum < 0:
                        QMessageBox.question(self,'Invalid data', 'The analog output channel number "' + channel + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                        return
                except:
                    QMessageBox.question(self,'Invalid data', 'The analog output channel number "' + channel + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                AoNameList.append(name)
                AoSerialList.append(serialNum)
                AoChannelList.append(channelNum)
                AoDirectionList.append('-')
            
            #further error checking - make sure no names are repeated
            if(len(set(AoNameList)) != len(AoNameList)):
                QMessageBox.question(self,'Invalid data', 'Analog output names are repeated. Only unique names are allowed - changes not saved.', QMessageBox.Ok, QMessageBox.Ok)
                return
            
            #not checking for duplicate channels on the same board yet - have to trust the user a little bit
            
            AiNameList = []
            AiSerialList = []
            AiChannelList = []
            AiDirectionList = []
            aiRows = self.AiTable.rowCount()
            for row in range(0,aiRows):
                name   = self.AiTable.item(row,0).text()
                serial = self.AiTable.item(row,1).text()
                channel= self.AiTable.item(row,2).text()
                if name == '':
                    QMessageBox.question(self,'Invalid data', 'The analog input name "' + name + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                try:
                    serialNum = int(serial)
                except:
                    QMessageBox.question(self,'Invalid data', 'The analog input serial number "' + serial + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                try:
                    channelNum = int(channel)
                    if channelNum < 0:
                        QMessageBox.question(self,'Invalid data', 'The analog input channel number "' + channel + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                        return
                except:
                    QMessageBox.question(self,'Invalid data', 'The analog input channel number "' + channel + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                AiNameList.append(name)
                AiSerialList.append(serialNum)
                AiChannelList.append(channelNum)
                AiDirectionList.append('-')
            
            #further error checking - make sure no names are repeated
            if(len(set(AiNameList)) != len(AiNameList)):
                QMessageBox.question(self,'Invalid data', 'Analog input names are repeated. Only unique names are allowed - changes not saved.', QMessageBox.Ok, QMessageBox.Ok)
                return
            
            DxNameList = []
            DxSerialList = []
            DxChannelList = []
            DxDirectionList = []
            DxRows = self.DxTable.rowCount()
            for row in range(0,DxRows):
                name   = self.DxTable.item(row,0).text()
                serial = self.DxTable.item(row,1).text()
                channel= self.DxTable.item(row,2).text()
                dir    = self.DxTable.item(row,3).text()
                if name == '':
                    QMessageBox.question(self,'Invalid data', 'The digital name "' + name + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                try:
                    serialNum = int(serial)
                except:
                    QMessageBox.question(self,'Invalid data', 'The digital serial number "' + serial + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                try:
                    channelNum = int(channel)
                    if channelNum < 0:
                        QMessageBox.question(self,'Invalid data', 'The digital channel number "' + channel + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                        return
                except:
                    QMessageBox.question(self,'Invalid data', 'The digital channel number "' + channel + '"is invalid. Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                if not (dir.lower() == 'i' or dir.lower() == 'o'):
                    QMessageBox.question(self,'Invalid data', 'The digital direction "' + dir + '"is invalid - it should be either "I" or "O". Saving not performed.', QMessageBox.Ok, QMessageBox.Ok)
                    return
                DxNameList.append(name)
                DxSerialList.append(serialNum)
                DxChannelList.append(channelNum)
                DxDirectionList.append(dir)
            
            #further error checking - make sure no names are repeated
            if(len(set(DxNameList)) != len(DxNameList)):
                QMessageBox.question(self,'Invalid data', 'Digital input/output names are repeated. Only unique names are allowed - changes not saved.', QMessageBox.Ok, QMessageBox.Ok)
                return
            
            #actually write the file now that all data has been verified
            
            #determine date of writing for reference
            date = datetime.datetime.now()
            dateStr = '# Last save date: ' + date.strftime('%Y/%b/%d, %H:%M') + '\n'
            
            #copy the existing file and rename it as a backup
            copyfile('AddOnModules/SaveFiles/IoAssignments.txt', 'AddOnModules/SaveFiles/IoAssignments_' + date.strftime('%Y-%m-%d_%H-%M') + '.txt')
            
            #specify the file header
            data = []
            
            data.append(dateStr)
            data.append('#\n')
            data.append('#Type,      Channel Name,   Board serial,  Board Channel, Direction,\n')
            data.append("#(AO/AI/D), string,         integer,       integer,     , string ('I' or 'O'),\n")
            data.append('#\n')
            data.append('#Comma after the last entry is required to not have a newline character involved unnecessarily\n')
            data.append('#\n')
            data.append('#Analog Outputs\n')
            data.append('#\n')
            
            #write the analog outputs
            for i in range(0,len(AoNameList)):
                data.append('AO,' + AoNameList[i] + ',' + str(AoSerialList[i]) + ',' + str(AoChannelList[i]) + ',' + AoDirectionList[i] + ',\n')
            
            #specify the analog input file header
            data.append('#\n')
            data.append('#Analog Inputs\n')
            data.append('#\n')
            
            #write the analog inputs
            for i in range(0,len(AiNameList)):
                data.append('AI,' + AiNameList[i] + ',' + str(AiSerialList[i]) + ',' + str(AiChannelList[i]) + ',' + AiDirectionList[i] + ',\n')
            
            #specify the digital file header
            data.append('#\n')
            data.append('#Digitals\n')
            data.append('#\n')
            
            #write the digital inputs and outputs
            for i in range(0,len(DxNameList)):
                data.append('Dx,' + DxNameList[i] + ',' + str(DxSerialList[i]) + ',' + str(DxChannelList[i]) + ',' + DxDirectionList[i] + ',\n')
            
            #open a file for writing to
            fid = open('AddOnModules/SaveFiles/IoAssignments.txt','w')
            fid.writelines(data)
            fid.close()
            
            #reset the save flag
            self.doSave = False
            
            QMessageBox.question(self,'Save complete.', 'Saving the assignments file has been completed', QMessageBox.Ok, QMessageBox.Ok)
    
    #linked to whenever a value is changed in the hardware module interface; asks for saving on exit
    def triggerSave(self):
        self.doSave = True
    
    #creates a new analog output in the hardware table
    def newAnalogOutput(self):
        #define the current row in the hardware analog output table
        row = self.AoTable.rowCount()
        self.AoTable.insertRow(row)
        self.AoTable.setItem(row, 0, QTableWidgetItem())
        self.AoTable.setItem(row, 1, QTableWidgetItem())
        self.AoTable.setItem(row, 2, QTableWidgetItem())
        
    #creates a new analog input in the hardware table
    def newAnalogInput(self):
        #define the current row in the hardware analog output table
        row = self.AiTable.rowCount()
        self.AiTable.insertRow(row)
        self.AiTable.setItem(row, 0, QTableWidgetItem())
        self.AiTable.setItem(row, 1, QTableWidgetItem())
        self.AiTable.setItem(row, 2, QTableWidgetItem())
        
    #creates a new digital line in the hardware table
    def newDigital(self):
        #define the current row in the hardware analog output table
        row = self.DxTable.rowCount()
        self.DxTable.insertRow(row)
        self.DxTable.setItem(row, 0, QTableWidgetItem())
        self.DxTable.setItem(row, 1, QTableWidgetItem())
        self.DxTable.setItem(row, 2, QTableWidgetItem())
        self.DxTable.setItem(row, 3, QTableWidgetItem())
        
#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE IN THIS CLASS OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************
    #function for saving variables - nothing here so just return an empty dictionary
    def getValues(self):
        return {}
    
    #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()
        
    #this function handles the closing of the pop-up window - it doesn't actually close, simply hides visibility. 
    #this functionality allows for permanance of objects in the background
    def closeEvent(self, event):
        event.ignore()
        if windowHandle.doSave == True:
            reply = QMessageBox.question(self, 'Save changes?', 'I/O assignments have changed. Save?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                windowHandle.saveChanges()
            else:
                windowHandle.AoTable.setRowCount(0)
                windowHandle.AiTable.setRowCount(0)
                windowHandle.DxTable.setRowCount(0)
                IO.loadAssigments()
                windowHandle.doSave = False
        self.hide()
        
    #this function is called on main window shutdown, and it forces the popup to close
    def shutdown():
        return sys.exit(True)

#the main program will instantiate the window once
#if it has been instantiated, it simply puts focus on the window instead of making a second window
#modifying this function can break the main window functionality
def main():
    global windowHandle
    windowHandle = popWindow()
    
    # initialize hardware
    global IO
    #instantiate a structure for all inputs/outputs
    IO = IoStruct()
    #perform a hardware scan, and add inputs/outputs and boards to the structure
    IO = IO.hardwareScan()
    
    print("Number of boards found:", IO.boardsFound)
    print()
    return windowHandle

#def reload_hardware():
    #import hardware
    #importlib.reload(hardware)

#the showPopUp program will show the instantiated window (which was either hidden or visible)
def showPopUp():
    windowHandle.show()
    windowHandle.doSave = False

if __name__ == '__main__':
    main()

#class to handle all of the input/output assignments in a (hopefully) clean and expandable way
class IoStruct:
    #XXIndex increments when a new board is found with that specific type of channel, and as many channels as are on the board are added.
    #Then XxNames is a dictionary that is instantiated to have that many more entries with values "Placeholder_Xx##".
    #XxBoard is a dictionary that is instantiated with that many more entries with values set to the board index.
    #XxChannel is a dictionary that is instantiated to have that many more entries with values set to the local channel index.
    #When complete the dictionaries are:
    #XxNames ------ key: value pairs of "channel names": "global channel index"
    #XxBoard ------ key: value pairs of "global channel index": "board index"
    #XxChannel ---- key: value pairs of "global channel index": "local board channel"
    #DxDirection -- key: value pairs of "global channel index": "port direction" (only for digital ports, where 'I' is used for input and 'O' is used for output)
    #the internal variable "global channel index" is not useful to the world outside of the class, but acts as a linkage between the name and the board/channel/direction to associate with that name
    
    #analog outputs
    AoIndex = 0
    AoNames = {}
    AoBoard = {}
    AoChannel = {}
    
    #analog inputs
    AiIndex = 0
    AiNames = {}
    AiBoard = {}
    AiChannel = {}
    AiValues = {}
    
    #analog input current/live values, as of last reading, which is set every 100ms in this module
    AiLiveValues = {}
    #when a new set of values are read into AiLiveValues, this will increment and roll over at 9, i.e 0 - 9
    AiNewValue = 0
    
    #digital inputs and outputs as one, as they are configurable
    DxIndex = 0
    DxNames = {}
    DxBoard = {}
    DxChannel = {}
    DxDirection = {}
    
    #number of boards actually detected
    boardsFound = 0
    #linking the board indicies and the part serial numbers
    boardSerialNumbers = {}
    
    #update timer for frequent input updates
    updateTimer = QtCore.QTimer()

    #function to add a new board found to the class
    def addBoard(struct, portType, numberOfChannels, boardIndex):
        #adding a new analog output set of channels
        if portType == 'AO':
            for index in range(numberOfChannels):
                struct.AoNames['Placeholder_AO'+ str(index+struct.AoIndex)] = index + struct.AoIndex
                struct.AoChannel[index + struct.AoIndex] = index
                struct.AoBoard[index + struct.AoIndex] = boardIndex
            struct.AoIndex = struct.AoIndex + numberOfChannels
            
        elif portType == 'AI':
            for index in range(numberOfChannels):
                struct.AiNames['Placeholder_AI'+ str(index+struct.AiIndex)] = index + struct.AiIndex
                struct.AiChannel[index + struct.AiIndex] = index
                struct.AiBoard[index + struct.AiIndex] = boardIndex
            struct.AiIndex = struct.AiIndex + numberOfChannels
            
        elif portType == 'D':
            for index in range(numberOfChannels):
                struct.DxNames['Placeholder_Dx' + str(index + struct.DxIndex)] = index + struct.DxIndex
                struct.DxChannel[index + struct.DxIndex] = index
                struct.DxBoard[index + struct.DxIndex] = boardIndex
                struct.DxDirection[index + struct.DxIndex] = None
            struct.DxIndex = struct.DxIndex + numberOfChannels
            
        else:
            print('Board not added because type of board was incorrect.')

    #function to scan through all hardware and fill out the structure in the class
    def hardwareScan(struct):
        #initialize structures
        struct.initStructures()
        
        #stop update timer (in case it was started)
        struct.updateTimer.stop()
        
        #initialize hardware
        AIOUSB.AIOUSB_Init()
        
        print()
        
        #enquire about what hardware is currently connected
        devMask = AIOUSB.GetDevices()
        struct.boardsFound = 0
        for boardIndex in range(31):
            if 0 != (devMask & (1 << boardIndex)):
                struct.boardsFound = struct.boardsFound + 1
                status, serial, name, digitalIo, ctrs = AIOUSB.QueryDeviceInfo(boardIndex)
                
                print("Board found at index", boardIndex, ", with serial number", serial, ", board name:", name, ", and", digitalIo, "digital I/O bytes available")
                
                struct.boardSerialNumbers[serial] = boardIndex
                
                if name == 'USB-AIO16-16F':
                    #16 analog inputs, 2 analog outputs, 16 digital IO
                    
                    #set up the analog inputs in software
                    struct.addBoard("AI", 16, boardIndex)
                    
                    #set up the analog outputs in software
                    struct.addBoard("AO", 2, boardIndex)
                    
                    #ADC_Range1 (boardIndex, channel, gaincode, bDifferential):
                    # boardIndex = board number
                    # channel = channel number
                    # gaincode: 0=0-10V, 1=+/-10V, 2=0-5V, 3=+/-5V, 4=0-2V, 5=+/-2V, 6=0-1V, 7=+/-1V
                    # bDifferential: 0 = single-ended measurement, 1 = differential measurement
                    AIOUSB.ADC_Range1(boardIndex, 0, 1, 0)
                    
                    #set up the digital IO in software
                    struct.addBoard('D', 8*digitalIo, boardIndex)
                    
                    #DIO_Configure(boardIndex, tristate boolean, Outs Array, Data Array):
                    #
                    #Outs Array = 0 means both I/O Groups will be input
                    #Outs Array = 1 means I/O Group 0 will be output and I/O Group 1 will be input
                    #Outs Array = 2 means I/O Group 0 will be input and I/O Group 1 will be output
                    #Outs Array = 3 means both I/O Groups will be output
                    #
                    #Data Array = [0-255, 0-255] - sets the initial value of the digital outputs in a bank
                    AIOUSB.DIO_Configure(boardIndex, False, [0], [0,0])
                    
                if name == 'USB-AO16-16':
                    #16 analog outputs, 16 digital IO
                    
                    #set up the analog outputs in software
                    struct.addBoard("AO", 16, boardIndex)
                    
                    #DACSetBoardRange (boardIndex, range):
                    # range: 0=0-5V, 1=+/-5V, 2=0-10V, 3=+/-10V
                    AIOUSB.DACSetBoardRange(boardIndex, 0)
                    
                    #set up the digital IO in software
                    struct.addBoard('D', 8*digitalIo, boardIndex)
                    
                    #DIO_Configure(boardIndex, tristate boolean, Outs Array, Data Array):
                    #
                    #Outs Array = 0 means both I/O Groups will be input
                    #Outs Array = 1 means I/O Group 0 will be output and I/O Group 1 will be input
                    #Outs Array = 2 means I/O Group 0 will be input and I/O Group 1 will be output
                    #Outs Array = 3 means both I/O Groups will be output
                    #
                    #Data Array = [0-255, 0-255] - sets the initial value of the digital outputs in a bank
                    AIOUSB.DIO_Configure(boardIndex, False, [3], [0,0])
        
        #add line to output for readability
        print()
        
        #see if there are previous assignments to include
        struct.loadAssigments()
        
        if struct.boardsFound > 0:
            #link update timer tick to scanning hardware
            struct.updateTimer.timeout.connect(lambda: struct.getAnalogs())
            
            #start update timer
            struct.updateTimer.start(1)
        
        return struct
        
    #clear all structure data because we're starting fresh or refreshing existing stuff
    def initStructures(struct):
        #analog outputs
        struct.AoIndex = 0
        struct.AoNames = {}
        struct.AoBoard = {}
        struct.AoChannel = {}
        
        #analog inputs
        struct.AiIndex = 0
        struct.AiNames = {}
        struct.AiBoard = {}
        struct.AiChannel = {}
        
        #digital inputs and outputs as one, as they are configurable
        struct.DxIndex = 0
        struct.DxNames = {}
        struct.DxBoard = {}
        struct.DxChannel = {}
        struct.DxDirection = {}
        
        #number of boards actually detected
        struct.boardsFound = 0
        #linking the board indicies and the part serial numbers
        struct.boardSerialNumbers = {}
    
    #function used to load assignments that were set up previously so users don't have to set up the microscope I/O every time the code starts.  Will throw an error if boards don't exist etc.
    def loadAssigments(struct):
        #set up the reading of the assignment file for the IO profile
        fName = 'AddOnModules/SaveFiles/IoAssignments.txt'
        #list of failed serial numbers for display later
        fails = []
        try:
            #open the file, try will catch it if it doesn't exist
            with open(fName, 'r') as reader:
                #read lines out of the file one-by-one
                for line in reader.readlines():
                    #leading with a # means the line is commented out to make it human readable
                    if line[0] != '#':
                        #split the line by comments
                        entries = line.split(',')
                        name = entries[1]
                        boardSerial = int(entries[2])
                        channel = int(entries[3])
                        try:
                            boardIndex = struct.boardSerialNumbers[boardSerial]
                        except KeyError:
                            fails.append(boardSerial)
                            continue
                        
                        #if dealing with analog outputs:
                        if entries[0] == 'AO':
                            #instantiate a list of potential matches - need to link the board index and channel value to a specific global channel index, which we then set the name to.
                            #all this is because we can't have multiple-valued dictionaries?
                            possibles = []
                            #search through board indexes, come up with a list of potential values
                            for gChannel, bIndex in struct.AoBoard.items():
                                if bIndex == boardIndex:
                                    possibles.append(gChannel)
                            #search through channel indexes, compare against previous potentials - should only be one match uniquely
                            for gChannel, chIndex in struct.AoChannel.items():
                                if chIndex == channel and gChannel in possibles:
                                    globalChannel = gChannel
                                    break
                            #set the name at the determined global channel - this will allow simple linkage later
                            for dictionaryName, gChannel in struct.AoNames.items():
                                if gChannel == globalChannel:
                                    struct.AoNames[name] = struct.AoNames.pop(dictionaryName)
                                    break
                            #define the current row in the hardware analog output table
                            row = windowHandle.AoTable.rowCount()
                            windowHandle.AoTable.insertRow(row)
                            windowHandle.AoTable.setItem(row, 0, QTableWidgetItem(name))
                            windowHandle.AoTable.setItem(row, 1, QTableWidgetItem(str(boardSerial)))
                            windowHandle.AoTable.setItem(row, 2, QTableWidgetItem(str(channel)))
                            
                        #if dealing with analog inputs
                        elif entries[0] == 'AI':
                            #instantiate a list of potential matches - need to link the board index and channel value to a specific global channel index, which we then set the name to.
                            #all this is because we can't have multiple-valued dictionaries?
                            possibles = []
                            #search through board indexes, come up with a list of potential values
                            for gChannel, bIndex in struct.AiBoard.items():
                                if bIndex == boardIndex:
                                    possibles.append(gChannel)
                            #search through channel indexes, compare against previous potentials - should only be one match uniquely
                            for gChannel, chIndex in struct.AiChannel.items():
                                if chIndex == channel and gChannel in possibles:
                                    globalChannel = gChannel
                                    break
                            #set the name at the determined global channel - this will allow simple linkage later
                            for dictionaryName, gChannel in struct.AiNames.items():
                                if gChannel == globalChannel:
                                    struct.AiNames[name] = struct.AiNames.pop(dictionaryName)
                                    break
                            #struct.AiNames[globalChannel] = name
                            #define the current row in the hardware analog input table
                            row = windowHandle.AiTable.rowCount()
                            windowHandle.AiTable.insertRow(row)
                            windowHandle.AiTable.setItem(row, 0, QTableWidgetItem(name))
                            windowHandle.AiTable.setItem(row, 1, QTableWidgetItem(str(boardSerial)))
                            windowHandle.AiTable.setItem(row, 2, QTableWidgetItem(str(channel)))
                            
                        #if dealing with digital outputs
                        elif entries[0] == 'Dx':
                            #instantiate a list of potential matches - need to link the board index and channel value to a specific global channel index, which we then set the name to.
                            #all this is because we can't have multiple-valued dictionaries?
                            possibles = []
                            #search through board indexes, come up with a list of potential values
                            for gChannel, bIndex in struct.DxBoard.items():
                                if bIndex == boardIndex:
                                    possibles.append(gChannel)
                            #search through channel indexes, compare against previous potentials - should only be one match uniquely
                            for gChannel, chIndex in struct.DxChannel.items():
                                if chIndex == channel and gChannel in possibles:
                                    globalChannel = gChannel
                                    break
                            #set the name at the determined global channel - this will allow simple linkage later
                            #struct.DxNames[globalChannel] = name
                            for dictionaryName, gChannel in struct.DxNames.items():
                                if gChannel == globalChannel:
                                    struct.DxNames[name] = struct.DxNames.pop(dictionaryName)
                                    break
                            struct.DxDirection[globalChannel] = entries[4]
                            #define the current row in the hardware digitals table
                            row = windowHandle.DxTable.rowCount()
                            windowHandle.DxTable.insertRow(row)
                            windowHandle.DxTable.setItem(row, 0, QTableWidgetItem(name))
                            windowHandle.DxTable.setItem(row, 1, QTableWidgetItem(str(boardSerial)))
                            windowHandle.DxTable.setItem(row, 2, QTableWidgetItem(str(channel)))
                            windowHandle.DxTable.setItem(row, 3, QTableWidgetItem(entries[4]))

                        else:
                            print('Could not load IO Assignment for type ', entries[0])
        except:
            print('Could not load IO Assignments file.')
        
        windowHandle.rowSave = False
        
        if len(fails)>0:
            print('Could not find the following hardware boards that were in the IO Assignments file:')
            fs = list(set(fails))
            for f in fs:
                print('    Serial number:', f)
            print('Check connections and rescan the hardware.')
    
    #function to set an analog output value
    def setAnalog(struct, name, strValue):
        value = None
        try:
            value = float(strValue)
            if value >= 0:
                # set parameters for data writing:
                offset = 0
                span = 10
                globalChannelIndex = None
                
                #see if the name is valid, and if so grab the globalChannelIndex
                try:
                    globalChannelIndex = struct.AoNames[name]
                except:
                    print('Did not set analog output because channel name ' + name + ' does not exist or was not set up properly.')
                    return -1
                
                #if globalChannelIndex valid, get the boardIndex (0-31) and localBoardChannel
                try:
                    boardIndex = struct.AoBoard[globalChannelIndex]
                    localBoardChannel = struct.AoChannel[globalChannelIndex]
                except:
                    print('Did not set analog output because internal dictionaries were not set up properly')
                    return -2
                
                # this function writes output to device
                AIOUSB.DACDirect(boardIndex, localBoardChannel, int(float((value + offset) * 65536.0 / span)))
                return 0
        except:
            if not strValue == '':
                QMessageBox.question(self,'Invalid input', 'The value for setting ' + name + ' is invalid.', QMessageBox.Ok, QMessageBox.Ok)
                struct.sender().setText('0')

    def tempGetImage(self):
        #acquire all values for all boards
        AIOUSB.ADC_SetCal(0, ':AUTO:')
        status = None
        data = None
        #do two scans because first scan is not useful
        for i in range(2):
            status, data = AIOUSB.ADC_GetScanV(0)
        value = []
        value.extend(data[0:16])
        return value[0]

    # this function reads input from device
    def getAnalogs(struct):
        #acquire all values for all boards
        try:
            AiBoardNumbers = set(struct.AiBoard.values())
            overallData = []
            for boardIndex in AiBoardNumbers:
                AIOUSB.ADC_SetCal(boardIndex, ':AUTO:')
                status = None
                data = None
                #do two scans because first scan is not useful
                for i in range(2):
                    status, data = AIOUSB.ADC_GetScanV(boardIndex)
                overallData.extend(data[0:16])
            
            for gci in range(0, struct.AiIndex):
                for key, value in struct.AiNames.items():
                    if value == gci:
                        struct.AiLiveValues[key] = overallData[gci]
                        break
            
            #todo: set a signal here that handlers in other modules can pick up on and be notified that there is new data, so they can update displays and plots asynchronously
            if struct.AiNewValue >= 9:
                struct.AiNewValue = 0
            else:
                struct.AiNewValue = struct.AiNewValue + 1
            
            return 0
        except:
            struct.updateTimer.stop()
            return -1
            #def getAnalog(struct, name):
        ##see if the name is valid, and if so grab the globalChannelIndex
        #globalChannelIndex = None
        #try:
            #globalChannelIndex = struct.AiNames[name]
        #except:
            #return -1
        
        ##if globalChannelIndex valid, get the boardIndex (0-31) and localBoardChannel
        #try:
            #boardIndex = struct.AiBoard[globalChannelIndex]
            #localBoardChannel = struct.AiChannel[globalChannelIndex]
        #except:
            ##print('Did not read analog input because of an invalid value')
            #return -2
        
        #AIOUSB.ADC_SetCal(boardIndex, ":AUTO:")
        #status = None
        #data = None

        ##do two scans because first scan is not useful
        #for i in range(2):
            #status, data = AIOUSB.ADC_GetScanV(boardIndex)
        
        #return data[localBoardChannel]
        
    #write a digital value to one pin
    def setDigital(struct, name, value):
        globalChannelIndex = struct.DxNames[name]
        boardIndex = struct.DxBoard[globalChannelIndex]
        channelIndex = struct.DxChannel[globalChannelIndex]
        AIOUSB.DIO_Write1(boardIndex, channelIndex, value)
        
    #read a digital value from one pin
    def getDigital(struct, name):
        globalChannelIndex = struct.DxNames[name]
        boardIndex = struct.DxBoard[globalChannelIndex]
        channelIndex = struct.DxChannel[globalChannelIndex]
        AIOUSB.DIO_Read1(boardIndex, channelIndex)

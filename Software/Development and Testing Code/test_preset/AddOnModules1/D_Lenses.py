'''

NANOmi Electron Microscope Lenses Module

This code handles setting values on the lenses, as well as displaying the feedback voltage values numerically and in a time plot for chosen values.

Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
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
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit
from PyQt5 import QtCore, QtGui

# import necessary aspects of the hardware module
from hardware import *

buttonName = 'Lenses'                 #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope

#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):

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
        
        #create a label at the top of the window so we know what the window does
        topTextLabel = QLabel('Lenses Control', self)
        topTextLabel.setAlignment(QtCore.Qt.AlignCenter)
        topTextLabel.setFixedWidth(windowWidth-10)
        topTextLabel.setWordWrap(True)
        topTextLabel.setFont(titleFont)
        mainGrid.addWidget(topTextLabel, 0, 0)
        
        #define a tab control with two tabs - Load & Save - underneath the top text
        tabs = QTabWidget()
        saveTab = QWidget()
        loadTab = QWidget()
        tabs.addTab(saveTab, 'Save Presets')
        tabs.addTab(loadTab, 'Load Presets')
        
        #set up a grid layout inside the save tab
        saveGrid = QGridLayout()
        saveGrid.setSpacing(10)
        
        if hardware_detected():
            
            #add labels for condenser 1, condenser 2, intermediate 1
            cond_1_set_label = QLabel('Condenser 1 Setting')
            saveGrid.addWidget(cond_1_set_label, 0, 0)
            
            cond_2_set_label = QLabel('Condenser 2 Setting')
            saveGrid.addWidget(cond_2_set_label, 1, 0)
            
            inter_1_set_label = QLabel('Intermediate 1 Setting')
            saveGrid.addWidget(inter_1_set_label, 2, 0)
            
            cond_1_feed_label = QLabel('Condenser 1 Feedback')
            saveGrid.addWidget(cond_1_feed_label, 3, 0)
            
            cond_2_feed_label = QLabel('Condenser 2 Feedback')
            saveGrid.addWidget(cond_2_feed_label, 4, 0)
            
            inter_1_feed_label = QLabel('Intermediate 1 Feedback')
            saveGrid.addWidget(inter_1_feed_label, 5, 0)
            
            #add an edit boxes to the right of the setting labels
            cond_1_edit = QLineEdit(self)
            cond_1_edit.setText('0')
            saveGrid.addWidget(cond_1_edit, 0, 1)
            
            cond_2_edit = QLineEdit()
            cond_2_edit.setText('0')
            saveGrid.addWidget(cond_2_edit, 1, 1)
            
            inter_1_edit = QLineEdit()
            inter_1_edit.setText('0')
            saveGrid.addWidget(inter_1_edit, 2, 1)
            
            
            #add push buttons to the right of edit boxes that will send edit box inputs to analog outputs
            
            cond_1_btn = QPushButton('Set', self)
            cond_1_btn.clicked.connect(lambda: analog_value_set('cond_1', int(cond_1_edit.text())))
            saveGrid.addWidget(cond_1_btn, 0, 2)
            
            cond_2_btn = QPushButton('Set', self)
            cond_2_btn.clicked.connect(lambda: analog_value_set('cond_2', int(cond_2_edit.text())))
            saveGrid.addWidget(cond_2_btn, 1, 2)
            
            inter_1_btn = QPushButton('Set', self)
            inter_1_btn.clicked.connect(lambda: analog_value_set('inter_1', int(inter_1_edit.text())))
            saveGrid.addWidget(inter_1_btn, 2, 2)
            
            timer = QtCore.QTimer(self)
            
            #add Feedback Labels and update them to display analog inputs from corresponding channels
            
            cond_1_feed = QLabel('')
            saveGrid.addWidget(cond_1_feed, 3, 1)
            cond_1_ch = channel_dict['cond_1_ch']
            timer.timeout.connect(lambda: self.updateFeedback(cond_1_feed, 'cond_1'))
            cond_1_feed.adjustSize()
            
            cond_2_feed = QLabel('')
            saveGrid.addWidget(cond_2_feed, 4, 1)
            cond_2_ch = channel_dict['cond_2_ch']
            timer.timeout.connect(lambda: self.updateFeedback(cond_2_feed, 'cond_2'))
            #timer.timeout.connect(lambda: print(self.scan(diADC)[1]))
            cond_2_feed.adjustSize()
            
            inter_1_feed = QLabel('')
            saveGrid.addWidget(inter_1_feed, 5, 1)
            inter_1_ch = channel_dict['inter_1_ch']
            timer.timeout.connect(lambda: self.updateFeedback(inter_1_feed, 'inter_1'))
            inter_1_feed.adjustSize()
            
            timer.start(1000) 
        
        else:
            error = QLabel('No hardware detected. Make sure hardware is connected correctly, then restart program.')
            saveGrid.addWidget(error)
            
        #set the layout to the actual tab, only once it's complete
        saveTab.setLayout(saveGrid)
        
        #actually add the main overall grid to the popup window
        mainGrid.addWidget(tabs, 1, 0)
        self.setLayout(mainGrid)
        
        #name the window
        self.setWindowTitle('Lens Settings')
    
    @QtCore.pyqtSlot()
    def updateFeedback(self, label, device_name):
        label_data = analog_value_get(device_name)
        label.setText(label_data)

        
#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************
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

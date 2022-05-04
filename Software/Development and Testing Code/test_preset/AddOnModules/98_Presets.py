'''

NANOmi Electron Microscope Presets Module

This code handles the saving and loading of all values the microscope has to offer.

Initial Code:       Ricky Au
                    Adam Prus-Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
*****************************************************************************************************************
Version:            2.0 - Aug 21, 2020
By:                 Ricky Au
Notes:              Added naming system that doesn't allow for duplicate names on saving.
                    Added loading tab that displays all possible load paths and allows the user to type load file   
                    to check if possible load file.

Current issues:     Preset file can't access other files in AddOnModules since main file is in NANOmi.py
                    Load tab can only check load files in NANOmi.py directory
                    Testing of reading from other files required 60_Camera.py to be in same directory as NANOmi.py
*****************************************************************************************************************
Version:            1.0 - May 27, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Set up the initial module for creating the user interface.
*****************************************************************************************************************
'''

import sys                              #import sys module for system-level functions
import glob, os                         # allow us to access other files
#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit
from PyQt5 import QtCore, QtGui

'''
# currently getting data from each file within addon modules
# lets inport lists or dictionaries that contain all the data that wants to be brought over
# once those are brought in we will need to loop through them and get the data and put it on a text file
# reading back in will need to be done similarly by having this from ___ import * but in those files of Addon module 
# make sure to have empty pre allocated lists so no errors occur in the ther other files
'''
# Camera = __import__('60_Camera') # work around for now since module files start with numbers
buttonName = 'Save or Load Presets'     #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope

#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************
    #a function that users can modify to create their user interface
    def initUI(self):
        QWidget.__init__(self)
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
        topTextLabel = QLabel('Saving and Loading of Presets', self)
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
        
        #add a label
        label = QLabel('Save file name:')
        saveGrid.addWidget(label, 0, 0)
        
        #add an edit box to the right of the label
        self.edit = QLineEdit()
        saveGrid.addWidget(self.edit, 0, 1)
        
        #add a sample button to the first save tab
        pb = QPushButton('Save to file')
        pb.clicked.connect(self.saveButton)
        #function inputs: object, row, column, rowspan, columnspan
        saveGrid.addWidget(pb, 1, 0, 1, 2)
        
        #set the layout to the actual tab, only once it's complete
        saveTab.setLayout(saveGrid)

        # set up grid layout for load tab
        loadGrid = QGridLayout()
        loadGrid.setSpacing(10)
                
        loadLabel = QLabel("Loadable files: ")
        loadGrid.addWidget(loadLabel, 0, 0)

        # list directory
        cwd = os.getcwd()  # Get the current working directory (cwd)
        files = os.listdir(cwd)  # Get all the files in that directory
        # print("Files in %r: %s" % (cwd, files))
        # print("all listed")
        space = 0
        for file in os.listdir(cwd):
            space+=1
            if file.endswith(".txt"):
                # print(os.path.join(cwd, file)) #lists file and its path
                print(file)
                loadLabel = QLabel(file)
                loadGrid.addWidget(loadLabel, space, 0)
        
        # edit box
        self.load_edit = QLineEdit()
        loadGrid.addWidget(self.load_edit, space+1, 0)
        # load button
        lb = QPushButton('Submit file you want to load')
        lb.clicked.connect(self.loadButton)
        loadGrid.addWidget(lb, space+2, 0, 1, 2)
        #set the layout to the actual tab, only once it's complete
        loadTab.setLayout(loadGrid)

        #actually add the main overall grid to the popup window
        mainGrid.addWidget(tabs, 1, 0)
        self.setLayout(mainGrid)
        
        '''
        -Need to automate the pulling-in of all user-settable variable objects in other modules for save and load
        -Need to set up a naming system that checks if the name is already used before saving, and notifies of overwriting before doing so
        -Loading tab should display all values that will be loaded in a list box that is easily readable
        '''
        
        
        #name the window
        self.setWindowTitle('Save/Load Presets')
        
        
    def saveButton(self):
        import P_Camera
        # global P_Camera # testing with camera file
        print('Save button was pushed')
        same_name = False

        file_name = self.edit.text()+".txt"
        cwd = os.getcwd()  # Get the current working directory (cwd)
        files = os.listdir(cwd)  # Get all the files in that directory
        # print("Files in %r: %s" % (cwd, files))
        # print("all listed")
        for f in files:
            if (file_name == f):   
                same_name = True
        # do nothing if nothing was typed
        if (self.edit.text() == ''):
            print('No file name entered try again')
            pass
        elif (same_name == False):
            file = open(file_name, "w")
            # loop through the data of each file
            file.write("Camera value is " + str(P_Camera.test))
            print("file made")
            P_Camera.test = 11
            print(P_Camera.test)
            file.close()
        else:
            print("can't make file")
            pass
    def loadButton(self):
        print("load button pressed")
        same_name = False

        file_name = self.load_edit.text()

        cwd = os.getcwd()  # Get the current working directory (cwd)
        files = os.listdir(cwd)  # Get all the files in that directory
        for f in files:
            if (file_name == f):   
                same_name = True
        if same_name == True:
            print("file found")
            '''
                load the file
            '''
        else:
            print("file not found try again")
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

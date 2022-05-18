'''

NANOmi Electron Microscope

This code is the main interface window to all equipment that connects to the microscope. Each set of equipment is represented by a module (a *.py code file) that is placed in a subfolder to where this code was originally extracted.

The majority of the work is done in the background modules.  The minimum modules required for a transmission electron microscope are:
    -electron gun controls
    -lens controls
    -deflector/stigmator controls
    -stage controls
    -aperture control
    -camera control.
Each of these .py files appears as a button on this interface that spawns a popup window.

If more equipment is required aside from the above stated, copy the file _stubModule.py and rename it to reflect what the equipment does, then modify the main program to do what you need it to do.

Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
*****************************************************************************************************************
Version:            4.0 - September 10, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Removed Adam's hardware reload and made it more central in the hardware module.
*****************************************************************************************************************
Version:            3.0 - August 28, 2020
By:                 Adam Czarnecki
Notes:              Added hardware reload functionality
*****************************************************************************************************************
Version:            2.0 - July 24, 2020
By:                 Adam Czarnecki
Notes:              Added modular hardware functionality.
*****************************************************************************************************************
Version:            1.0 - May 27, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Set up the initial module loading into pushbuttons that run background code.
*****************************************************************************************************************
'''

import sys          #import sys module for system-level functions
import importlib    #import importib to allow for dynamic importing of modules
import os           #import os module to get paths in operating system native ways

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QVBoxLayout
from PyQt5.QtCore import *
from PyQt5.QtGui import *

AddOns = []

#this class handles the main window interactions, mainly initialization
class MainWindow(QWidget):
    
    
    #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.diADC = None
        self.diDAC = None
        
        self.initUI()

    #function to create the user interface, and load in external modules for equipment control
    def initUI(self):
        
        global AddOns
        
        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 250
        windowHeight = 600
        self.setGeometry(50, 50, windowWidth, windowHeight)
        
        #name the window
        self.setWindowTitle('NANOmi Microscope Control')
        
        #define the module path, which should be in a folder called AddOnModules in the same directory as the current functioning file
        modulePath = os.getcwd() + '/AddOnModules/'

        #if the AddOnModules directory exists, carry on
        if os.path.isdir(modulePath):
            
            #pull out the files in the directory AddOnModules, sort them alphanumerically
            addOnFiles = os.listdir(modulePath)
            addOnFiles.sort()
            
            #for each file in the AddOnModules directory, see if it is a proper microscope module
            for filename in addOnFiles:

                #continue if the name is a file, and not if it is a directory
                if os.path.isfile(modulePath + filename):

                    #handle case of special files like __init__ that shouldn't be loaded
                    if (not filename[0] == '_') and (filename[-3:] == '.py'):

                        #remove the extension from the filename
                        module_name = filename[:-3]
                        
                        #attempt to read in the module
                        try:
                            #print()
                            #print("module name:", module_name, "; module path:", modulePath)
                            #print()
                            AddOns.append(importlib.import_module('.'+module_name, package='AddOnModules'))
                        except ImportError as err:
                            print('Error:',err)
        
        #if the AddOnModules directory doesn't exist, throw an error and return
        else:
            #try to make the directory
            os.makedirs('AddOnModules')
            
            #throw an error to the console that called the code
            print('No AddOnModules directory exists to add extra modules. The directory was created, please add  equipment modules (lenses, stage, etc) to it and restart the software.')
            
            #in case the console message is missed, throw a pop-up message box as well - need to be clear why things didn't work
            msgBox = QMessageBox()
            msgBox.setWindowTitle('Missing equipment modules!')
            msgBox.setText('No AddOnModules directory exists to add extra modules. The directory was created, please add equipment modules (lenses, stage, etc) to it and restart the software.')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            x = msgBox.exec_()
            
            #exit the program, as no hardware code is present to run on
            sys.exit(True)
        
        #define a font for the title of the UI
        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(12)
        
        #define a font for the buttons of the UI
        buttonFont = QFont()
        buttonFont.setBold(False)
        buttonFont.setPointSize(10)
        
        vBox = QVBoxLayout()
        vBox.setSpacing(20)
        vBox.setAlignment(Qt.AlignTop)
        
        #create a label at the top of the window so we know what the software does
        topTextLabel = QLabel('NANOmi Electron Microscope', self)
        topTextLabel.setAlignment(Qt.AlignCenter)
        topTextLabel.setFixedWidth(windowWidth-10)
        topTextLabel.setWordWrap(True)
        topTextLabel.setFont(titleFont)
        vBox.addWidget(topTextLabel)
        
        #for every module that was previously loaded, run it's main program to create the user interface from the module code. Then create a pushbutton and link it's click event to the showPopup program in that module.
        hw = None
        for module in AddOns:
            result = module.main()
            if result:
                btn = QPushButton(module.buttonName, self)
                btn.clicked.connect(module.showPopUp)
                btn.setFont(buttonFont)
                if hw == None:
                    hw = btn
                else:
                    vBox.addWidget(btn)
            else:
                print('There was an error loading the module for: ' + module.buttonName)
        
        #add the hardware button at the end, but it needs to be loaded first so other modules can reference it.
        vBox.addWidget(hw)
        
        #set the layout into the widget
        self.setLayout(vBox)
        
        #show the main user interface
        self.show()
        
    #make a clean shutdown, only if intended though!
    def closeEvent(self,event):
        #generate a popup message box asking the user if they REALLY meant to shut down the software
        #note that unless they've saved variable presets etc, they would lose a lot of data if they accidentally shut down the program
        reply = QMessageBox.question(self,'Closing?', 'Are you sure you want to shut down the program?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        #respond according to the user reply
        if reply == QMessageBox.Yes:
            #if shutting down, close all spawned child windows as well via the "shutdown" method in each popup
            for module in AddOns:
                module.popWindow.shutdown()
            event.accept()
        else:
            event.ignore()


def main():
    #instantiate the application
    app = QApplication(sys.argv)
    
    #link the window to a variable, set the window to be visible
    screen = MainWindow()
    screen.show()
    
    #halt execution here until the window is closed
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

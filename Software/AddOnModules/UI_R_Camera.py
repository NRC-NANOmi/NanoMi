'''

NANOmi Electron Microscope Camera Module

This code handles the camera functions, including acquiring the data and then dislaying it

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
import os                               #import os module to run terminal commands
import subprocess                       #import module to run async commands in terminal
import pygame                           #import module to handle video stream
import pygame.camera
from pygame.locals import *
import time                             #import module to add pause (temporary)
import datetime

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit
from PyQt5 import QtCore, QtGui

#import hardware
import importlib

buttonName = 'Camera'                   #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope
videoProcess = None

#This class handles the stream from the camera
class Capture(object):
    def __init__(self):
        self.size = (640,480)
        # create a display surface. standard pygame stuff
        self.display = pygame.display.set_mode(self.size, 0)

        # this is the same as what we saw before
        self.clist = pygame.camera.list_cameras()
        print(self.clist)
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        self.cam = pygame.camera.Camera(self.clist[0], self.size)
        self.cam.start()

        # create a surface to capture to.  for performance purposes
        # bit depth is the same as that of the display surface.
        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

    def get_and_flip(self):
        # if you don't want to tie the framerate to the camera, you can check
        # if the camera has an image ready.  note that while this works
        # on most cameras, some will never return true.
        #if self.cam.query_image():
        #    print('query triggered')
        self.snapshot = self.cam.get_image()

        # blit it to the display surface.  simple!
        self.display.blit(self.snapshot, (0,0))
        pygame.display.flip()
        pygame.display.update()

    def main(self):
        going = True
        while going:
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    # close the camera safely
                    self.cam.stop()
                    going = False
                    print('Closed by user')

            self.get_and_flip()

#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************

    #these variables are settable/readable by the data sets module, and must be global in the initUI function
    global data
    data = ['ImageSizeXSet','ImageSizeYSet']
    
    #a function that users can modify to create their user interface
    def initUI(self):
        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 30
        windowHeight = 30
        self.setGeometry(350, 50, windowWidth, windowHeight)
        
        #define a font for the title of the UI
        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(12)
        
        #define a font for the buttons of the UI
        buttonFont = QtGui.QFont()
        buttonFont.setBold(False)
        buttonFont.setPointSize(10)
        
        #grid for main layout of this popup window
        mainGrid = QGridLayout()
        self.setLayout(mainGrid)
        
        btnStreamEnabler = QPushButton('Enable Camera Stream')
        btnStreamEnabler.clicked.connect(self.enableVideoStream)
        mainGrid.addWidget(btnStreamEnabler, 0, 0)

        btnCaption = QPushButton('Capture Picture')
        btnCaption.clicked.connect(self.capturePic)
        mainGrid.addWidget(btnCaption, 1, 0)

        #name the window
        self.setWindowTitle('Camera Functions')
        self.close()
        #define global variables for testing save/load
        #global ImageSizeXSet, ImageSizeYSet
        #ImageSizeXSet = QLineEdit()
        #ImageSizeXSet.setText('2048')
        #ImageSizeXSet.setFixedWidth(100)
        #ImageSizeXSet.setAlignment(QtCore.Qt.AlignCenter)
        #mainGrid.addWidget(ImageSizeXSet, 5, 0)
        
        #ImageSizeYSet = QLineEdit()
        #ImageSizeYSet.setText('2048')
        #ImageSizeYSet.setFixedWidth(100)
        #ImageSizeYSet.setAlignment(QtCore.Qt.AlignCenter)
        #mainGrid.addWidget(ImageSizeYSet, 5, 1)
    def capturePic(self):
        reply = QMessageBox.question(self,'Warning','Take a picture will pause or may terminate the video streaming, do you want to proceed?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return -1
        else:
            subprocess.Popen(['pkill', '-f', 'gphoto2'])
            time.sleep(2)

        fileName = 'image/'+datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        capProcess = subprocess.run(['gphoto2', '--capture-image-and-download', '--filename', fileName], input=b'y\n')
        #resuming the capture the movie
        subprocess.Popen(['./AddOnModules/StartCanonM50'])

        
    def enableVideoStream(self):
        print("Loading camera stream ...")
        subprocess.Popen(['./AddOnModules/StartCanonM50'])
        time.sleep(2)
        subprocess.Popen(['vlc', 'v4l2:///dev/video0'])
        

        
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

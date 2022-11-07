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
import io

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit
from PyQt5 import QtCore, QtGui


from panta_rhei.gui.blocked_signals import BlockedSignals
from panta_rhei.scripting import PRScriptingInterface
from panta_rhei.repository.image_array import ImageArray
from panta_rhei.repository.repository import Repository
from panta_rhei.image_io.image_loader import load_from_file
import threading
import numpy
import logging

import gphoto2 as gp

#import hardware
import importlib

buttonName = 'Camera'                   #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope
videoProcess = None
log = logging.getLogger()

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
        
        btnStreamEnabler = QPushButton('VLC Camera Stream')
        btnStreamEnabler.clicked.connect(self.enableVideoStream)
        mainGrid.addWidget(btnStreamEnabler, 0, 0)

        btnCaption = QPushButton('Capture Picture and Save')
        btnCaption.clicked.connect(self.capturePic)
        mainGrid.addWidget(btnCaption, 1, 0)

        self.live_pb = QPushButton('Live to Panta Rhei')
        self.live_pb.setCheckable(True)
        self.single_pb = QPushButton('Acquire to Panta Rhei')
        self.single_pb.setCheckable(True)

        mainGrid.addWidget(self.live_pb,2,0)
        mainGrid.addWidget(self.single_pb,3,0)
        self.live_pb.toggled.connect(self.on_toggle_live)
        self.single_pb.toggled.connect(self.on_toggle_single)
        self.live = False
        self.hold_live = False
        self.single = False
        self.live_view = None
        self.single_view = None
        self.live_thread = threading.Thread(name="live_thread", target=self.stream)
        global pr
        try:
            pr = PRScriptingInterface()
        except:
            print("Please open image viewer and start ZMQ server")

        self.live_name = "Live"
        self.single_name, self.single_path = "Single", os.path.join(os.getcwd(),"single.jpg")
        self.dtype = numpy.uint16
        self.tacq = 500
        self.repo = Repository()
        if self.repo.connect():
            self.repo.get_all_names()
        else:
            log.error("Couldn't connect to Repository.")
        self.repo.connect()
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
    def copy_data(self, name, fpath):
        # adapt to actual format of image data from gphoto2
        # img: ndarray  meta: {'key': value, ...}

        img, meta = load_from_file(fpath)
        # use dtype as selected in combobox for output (optional)
        img = img.astype(self.dtype)
        dtype = img.dtype
        shape = img.shape
        # checkout shared memeory object by name
        nda = self.repo.new_or_update(name, shape, dtype)
        # copy data to shared memory
        numpy.copyto(nda, img)
        # submit the update repository
        self.repo.commit(nda, meta)

    def on_toggle_live(self, checked):
        if checked:
            self.start_live()
        else:
            self.stop_live()

    def start_live(self):
        if not self.live:
            self.live = True
            if not self.live_thread.is_alive():
                self.live_thread.start()

    def stream(self):
        camera = gp.Camera()
        camera.init()
        self.live_view = pr.display_image(self.live_name)
        while self.live:
            capture = camera.capture_preview()
            filedata = capture.get_data_and_size()
            data = memoryview(filedata)
            self.copy_data(self.live_name, io.BytesIO(data))
        camera.exit()
        
    def stop_live(self):
        self.live = False
        self.live_thread.join(0)
        self.live_thread = threading.Thread(name="live_thread", target=self.stream)



    def on_toggle_single(self, checked):
        if not checked:
            with BlockedSignals(self.single_pb): 
                self.single_pb.setChecked(True)
        else:
            self.single = True
            if self.live:
                self.stop_live()
                self.hold_live = True
            self.take_single()

        
    def take_single(self):
        subprocess.run(['gphoto2', '--capture-image-and-download', '--filename','single.jpg'], input=b'y\n')
        self.copy_data(self.single_name, self.single_path)
        self.live_view = pr.display_image(self.single_name)
        with BlockedSignals(self.single_pb): 
            self.single_pb.setChecked(False)     
        self.single = False
        if self.hold_live:
            self.hold_live = False
            self.start_live()

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

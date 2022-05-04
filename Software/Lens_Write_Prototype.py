'''
COPY VERSION
NANOmi Electron Microscope Lenses Module

This code handles setting values on the lenses, as well as displaying the feedback voltage values numerically and in a time plot for chosen values.




Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
*****************************************************************************************************************
Version:            9.0 - October 25th
By:                 John Kim
Notes:              Added lens controllers for adjusting the voltages of lenses.

*****************************************************************************************************************
Version:            8.0 - September 10, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Modified the code heavily. Integrated Adam and Ricky's work together, now have a fully
                    functional hardware module.
*****************************************************************************************************************
Version:            7.0 - August 28, 2020
By:                 Adam Czarnecki
Notes:              Added hardware reload functionality
******************************************************************
**********************************************
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
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QCheckBox, QSlider, QButtonGroup
from PyQt5 import QtCore, QtGui

import importlib
# import necessary aspects of the hardware module
from AddOnModules import Hardware
from AddOnModules.SoftwareFiles import TimePlot
import time
import threading


buttonName = 'Lenses Testing'                 #name of the button on the main window that links to this code
windowHandle = None                   #a handle to the window on a global scope






#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):
    #empty variable for holding the time plot handle
    displayPlot = None
    #initialization of the local counter for the hardware module in leiu of event driven updating
    hardwareTick = 0

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************





    #a function that users can modify to create their user interface
    def initUI(self):
        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 800
        windowHeight = 1000
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


        #Create an instruction for lens 1 (C1) voltage
        self.widget = QLabel("Please, enter C1 lens voltage:\n",self)
        self.widget.move(300,40)
        self.widget.resize(300,50)


        #Create a textbox for inputting lens 1 (C1) voltage
        self.textbox = QLineEdit(self)
        self.textbox.move(300, 70)
        self.textbox.resize(200,50)


        #Create an instruction for lens 2 (C2) voltage
        self.widget2 = QLabel("Please, enter C2 lens voltage:\n",self)
        self.widget2.move(300,250)
        self.widget2.resize(300,50)

        #Create a textbox for inputting lens 2 (C2) voltage
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(300,280)
        self.textbox2.resize(200,50)

        #Create an instruction for lens 3 (C3) voltage
        self.widget3 = QLabel("Please, enter C3 lens voltage:\n",self)
        self.widget3.move(300,460)
        self.widget3.resize(300,50)

        #Create a textbox for inputting lens 3 (C3) voltage
        self.textbox3 = QLineEdit(self)
        self.textbox3.move(300,490)
        self.textbox3.resize(200,50)

        #Create a button for submitting the potential values
        self.button = QPushButton('Submit',self)
        self.button.move(300,540)
        self.button.resize(100,50)

        #Create an instruction for an oscillation value
        self.widget4 = QLabel("Please, enter an oscillation value in percentange (0% to 100%):\n",self);
        self.widget4.move(300,640)
        self.widget4.resize(400,50)

        #Create a textbox for inputting an oscillation value
        self.textbox4 = QLineEdit(self)
        self.textbox4.move(300,690)
        self.textbox4.resize(200,50)

        #Create an instruction for submitting a value for the frequency of oscillation
        self.widget6 = QLabel("Please, enter a frequency value for oscillation in Hz",self)
        self.widget6.move(300,740)
        self.widget6.resize(400,50)

        #Create a textbox for inputting a frequency value
        self.textbox5 = QLineEdit(self)
        self.textbox5.move(300,790)
        self.textbox5.resize(200,50)

        #Create an instruction widget for oscillation
        self.widget5 = QLabel('Start to oscillate?',self)
        self.widget5.move(300,840)
        self.widget5.resize(300,50)

        #Create a button for starting to oscillate
        self.button4 = QPushButton('Start',self)
        self.button4.move(300,890)
        self.button4.resize(50,50)
        self.button4.setCheckable(True) #setcheckable, setAutoExclusive, setAutoExclusive allow the button group below to distinguish which button was pushed.
        self.button4.setAutoExclusive(True)
        self.button4.setChecked(True)

        #Create a button for stopping the oscillation
        self.button5 = QPushButton('Stop',self)
        self.button5.move(350,890)
        self.button5.resize(50,50)
        self.button5.setCheckable(True)  #setcheckable, setAutoExclusive, setAutoExclusive allow the button group below to distinguish which button was pushed.
        self.button5.setAutoExclusive(True)
        self.button5.setChecked(True)

        self.btn_grp = QButtonGroup(self)
        self.btn_grp.setExclusive(True)
        self.btn_grp.addButton(self.button4,1)
        self.btn_grp.addButton(self.button5,2)
        self.btn_grp.buttonClicked.connect(self.on_click_determine)

        #Bind buttons to function on_click
        self.button.clicked.connect(self.on_click) #We want a simultaneous increment process for updating C1,C2,C3 voltage values. So we need only one submit button.
        #self.button4.clicked.connect(self.on_click4)
        self.show()

        #Initializing the voltage of lenses
        self.C1_voltage = 0
        self.C2_voltage = 0
        self.C3_voltage = 0

        #Flag for communication between on_click4 and on_click5. In other words, this flag controls the oscillation part.
        self.flag = 0;



    #Function for simultaneously incrementing/updating all the lenses' potential.
    def on_click(self):

        desired_value = self.textbox.text() #Storing inputted value from the textbox above
        desired_value2 = self.textbox2.text() #Storing inputted value from the textbox2 above
        desired_value3 = self.textbox3.text() #Storing inputted value from the textbox3 above

        if(((float(desired_value) > 5.00) | (float(desired_value) < 0)) | ((float(desired_value2) > 5.00) | (float(desired_value2) < 0)) | ((float(desired_value3) > 5.00) | (float(desired_value3) < 0)) ):
            QMessageBox.question(self,"Warning", "Please, enter a value in-between 0V and 5V.", QMessageBox.Ok, QMessageBox.Ok)
        else:
            current_voltage = self.C1_voltage
            current_voltage2 = self.C2_voltage
            current_voltage3 = self.C3_voltage

            desired_value = round(float(desired_value),3)
            desired_value2 = round(float(desired_value2),3)
            desired_value3 = round(float(desired_value3),3)

            if (desired_value - current_voltage) > 0: #If the deisred value has not reached its limit, keep incrementing.
                increment = 0.001
            elif (desired_value - current_voltage) < 0: #If the desired value is less than the current voltage, decrement.
                increment = -0.001

            if (desired_value2 - current_voltage2) > 0: #If the deisred value has not reached its limit, keep incrementing.
                increment2 = 0.001
            elif (desired_value2 - current_voltage2) < 0: #If the desired value is less than the current voltage, decrement.
                increment2 = -0.001

            if (desired_value3 - current_voltage3) > 0: #If the deisred value has not reached its limit, keep incrementing.
                increment3 = 0.001
            elif (desired_value3 - current_voltage3) < 0: #If the desired value is less than the current voltage, decrement.
                increment3 = -0.001

            if ((desired_value - current_voltage == 0) & (desired_value2 - current_voltage2 == 0) & (desired_value3-current_voltage3 == 0)): #Return if every current lens potential value has reached their limits.
                return


            #The following while loop checks if any of the lenses has not reached its limit. And if it has not reached, it would increment.
            while ((round(current_voltage,3) != desired_value) | (round(current_voltage2,3) != desired_value2) | (round(current_voltage3,3) != desired_value3)): #Condition for checking if the lenses potentials have reached their limits.
                if ((round(current_voltage,3) != desired_value)):
                    Hardware.IO.setAnalog('test1', current_voltage)
                    time.sleep(0.01) #Increment continuously and slowly enough with 0.01S in-between every increment. Please, feel free to change the amount of time if you want a faster increment for output analog voltage.
                    current_voltage += increment #If the updated value has not reached the limit, continue to increment
                    print(round(float(current_voltage),3))
                elif (round(current_voltage2,3) != desired_value2):
                    Hardware.IO.setAnalog('test2', current_voltage2)
                    time.sleep(0.01) #Increment continuously and slowly enough with 0.01S in-between every increment. Please, feel free to change the amount of time if you want a faster increment for output analog voltage.
                    current_voltage2 += increment2 #If the updated value has not reached the limit, continue to increment
                    print(round(float(current_voltage2),3))
                elif (round(current_voltage3,3) != desired_value3):  #Loop for incrementing the analog output voltage value.
                    Hardware.IO.setAnalog('test3', current_voltage3)
                    time.sleep(0.01) #Increment continuously and slowly enough with 0.01S in-between every increment. Please, feel free to change the amount of time if you want a faster increment for output analog voltage.
                    current_voltage3 += increment3 #If the updated value has not reached the limit, continue to increment
                    print(round(float(current_voltage3),3))


        self.C1_voltage = round(float(current_voltage),3)
        self.C2_voltage = round(float(current_voltage2),3)
        self.C3_voltage = round(float(current_voltage3),3)



#A function designed for oscillating between wobble value limit.
    def on_click4(self):
        desired_wobble_percentage = float(self.textbox4.text()) #Convert user inputted wobble or oscillation value into a float
        lower_bound = round(self.C1_voltage-self.C1_voltage * (0.01*desired_wobble_percentage),3) #Lower bound for the oscillation value
        upper_bound = round(self.C1_voltage+self.C1_voltage * (0.01*desired_wobble_percentage),3) #Upper bound for the oscillation value
        self.flag = 1;

        while (self.flag):
            while (self.C1_voltage > lower_bound):
                self.C1_voltage -= 0.0001
                time.sleep(1/float(self.textbox5.text()))
                Hardware.IO.setAnalog('test1', self.C1_voltage)
                print(self.C1_voltage)
            while (self.C1_voltage < upper_bound):
                self.C1_voltage += 0.0001
                time.sleep(1/float(self.textbox5.text()))
                Hardware.IO.setAnalog('test1', self.C1_voltage)
                print(self.C1_voltage)

    def on_click_determine(self):
          if (self.btn_grp.checkedId() == 1):
            print("1 clicked");
            time.sleep(0.01)
          if(self.btn_grp.checkedId() == 2):
            print("2 clicked");








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
                eval(varName + '.setText("' + str(value) + '")')
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

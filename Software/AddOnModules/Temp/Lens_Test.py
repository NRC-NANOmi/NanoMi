

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

#import csv library for reading a configuration file
import csv

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QCheckBox, QSlider, QButtonGroup
from PyQt5 import QtCore, QtGui

import importlib
# import necessary aspects of the hardware module
from AddOnModules import Hardware
from AddOnModules.SoftwareFiles import TimePlot
import time
import threading

#needed for oscillation of X and Y values for deflectors
import datetime


buttonName = 'Lenses Optics Controller'                 #name of the button on the main window that links to this code
windowHandle = None                   #a handle to the window on a global scope



#We read and import from a csv file for the default increment and wobble frequencies, and wobble percentage.
with open('ConfigFile.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    print(csv_reader)
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            #Set all the default values.
            increment_frequency= float(row[0])
            wobble_frequency = float(row[1])
            wobble_percentage = float(row[2])
            wobble_duration = float(row[3])
            voltage_increment = float(row[4])
            number_of_lenses = int(row[5])
            lower_boundary = float(row[6])
            higher_boundary = float(row[7])
            wobble_increment = float(row[8])
            line_count += 1
    print(f'Processed {line_count} lines.')

default_paramter_list = [increment_frequency, voltage_increment, wobble_frequency, wobble_percentage, wobble_duration, wobble_increment] #Default voltage controlling parameters list

print(increment_frequency)
print(wobble_frequency)
print(wobble_percentage)
print(wobble_duration)
print(voltage_increment)
print(number_of_lenses)
print(lower_boundary)
print(higher_boundary)
print(wobble_increment)



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
        windowWidth = 400
        lens_texts_height = 40*(number_of_lenses+1) #The size of all the lens textboxes and widgets

 #In order to minimize the size of the entire UI, if the size of all lenses textboxes and widgets is higher than 400 (Height of all controller parameters textboxes and widgets), set it as the size of all the lenses.
        if (lens_texts_height > 400):
            windowHeight = lens_texts_height
        else:
            windowHeight = 400

        self.setGeometry(350, 50, windowWidth, windowHeight)

        mainGrid = QGridLayout()
        self.setLayout(mainGrid)

        self.textboxes = [QLineEdit(self) for i in range(number_of_lenses)]

        #Create a list of lens voltage input boxes
        for i in range(number_of_lenses):
            self.widget = QLabel("C" + str(i+1) + '(in Volts) \n',self)
            self.widget.move(0,i*30)
            self.widget.resize(80,10)
            self.textboxes[i].move(0, i*30+10)
            self.textboxes[i].resize(50, 20)
            if (i== number_of_lenses-1): #After adding all the lenses, we want to add a submit button.
                self.button = QPushButton('Submit',self)
                self.button.move(0,i*30+40)
                self.button.resize(50,30)
                self.button.clicked.connect(self.on_click) #We want a simultaneous increment process for updating lenses voltage values. We need only one submit button.


        #Create all the oscillation buttons.
        self.wobble_buttons = [QPushButton('Oscillate',self) for i in range(number_of_lenses)]

        for i in range(number_of_lenses):
            self.wobble_buttons[i].move(50,i*30+10)
            self.wobble_buttons[i].resize(50,20)
            self.wobble_buttons[i].setObjectName('Button%d' % i) #This line is required for figuring out which wobble button or which lens has to oscillate.
            self.wobble_buttons[i].clicked.connect(self.oscillate) #When any of the wobble buttons is clicked, it goes to oscillate function.


        #Creat a list of textboxes for collecting control parameters
        self.widget2 = QLabel("Voltage increment frequency",self)
        self.widget2.move(200,0)
        self.widget2.resize(200,20)
        self.textbox1 = QLineEdit(self)
        self.textbox1.move(200,30)
        self.textbox1.resize(50,20)

        self.widget7 = QLabel("Voltage increment value",self)
        self.widget7.move(200,50)
        self.widget7.resize(200,20)
        self.textbox6 = QLineEdit(self)
        self.textbox6.move(200,80)
        self.textbox6.resize(50,20)

        self.widget3 = QLabel("Wobble frequency",self)
        self.widget3.move(200,110)
        self.widget3.resize(200,20)
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(200,140)
        self.textbox2.resize(50,20)

        self.widget4 = QLabel("Wobble percentage",self)
        self.widget4.move(200,170)
        self.widget4.resize(200,20)
        self.textbox3 = QLineEdit(self)
        self.textbox3.move(200,200)
        self.textbox3.resize(50,20)

        self.widget5 = QLabel("Wobble duration",self)
        self.widget5.move(200,230)
        self.widget5.resize(200,20)
        self.textbox4 = QLineEdit(self)
        self.textbox4.move(200,260)
        self.textbox4.resize(50,20)

        self.widget6 = QLabel("Wobble increment",self)
        self.widget6.move(200,290)
        self.widget6.resize(200,20)
        self.textbox5 = QLineEdit(self)
        self.textbox5.move(200,320)
        self.textbox5.resize(50,20)

        self.current_voltages = [0 for i in range(number_of_lenses)] #List of current lens voltages.


    #Return key (Enter) press event binder. Enter key initiates on_click function.
    def keyPressEvent(self, qKeyEvent):
        print(qKeyEvent.key())
        if qKeyEvent.key() == QtCore.Qt.Key_Return:
            self.on_click()
        else:
            super().keyPressEvent(qKeyEvent)


    #Function for incrementing/updating all the lenses' potential.
    def on_click(self):
        #The following if else statements make sure to set desired_values as 0 (default to 0) if nothing was typed into the textboxes.

        self.parameters = [self.textbox1.text(),self.textbox6.text(),self.textbox2.text(),self.textbox3.text(),self.textbox4.text(),self.textbox5.text()] #List of voltage wobble parameters collected in the textboxes.

        self.updated_parameter_list = [0, 0, 0, 0, 0, 0] #Updated voltage controlling parameters list. Be careful about whether its order matches with parameters list and default_parameters list above. Defaulted to zero.

        for i in range(len(self.parameters)):
            if (self.parameters[i] == ''): #If nothing was typed into any of voltage controlling parameter textboxes, use the default values.
                self.updated_parameter_list[i] = default_paramter_list[i] #Just keep it as it is.
            else:
                self.updated_parameter_list[i] = self.parameters[i] #If something was typed, update parameters list with that value.

        #Update all the voltage controlling parameters
        increment_frequency = self.updated_parameter_list[0]
        voltage_increment = self.updated_parameter_list[1]
        wobble_frequency = self.updated_parameter_list[2]
        wobble_percentage = self.updated_parameter_list[3]
        wobble_duration = self.updated_parameter_list[4]
        wobble_increment = self.updated_parameter_list[5]

       # print(str(increment_frequency)+" "+str(voltage_increment)+" "+str(wobble_frequency)+" "+str(wobble_percentage)+" "+str(wobble_duration)+" "+str(wobble_increment)) #See if the parameters were updated properly.

        desired_values = [] #List of desired voltage values
        updated_desired_values = []
        increments = [] #List of increment values

        for i in range(number_of_lenses):
            if (self.textboxes[i].text() != ''): #Case for something typed in the textbox.
                desired_values.append(float(self.textboxes[i].text())) #Storing inputted value from the textbox above
            else:
                desired_values.append(0) #Case for nothing typed in the textbox.

        for i in range(number_of_lenses): #See if the desired values are in-between our desired potential boundaries.
            if((desired_values[i] > higher_boundary) | (desired_values[i] < lower_boundary)):
                QMessageBox.question(self,"Warning", "Enter a value in-between " + str(lower_boundary) + " and " + str(higher_boundary), QMessageBox.Ok, QMessageBox.Ok)
            else:
                updated_desired_values.append(desired_values[i])

        desired_values_float= [round(float(item),3) for item in updated_desired_values] #Round our float values to 3 digits.

        for i in range(number_of_lenses):
            if (desired_values_float[i] - self.current_voltages[i]) > 0: #If the deisred value has not reached its limit, keep incrementing.
                increments.append(voltage_increment) #This is a default value from the config file. If you wish, please, feel free to change its value in the config txt file. Thank you.
            elif (desired_values_float[i] - self.current_voltages[i]) < 0: #If the desired value is less than the current voltage, decrement.
                increments.append(-voltage_increment)
            else:
                increments.append(0)


        #The following while loop checks if any of the lenses has not reached its limit. And if it has not reached, it would increment.
        for i in range(number_of_lenses):
            while (round(self.current_voltages[i],3) != desired_values_float[i]):
                Hardware.IO.setAnalog('test' + str(i+1), self.current_voltages[i])
                time.sleep(1/increment_frequency) #Increment continuously every increment time. Please, feel free to change the amount of time in the config file if you want a faster increment for output analog voltage.
                print(round(self.current_voltages[i],3))
                self.current_voltages[i] += increments[i] #If the updated value has not reached the limit, continue to increme



#A function designed for oscillating between wobble value limit for C1.
    def oscillate(self):

        self.parameters = [self.textbox1.text(),self.textbox6.text(),self.textbox2.text(),self.textbox3.text(),self.textbox4.text(),self.textbox5.text()] #List of voltage wobble parameters collected in the textboxes.

        self.updated_parameter_list = [0, 0, 0, 0, 0, 0] #Updated voltage controlling parameters list. Be careful about whether its order matches with parameters list and default_parameters list above. Defaulted to zero.

        for i in range(len(self.parameters)):
            if (self.parameters[i] == ''): #If nothing was typed into any of voltage controlling parameter textboxes, use the default values.
                self.updated_parameter_list[i] = default_paramter_list[i] #Just keep it as it is.
            else:
                self.updated_parameter_list[i] = int(self.parameters[i]) #If something was typed, update parameters list with that value.

        #Update all the voltage controlling parameters
        increment_frequency = self.updated_parameter_list[0]
        voltage_increment = self.updated_parameter_list[1]
        wobble_frequency = self.updated_parameter_list[2]
        wobble_percentage = self.updated_parameter_list[3]
        wobble_duration = self.updated_parameter_list[4]
        wobble_increment = self.updated_parameter_list[5]


        sending_button = self.sender()  #With this sender method, we can receive which oscillate button was pressed.
        print('%d' % int(sending_button.objectName()[6])) #It tells us which button is pressed. The reason why we use [6] is because it gives button number.
        #Without [6], for instance, it outputs button1. And we want the number part only because we can use it as an index for our current voltage list.

        button_pressed_index = int(sending_button.objectName()[6]) #Tells you which button was pressed.


        saved_value = self.current_voltages[button_pressed_index] #We save our lens voltage value before the oscillation. We need this because we want to make the lens voltage return to where it was.

        lower_bound = round(self.current_voltages[button_pressed_index]-(self.current_voltages[button_pressed_index] * (0.01*wobble_percentage)),3) #Lower bound for the oscillation value
        upper_bound = round(self.current_voltages[button_pressed_index]+(self.current_voltages[button_pressed_index] * (0.01*wobble_percentage)),3) #Upper bound for the oscillation value
        timer = 0 #set a timer for oscillation duration

        #THe following loop is responsible for oscillating lens voltage values in-between the above boundaries.

        while (timer <= wobble_duration):
            while ((self.current_voltages[button_pressed_index] > lower_bound)  & (timer <= wobble_duration)):
                #Decrement the lens voltage if it is larger than the lower bound and lower than the initial value, and oscillate until timer hits the duration.
                self.current_voltages[button_pressed_index] -= wobble_increment
                time.sleep(1/wobble_frequency) #The frequency of each increment. So, its inverse is the period of each increment
                Hardware.IO.setAnalog('test' + str(button_pressed_index + 1), self.current_voltages[button_pressed_index])
                timer += 1/wobble_frequency
                print(self.current_voltages[button_pressed_index])


            while ((self.current_voltages[button_pressed_index] < upper_bound) & (timer <= wobble_duration)):
                #Increment the lens voltage if it is less than the upper bound and higher than the initial value, and oscillate until timer hits the duration.
                self.current_voltages[button_pressed_index] += wobble_increment
                time.sleep(1/wobble_frequency)
                Hardware.IO.setAnalog('test'+ str(button_pressed_index + 1), self.current_voltages[button_pressed_index])
                timer += 1/wobble_frequency
                print(self.current_voltages[button_pressed_index])


        #After wobbling/oscillating, we make our lens voltage value go back to where it was.
        while (round(self.current_voltages[button_pressed_index] ,4) != round(saved_value,4)):
            if(self.current_voltages[button_pressed_index] > saved_value): #Case for lens voltage being higher than the initial value
                self.current_voltages[button_pressed_index]  -= voltage_increment
                print(self.current_voltages[button_pressed_index])
            else: #Case for lens voltage being lower than the initial value
                self.current_voltages[button_pressed_index]  += voltage_increment
                print(self.current_voltages[button_pressed_index])
        return


    def terminate(self): #Function to decrement all the lens voltage values to 0 when the user closes Lenses Optics Controller module
        for i in range(number_of_lenses):
            while(self.current_voltages[i] - voltage_increment > 0): #Until the decrementing process lowers the lens voltage value to 0, keep decrementing the voltage value through this loop.
                self.current_voltages[i] -= voltage_increment
                Hardware.IO.setAnalog('test' + str(i+1), self.current_voltages[i])
                print(self.current_voltages[i])
                time.sleep(0.01)
                if(self.current_voltages[i] - voltage_increment < 0): #If the decrementing process results in decrementing the voltage below zero, terminate the loop.
                    self.current_voltages[i] = 0
                    break
        return



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
        self.terminate() #Terminate all the voltage values to zero before closing the Lenses Optics Controller module.
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


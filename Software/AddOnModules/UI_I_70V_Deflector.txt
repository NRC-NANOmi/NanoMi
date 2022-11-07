import sys                              #import sys module for system-level functions

#import csv library for reading a configuration file
import csv

#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QCheckBox, QSlider, QButtonGroup, QSlider, QRadioButton, QGroupBox, QVBoxLayout, QDoubleSpinBox, QComboBox,QHBoxLayout
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import importlib
# import necessary aspects of the hardware module
from AddOnModules import Hardware, UI_U_DataSets as DataSets
from AddOnModules.SoftwareFiles import TimePlot
import time
import threading

#needed for oscillation of X and Y values for deflectors
import datetime


buttonName = '70V Deflector'                 #name of the button on the main window that links to this code
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
        windowWidth = 400
        windowHeight = 300
        self.setGeometry(350, 50, windowWidth, windowHeight)

        mainGrid = QGridLayout()
        self.setLayout(mainGrid)

        self.widget1 = QLabel("70V Deflector",self) #Widget name
        mainGrid.addWidget(self.widget1, 0,0)


        #The following block of code is responsible for slider Bx1 value
        self.groupBox1 = QGroupBox()
        self.label1 = QLabel("Bx", self)  #Add a label called Bx1 for Bx1.

        self.Bx = QDoubleSpinBox()
        self.Bx.setMinimum(-9.98)
        self.Bx.setMaximum(9.98)
        self.Bx.setValue(0)
        self.Bx.setSingleStep(0.01)
        self.Bx.valueChanged.connect(lambda: self.updateBx())

        self.BxIncrement = QComboBox()
        self.BxIncrement.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.BxIncrement.setCurrentIndex(0)
        self.BxIncrement.currentIndexChanged.connect(self.BxIncrementChange)
        #self.slider = QSlider(Qt.Horizontal)
##It should be from -5V to 5V. But, there is a binary overflow for output IO pins at +-5 V. Therefore, I decreased it to -4.99 and 4.99 V.
##And SingleStep below has to be an integer, I multiplied -4.99 and 4.99 by 100.
        #self.slider.setMinimum(-499)
        #self.slider.setMaximum(499)
        #self.slider.setValue(0) #Initial value of Bx1 slider is set as 0
        #self.slider.setTickInterval(QSlider.NoTicks)
        #self.slider.setSingleStep(5)

        self.vbox = QHBoxLayout() #box containing the first slider for controlling Bx1
        self.vbox.addWidget(self.label1)
        self.vbox.addWidget(self.Bx)
        self.vbox.addWidget(self.BxIncrement)
        self.vbox.addStretch()


        #self.slider.valueChanged.connect(self.val_changed_Bx)

        #self.widget2 = QLabel("Bx: 0",self) #Bx1 widget displaying Bx slider value

        #mainGrid.addWidget(self.widget2, 2, 0)




        #The following block of code is responsible for slider Bx2 value
        #self.groupBox6 = QGroupBox()
        self.label6 =QLabel("By",self) #Add a label called Bx2 for Bx2.

        self.By = QDoubleSpinBox()
        self.By.setMinimum(-9.98)
        self.By.setMaximum(9.98)
        self.By.setValue(0)
        self.By.setSingleStep(0.01)
        self.By.valueChanged.connect(lambda: self.updateBy())

        self.ByIncrement = QComboBox()
        self.ByIncrement.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.ByIncrement.setCurrentIndex(0)
        self.ByIncrement.currentIndexChanged.connect(self.ByIncrementChange)
        #self.slider6 = QSlider(Qt.Horizontal)
##It should be from -5V to 5V. But, there is a binary overflow for output IO pins at +-5 V. Therefore, I decreased it to -4.99 and 4.99 V.
##And SingleStep below has to be an integer, I multiplied -4.99 and 4.99 by 100.
        #self.slider6.setMinimum(-499)
        #self.slider6.setMaximum(499)
        #self.slider6.setValue(0)
        #self.slider6.setTickInterval(QSlider.NoTicks)
        #self.slider6.setSingleStep(5)

        #self.vbox6 = QVBoxLayout()
        self.vbox.addWidget(self.label6)
        self.vbox.addWidget(self.By)
        self.vbox.addWidget(self.ByIncrement)
        #self.groupBox6.setLayout(self.vbox6)
        self.groupBox1.setLayout(self.vbox)

        mainGrid.addWidget(self.groupBox1, 1, 0) #First slider for Bx1
        #self.slider6.valueChanged.connect(self.val_changed_Bx2)

        #self.widget7 = QLabel("Bx2: 0",self) #Bx2 widget displaying Bx slider value

        #mainGrid.addWidget(self.groupBox6, 2, 0) #First slider for Bx1

        #mainGrid.addWidget(self.widget7, 4, 0)




        #The following block of code is responsible for slider By1 value
        #self.groupBox2 = QGroupBox()
        #self.label2 =QLabel("By1", self) #Add a label called By1 for By1.

        #self.slider2 = QSlider(Qt.Horizontal)
##It should be from -5V to 5V. But, there is a binary overflow for output IO pins at +-5 V. Therefore, I decreased it to -4.99 and 4.99 V.
##And SingleStep below has to be an integer, I multiplied -4.99 and 4.99 by 100.
        #self.slider2.setMinimum(-499)
        #self.slider2.setMaximum(499)
        #self.slider2.setValue(0)
        #self.slider2.setTickInterval(QSlider.NoTicks)
        #self.slider2.setSingleStep(5)

        #self.vbox2 = QVBoxLayout()
        #self.vbox2.addWidget(self.label2)
        #self.vbox2.addWidget(self.slider2)
        #self.vbox2.addStretch(1)
        #self.groupBox2.setLayout(self.vbox2)

        #self.slider2.valueChanged.connect(self.val_changed_By1)

        #self.widget3 = QLabel("By1: 0",self) #By1 widget displaying By1 slider value

        #mainGrid.addWidget(self.groupBox2, 5, 0) #Second slider for By1

        #mainGrid.addWidget(self.widget3, 6, 0)


        ##The following block of code is responsible for slider By2 value
        #self.groupBox3 = QGroupBox()
        #self.label3=QLabel("By2", self) #Add a label called By2 for By2.

        #self.slider3 = QSlider(Qt.Horizontal)
##It should be from -5V to 5V. But, there is a binary overflow for output IO pins at +-5 V. Therefore, I decreased it to -4.99 and 4.99 V.
##And SingleStep below has to be an integer, I multiplied -4.99 and 4.99 by 100.
        #self.slider3.setMinimum(-499)
        #self.slider3.setMaximum(499)
        #self.slider3.setValue(0)
        #self.slider3.setTickInterval(QSlider.NoTicks)
        #self.slider3.setSingleStep(5)

        #self.vbox3 = QVBoxLayout()
        #self.vbox3.addWidget(self.label3)
        #self.vbox3.addWidget(self.slider3)
        #self.vbox3.addStretch(1)
        #self.groupBox3.setLayout(self.vbox3)

        #self.slider3.valueChanged.connect(self.val_changed_By2)

        #self.widget4 = QLabel("By2: 0",self) #By2 widget displaying By2 slider value

        #mainGrid.addWidget(self.groupBox3, 7, 0) #Third slider for By2

        #mainGrid.addWidget(self.widget4, 8, 0)


        #The following block of code is responsible for slider Xin value
        self.groupBox4 = QGroupBox()
        self.label4 =QLabel("Xin", self) #Add a label called Xin.

        self.Xin = QDoubleSpinBox()
        self.Xin.setMinimum(-4.99)
        self.Xin.setMaximum(4.99)
        self.Xin.setValue(0)
        self.Xin.setSingleStep(0.01)
        self.Xin.valueChanged.connect(lambda: self.val_changed_Xin)

        self.XinIncrement = QComboBox()
        self.XinIncrement.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.XinIncrement.setCurrentIndex(0)
        self.XinIncrement.currentIndexChanged.connect(self.XinIncrementChange)

        self.vbox4 = QHBoxLayout()
        self.vbox4.addWidget(self.label4)
        self.vbox4.addWidget(self.Xin)
        self.vbox4.addWidget(self.XinIncrement)
        self.vbox4.addStretch()




        #The following block of code is responsible for slider Yin value
        self.label5 =QLabel("Yin", self) #Add a label called Yin.

        self.Yin = QDoubleSpinBox()
        self.Yin.setMinimum(-4.99)
        self.Yin.setMaximum(4.99)
        self.Yin.setValue(0)
        self.Yin.setSingleStep(0.01)
        self.Yin.valueChanged.connect(lambda: self.val_changed_Yin)

        self.YinIncrement = QComboBox()
        self.YinIncrement.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
        self.YinIncrement.setCurrentIndex(0)
        self.YinIncrement.currentIndexChanged.connect(self.YinIncrementChange)

        self.vbox4.addWidget(self.label5)
        self.vbox4.addWidget(self.Yin)
        self.vbox4.addWidget(self.YinIncrement)
        self.groupBox4.setLayout(self.vbox4)

        mainGrid.addWidget(self.groupBox4, 2, 0)

        #Add a button for save feature
        #self.save = QPushButton()
        #self.save.setText("Save parameter values")
        #self.save.clicked.connect(self.save_button_clicked)
        #mainGrid.addWidget(self.save,13,0)


        ##Add a button for load saved parameters feature
        #self.load = QPushButton()
        #self.load.setText("Load saved parameter values")
        #self.load.clicked.connect(self.retrieve)
        #mainGrid.addWidget(self.load,14,0)



        #Add a slider for X+ deflector plate SDI integer value.
        self.groupBox_slider1 = QGroupBox()
        self.label_slider1 =QLabel("X+ SDI Value", self) #Add a label called X+ SDI value.


        self.slider_SDI1 = QSlider(Qt.Horizontal)
        #It should be from 0 to 255.
        self.slider_SDI1.setMinimum(0)
        self.slider_SDI1.setMaximum(255)
        self.slider_SDI1.setValue(0) #Initial value of SDI
        self.slider_SDI1.setTickInterval(QSlider.NoTicks)
        self.slider_SDI1.setSingleStep(1)
        self.slider_SDI1.sliderReleased.connect(self.sldReconnect1) #Update SDI value when the slider is released.


        self.vbox_SDI1 = QVBoxLayout()
        self.vbox_SDI1.addWidget(self.label_slider1)
        self.vbox_SDI1.addWidget(self.slider_SDI1)
        self.vbox_SDI1.addStretch(1)
        self.groupBox_slider1.setLayout(self.vbox_SDI1)


        mainGrid.addWidget(self.groupBox_slider1, 7, 0)


        self.widget_SDI1 =QLabel("SDI: 0", self) #SDI widget displays current SDI value.


        mainGrid.addWidget(self.widget_SDI1, 8, 0)




        #Add a slider for X- deflector plate SDI integer value.
        self.groupBox_slider2 = QGroupBox()
        self.label_slider2 =QLabel("X- SDI Value", self) #Add a label called X+ SDI value.


        self.slider_SDI2 = QSlider(Qt.Horizontal)
        #It should be from 0 to 255.
        self.slider_SDI2.setMinimum(0)
        self.slider_SDI2.setMaximum(255)
        self.slider_SDI2.setValue(0) #Initial value of SDI
        self.slider_SDI2.setTickInterval(QSlider.NoTicks)
        self.slider_SDI2.setSingleStep(1)
        self.slider_SDI2.sliderReleased.connect(self.sldReconnect2) #Update SDI value when the slider is released.


        self.vbox_SDI2 = QVBoxLayout()
        self.vbox_SDI2.addWidget(self.label_slider2)
        self.vbox_SDI2.addWidget(self.slider_SDI2)
        self.vbox_SDI2.addStretch(1)
        self.groupBox_slider2.setLayout(self.vbox_SDI2)


        mainGrid.addWidget(self.groupBox_slider2, 9, 0)


        self.widget_SDI2 =QLabel("SDI: 0", self) #SDI widget displays current SDI value.


        mainGrid.addWidget(self.widget_SDI2, 10, 0)





        #Add a slider for y+ deflector plate SDI integer value.
        self.groupBox_slider3 = QGroupBox()
        self.label_slider3 =QLabel("Y+ SDI Value", self) #Add a label called Y+ SDI value.


        self.slider_SDI3 = QSlider(Qt.Horizontal)
        #It should be from 0 to 255.
        self.slider_SDI3.setMinimum(0)
        self.slider_SDI3.setMaximum(255)
        self.slider_SDI3.setValue(0) #Initial value of SDI
        self.slider_SDI3.setTickInterval(QSlider.NoTicks)
        self.slider_SDI3.setSingleStep(1)
        self.slider_SDI3.sliderReleased.connect(self.sldReconnect3) #Update SDI value when the slider is released.


        self.vbox_SDI3 = QVBoxLayout()
        self.vbox_SDI3.addWidget(self.label_slider3)
        self.vbox_SDI3.addWidget(self.slider_SDI3)
        self.vbox_SDI3.addStretch(1)
        self.groupBox_slider3.setLayout(self.vbox_SDI3)


        mainGrid.addWidget(self.groupBox_slider3, 11, 0)


        self.widget_SDI3 =QLabel("SDI: 0", self) #SDI widget displays current SDI value.


        mainGrid.addWidget(self.widget_SDI3, 12, 0)



        #Add a slider for y- deflector plate SDI integer value.
        self.groupBox_slider4 = QGroupBox()
        self.label_slider4 =QLabel("Y- SDI Value", self) #Add a label called Y+ SDI value.


        self.slider_SDI4 = QSlider(Qt.Horizontal)
        #It should be from 0 to 255.
        self.slider_SDI4.setMinimum(0)
        self.slider_SDI4.setMaximum(255)
        self.slider_SDI4.setValue(0) #Initial value of SDI
        self.slider_SDI4.setTickInterval(QSlider.NoTicks)
        self.slider_SDI4.setSingleStep(1)
        self.slider_SDI4.sliderReleased.connect(self.sldReconnect4) #Update SDI value when the slider is released.


        self.vbox_SDI4 = QVBoxLayout()
        self.vbox_SDI4.addWidget(self.label_slider4)
        self.vbox_SDI4.addWidget(self.slider_SDI4)
        self.vbox_SDI4.addStretch(1)
        self.groupBox_slider4.setLayout(self.vbox_SDI4)


        mainGrid.addWidget(self.groupBox_slider4, 13, 0)


        self.widget_SDI4 =QLabel("SDI: 0", self) #SDI widget displays current SDI value.


        mainGrid.addWidget(self.widget_SDI4, 14, 0)



        #Initialize 18 bits of SDI value with 0. It will be fed into the digi pots. We need 18 bits to take care of both digi pots.

        self.zero_padded_SDI_binary = ['0'] * 18
        print(self.zero_padded_SDI_binary)

        #Parameters of this module are saved inside of self.data, so Datasets module can use it
        self.data = {
            'Bx': self.Bx,
            'By' : self.By,
            'Xin' : self.Xin,
            'Yin' : self.Yin,
            'X+SDI': self.slider_SDI1,
            'X-SDI' : self.slider_SDI2,
            'Y+SDI' : self.slider_SDI3,
            'Y-SDI' : self.slider_SDI4
            }

        self.plotGroupBox = QGroupBox()
        self.plot = pg.PlotWidget()
        self.plot.setXRange(-10,10)
        self.plot.setYRange(-10,10)
        self.plot.setFixedSize(400, 400)
        self.plot.setMouseEnabled(x=False,y=False)
        self.vboxPlot = QVBoxLayout()
        self.vboxPlot.addWidget(self.plot)
        self.vboxPlot.addStretch(4)
        self.plotGroupBox.setLayout(self.vboxPlot)
        mainGrid.addWidget(self.plotGroupBox, 15,0)
        self.updatePlot()

    def updatePlot(self):
        #get the coordinate of the beam
        x = self.Bx.value()
        y = self.By.value()
        #set the beam to the plot
        self.plot.plot([x], [y], clear=True, symbol='o', symbolBrush=.5)

#The following val_changed functions are activated when the slider values change. And the IO pins output accordingly.
    def updateBx(self):
        DataSets.windowHandle.refreshDataSets()
        value = self.Bx.value()
        halfVal = round(value/2,2)
        Hardware.IO.setAnalog('Bx2',str(halfVal))
        Hardware.IO.setAnalog('Bx1',str(-halfVal))
        self.updatePlot()

    def BxIncrementChange(self):
        self.Bx.setSingleStep(float(self.BxIncrement.currentText()))

    def updateBy(self):
        DataSets.windowHandle.refreshDataSets()
        value = self.By.value()
        halfVal = round(value/2,2)
        Hardware.IO.setAnalog('By2',halfVal)
        Hardware.IO.setAnalog('By1',-halfVal)
        self.updatePlot()

    def ByIncrementChange(self):
        self.By.setSingleStep(float(self.ByIncrement.currentText()))


    def val_changed_Bx1(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget2.setText("Bx1: " + str(self.slider.value()/100))
        Hardware.IO.setAnalog('Bx1',self.slider.value()/100)


    def val_changed_By1(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget3.setText("By1: " + str(self.slider2.value()/100))
        Hardware.IO.setAnalog('By1',self.slider2.value()/100)


    def val_changed_By2(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget4.setText("By2: " + str(self.slider3.value()/100))
        Hardware.IO.setAnalog('By2',self.slider3.value()/100)


    def val_changed_Xin(self):
        DataSets.windowHandle.refreshDataSets()
        Hardware.IO.setAnalog('Xin',self.Xin.value())

    def XinIncrementChange(self):
        self.Xin.setSingleStep(float(self.XinIncrement.currentText()))


    def val_changed_Yin(self):
        DataSets.windowHandle.refreshDataSets()
        Hardware.IO.setAnalog('Yin',self.Yin.value())

    def YinIncrementChange(self):
        self.Yin.setSingleStep(float(self.YinIncrement.currentText()))

    def val_changed_Bx2(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget7.setText("Bx2: " + str(self.slider6.value()/100))
        Hardware.IO.setAnalog('Bx2',self.slider6.value()/100)

    def val_changed_SDI1(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget_SDI1.setText("SDI: " + str(self.slider_SDI1.value()))
        return

    def val_changed_SDI2(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget_SDI2.setText("SDI: " + str(self.slider_SDI2.value()))
        return

    def val_changed_SDI3(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget_SDI3.setText("SDI: " + str(self.slider_SDI3.value()))
        return

    def val_changed_SDI4(self):
        DataSets.windowHandle.refreshDataSets()
        self.widget_SDI4.setText("SDI: " + str(self.slider_SDI4.value()))
        return


#update SDI value fed into the digital potentiometer with a value from a slider. (For X+ plate)
    def sldReconnect1(self):
        self.val_changed_SDI1()
        print("Slider released \n")
        Hardware.IO.setDigital('CLK1',False)
        Hardware.IO.setDigital('ChipSelect1',True) #~CS
        Hardware.IO.setDigital('SDI1',0)

        print("The current SDI input from the slider is " + str(self.slider_SDI1.value()) +"\n")
        slider1_received = bin(int(self.slider_SDI1.value())) #SDI binary value received from slider 1

        slider1_received = slider1_received[2:]  #Get rid of '0b' in front of binary value

        slider1_received = slider1_received.zfill(8) #Zero-pad to 8 bits to match with AD5262's SDI length requirements.

        slider1_received = '0' + slider1_received #If '0' is added in the beginning, we use RDAC1 (first variable resistor). And,if '1' is added, we use RDAC2 (second variable resistor).

        print("Slider binary values are: " + slider1_received) #Check if our slider value is correct


        #Update SDI value with the value from slider.
        for i in range (9, 18): #Range is from 9th bit to 17th bit because we try to update the first digi pot.
            self.zero_padded_SDI_binary[i] = slider1_received[i-9]

        print(self.zero_padded_SDI_binary)

        #Check if SDI values are correct
        print("SDI values are:")
        for n in range(len(self.zero_padded_SDI_binary)):
            print(self.zero_padded_SDI_binary[n])

        print("\n Update start:\n")
        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", False) #Before changing clk and cs values, set ~CS as 0.
        for n in range(len(self.zero_padded_SDI_binary)):
            Hardware.IO.setDigital('SDI1',int(self.zero_padded_SDI_binary[n])) #Output from the MSB first.
            print("Bit " + str(n) + " = " + self.zero_padded_SDI_binary[n]) #Check if it outputs as expected.It's flipped.
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',True) #Turn on clk
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',False) #Turn off clk
            time.sleep(0.01)

        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", True) #After changing clk and cs values, set ~CS as 1.
        time.sleep(0.05)

        return


#update SDI value fed into the digital potentiometer with a value from a slider. (For X- plate)
    def sldReconnect2(self):
        self.val_changed_SDI2()
        print("Slider released \n")
        Hardware.IO.setDigital('CLK1',False)
        Hardware.IO.setDigital('ChipSelect1',True) #~CS
        Hardware.IO.setDigital('SDI1',0)

        print("The current SDI input from the slider is " + str(self.slider_SDI2.value()) +"\n")
        slider2_received = bin(int(self.slider_SDI2.value())) #SDI binary value received from slider 1

        slider2_received = slider2_received[2:]  #Get rid of '0b' in front of binary value

        slider2_received = slider2_received.zfill(8) #Zero-pad to 8 bits to match with AD5262's SDI length requirements.

        slider2_received = '1' + slider2_received #If '0' is added in the beginning, we use RDAC1 (first variable resistor). And,if '1' is added, we use RDAC2 (second variable resistor).

        print("Slider binary values are: " + slider2_received) #Check if our slider value is correct


        #Update SDI value with the value from slider.
        for i in range (9, 18): #Range is from 9th bit to 17th bit because we try to update the first digi pot.
            self.zero_padded_SDI_binary[i] = slider2_received[i-9]

        print(self.zero_padded_SDI_binary)

        #Check if SDI values are correct
        print("SDI values are:")
        for n in range(len(self.zero_padded_SDI_binary)):
            print(self.zero_padded_SDI_binary[n])

        print("\n Update start:\n")
        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", False) #Before changing clk and cs values, set ~CS as 0.
        for n in range(len(self.zero_padded_SDI_binary)):
            Hardware.IO.setDigital('SDI1',int(self.zero_padded_SDI_binary[n])) #Output from the MSB first.
            print("Bit " + str(n) + " = " + self.zero_padded_SDI_binary[n]) #Check if it outputs as expected.It's flipped.
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',True) #Turn on clk
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',False) #Turn off clk
            time.sleep(0.01)

        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", True) #After changing clk and cs values, set ~CS as 1.
        time.sleep(0.05)

        return




#update SDI value fed into the digital potentiometer with a value from a slider. (For Y+ plate)
    def sldReconnect3(self):

        self.val_changed_SDI3()
        print("Slider released \n")
        Hardware.IO.setDigital('CLK1',False)
        Hardware.IO.setDigital('ChipSelect1',True) #~CS
        Hardware.IO.setDigital('SDI1',0)

        print("The current SDI input from the slider is " + str(self.slider_SDI3.value()) +"\n")
        slider3_received = bin(int(self.slider_SDI3.value())) #SDI binary value received from slider 1

        slider3_received = slider3_received[2:]  #Get rid of '0b' in front of binary value

        slider3_received = slider3_received.zfill(8) #Zero-pad to 8 bits to match with AD5262's SDI length requirements.

        slider3_received = '0' + slider3_received #If '0' is added in the beginning, we use RDAC1 (first variable resistor). And,if '1' is added, we use RDAC2 (second variable resistor).

        print("Slider binary values are: " + slider3_received) #Check if our slider value is correct


        #Update SDI value with the value from slider.
        for i in range (0, 9): #Range is from 0th bit to 8th bit because we try to update the second digi pot.
            self.zero_padded_SDI_binary[i] = slider3_received[i]

        print(self.zero_padded_SDI_binary)

        #Check if SDI values are correct
        print("SDI values are:")
        for n in range(len(self.zero_padded_SDI_binary)):
            print(self.zero_padded_SDI_binary[n])

        print("\n Update start:\n")
        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", False) #Before changing clk and cs values, set ~CS as 0.
        for n in range(len(self.zero_padded_SDI_binary)):
            Hardware.IO.setDigital('SDI1',int(self.zero_padded_SDI_binary[n])) #Output from the MSB first.
            print("Bit " + str(n) + " = " + self.zero_padded_SDI_binary[n]) #Check if it outputs as expected.It's flipped.
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',True) #Turn on clk
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',False) #Turn off clk
            time.sleep(0.01)

        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", True) #After changing clk and cs values, set ~CS as 1.
        time.sleep(0.05)

        return



#update SDI value fed into the digital potentiometer with a value from a slider. (For Y- plate)
    def sldReconnect4(self):

        self.val_changed_SDI4()
        print("Slider released \n")
        Hardware.IO.setDigital('CLK1',False)
        Hardware.IO.setDigital('ChipSelect1',True) #~CS
        Hardware.IO.setDigital('SDI1',0)

        print("The current SDI input from the slider is " + str(self.slider_SDI4.value()) +"\n")
        slider4_received = bin(int(self.slider_SDI4.value())) #SDI binary value received from slider 1

        slider4_received = slider4_received[2:]  #Get rid of '0b' in front of binary value

        slider4_received = slider4_received.zfill(8) #Zero-pad to 8 bits to match with AD5262's SDI length requirements.

        slider4_received = '1' + slider4_received #If '0' is added in the beginning, we use RDAC1 (first variable resistor). And,if '1' is added, we use RDAC2 (second variable resistor).

        print("Slider binary values are: " + slider4_received) #Check if our slider value is correct


        #Update SDI value with the value from slider.
        for i in range (0, 9): #Range is from 0th bit to 8th bit because we try to update the second digi pot.
            self.zero_padded_SDI_binary[i] = slider4_received[i]

        print(self.zero_padded_SDI_binary)

        #Check if SDI values are correct
        print("SDI values are:")
        for n in range(len(self.zero_padded_SDI_binary)):
            print(self.zero_padded_SDI_binary[n])

        print("\n Update start:\n")
        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", False) #Before changing clk and cs values, set ~CS as 0.
        for n in range(len(self.zero_padded_SDI_binary)):
            Hardware.IO.setDigital('SDI1',int(self.zero_padded_SDI_binary[n])) #Output from the MSB first.
            print("Bit " + str(n) + " = " + self.zero_padded_SDI_binary[n]) #Check if it outputs as expected.It's flipped.
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',True) #Turn on clk
            time.sleep(0.01)
            Hardware.IO.setDigital('CLK1',False) #Turn off clk
            time.sleep(0.01)

        time.sleep(0.05)
        Hardware.IO.setDigital("ChipSelect1", True) #After changing clk and cs values, set ~CS as 1.
        time.sleep(0.05)

        return



    def cycle(self):

        while self.runPeakPeak:

            timeDiff = datetime.datetime.now() - self.cycleStart

            #use y = mx + b, where x = time in seconds, m = -2*X_pp or -2*Y_pp, b = X_pp or Y_pp
            currentX = float(timeDiff.microseconds)/50000 * self.Xm + self.Xb
            currentY = float(timeDiff.microseconds)/50000 * self.Ym + self.Yb

            Hardware.IO.setAnalog("Xin",currentX)
            Hardware.IO.setAnalog("Yin",currentY)

            if float(timeDiff.microseconds) >= 50000:
                self.Xm = -self.Xm
                self.Xb = -self.Xb
                self.Ym = -self.Ym
                self.Yb = -self.Yb
                self.cycleStart = datetime.datetime.now()


#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************0

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
        #check if the name exists
        if name in self.data:
            #set the value
            self.data[name].setValue(int(value))
            return 0
        return -1
    #function to get a value from the module, used by DataSets
    def getValues(self):
        #return a dictionary of all variable names in data, and values for those variables
        varDict = {}
        #iterate all variables of this module
        for var in self.data:
            # Get the value of the current variable
            #double spinbox has bug when gettting values, need to round manually
            value = round(self.data[var].value(),2)
            # Check if the value is 0(default), if not, add to dic to save
            varDict[var] = str(value)
        return varDict

    #this function handles the closing of the pop-up window - it doesn't actually close, simply hides visibility.
    #this functionality allows for permanance of objects in the background
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    #this function is called on main window shutdown, and it forces the popup to close+
    def shutdown(self):
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

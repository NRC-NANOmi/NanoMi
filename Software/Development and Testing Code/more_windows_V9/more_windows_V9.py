# ---------------------------------------------------------------------------------
#    GUI prototype
# 
# A script to save data created from the program sending the data to text file 
# and test the functionality of multiple different windows under one main gui.

#    Written by: Ricky Au
# ---------------------------------------------------------------------------------
#    Version:    9 - June 26, 2020
#    By:         Ricky Au
#    Notes:      Added ability for user to build graph with line inputs
#                Added button for user to see their inputed values
#                Added button that allows user to refresh preview screen
#                Added button that allows user to create graph out of inputed values 
# 
# ---------------------------------------------------------------------------------
#    Version:    8 - June 19, 2020
#    By:         Ricky Au
#    Notes:      Added plot button not time scaled yet
#                Added a random plot just to test functionality
#                Added a controller window when plot activated that will control plot (Work in progress)                
#   
# ---------------------------------------------------------------------------------
#    Version:    7.5 - June 12, 2020
#    By:         Ricky Au
#    Notes:      Added comments to avoid confusions
#                Added more nicer layout and tool tips to incrementor window
#                cleaned up unnessasary code
#   
# ---------------------------------------------------------------------------------
#    Version:    7 - June 5, 2020
#    By:         Ricky Au
#    Notes:      Added read from previous save file using Regular expressions (Regex)
#                Added more nicer layout and tool tip to main window
#                
# ---------------------------------------------------------------------------------
#    Version:    6 - May 28, 2020
#    By:         Ricky Au
#    Notes:      Added input line to allow user to input data
#                Added restriction to input line to only take in numbers
#                Added refresh button to increment screen to allow user to see edit they make
#                Added reset button to set number to 0
#                
# ---------------------------------------------------------------------------------
#    Version:    5 - May 22, 2020
#    By:         Ricky Au
#    Notes:      Added better version of Increment window where user can see real
#                time number changes when user presses increment button
# ---------------------------------------------------------------------------------
#    Version:    4 - 
#    By:         Ricky Au
#    Notes:      Added the ability to send number from increment window to txt file 
#                
# ---------------------------------------------------------------------------------
#    Version:    3 - 
#    By:         Ricky Au
#    Notes:      Modified code to be more dynamic allowing seperate user functions
#                to not be tied together
#                
# ---------------------------------------------------------------------------------
#    Version:    2 -
#    By:         Ricky Au
#    Notes:      Created a secondary function that tests if program can handle 
#                multiple programs at the same time
#                
# ---------------------------------------------------------------------------------
#    Version:    1 - 
#    By:         Ricky Au
#    Notes:      Created a simple UI that links to one function the incrementor
#                Which increments the number when user presses the button
#                
# ---------------------------------------------------------------------------------

# import system and regex 
import sys, re, optparse
# this import seems redundent but without the graph plot won't execute properly
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout, QLabel, QGridLayout, QLineEdit, QMessageBox, QToolTip
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIntValidator, QFont
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg


display_num = 0
plot_num = list()
plot_x_axis = list()
# Main GUI that has buttons that connect to other functions
class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()


    def initUI(self):
        QWidget.__init__(self) 
        global display_num
        
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Main Window')

        layout = QGridLayout()

        QToolTip.setFont(QFont('SansSerif', 10))


        # line input that only allows for integer inputs 
        self.line_edit = QLineEdit() 
        self.onlyInt = QIntValidator()
        self.line_edit.setValidator(self.onlyInt)
        self.line_edit.setToolTip('Input number you want to start incrementor at')
        layout.addWidget(self.line_edit)
        
        # pushbutton to save number typed into line
        self.lbtn = QPushButton('save inputed number', self)
        self.lbtn.clicked.connect(self.on_click_input)
        layout.addWidget(self.lbtn)        

        # opens window with the incrementor
        self.IncBtn = QPushButton('Increment-Window', self)
        self.IncBtn.clicked.connect(self.incrementWind)
        self.IncBtn.resize(self.IncBtn.sizeHint())
        layout.addWidget(self.IncBtn)

        # opens window that creates another window that can be opened multiple times
        self.mbtn = QPushButton('Multi-Window', self)
        self.mbtn.clicked.connect(self.show_child)
        self.children = []             # place to save child window references
        layout.addWidget(self.mbtn)

        self.pbtn = QPushButton('Plot a graph', self)
        self.pbtn.clicked.connect(self.show_plot)
        self.pbtn.resize(self.pbtn.sizeHint())
        layout.addWidget(self.pbtn)

        # button that closes the whole program
        self.qbtn = QPushButton('Close whole program', self)
        self.qbtn.clicked.connect(QApplication.instance().quit)
        self.qbtn.resize(self.qbtn.sizeHint())
        layout.addWidget(self.qbtn)

        # set all the buttons in a nice layout
        self.setLayout(layout)

    # function that creates, titles and stores the multiwindow
    def show_child(self):
        child = Child() 
        child.setWindowTitle('test if title works for child')
        child.show() 
        self.children.append(child)    # save new window ref in list

    # function that creates and opens the incrementor window
    def incrementWind(self):
        self.iWindow = Incrementor()
        self.iWindow.show()

    # function that takes in the line input
    def on_click_input(self):
        global display_num
        # case where nothing is typed into the line but user still presses the button
        if (self.line_edit.text() == ''):
            display_num = 0
        # case where user does type store the number
        else:
            print(self.line_edit.text())
            display_num = int(self.line_edit.text())

    # currently only works on the main UI window when user presses the X on the top right of application
    # TODO: find a way to get qmessage box for button presses
    def closeEvent(self,event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if (reply == QMessageBox.Yes):
            event.accept()
        else:
            event.ignore()
    
    def show_plot(self):
        self.pController = Plot_Controller()
        self.pController.show()


# controller window that opens alongside plots
class Plot_Controller(QWidget):
    def __init__(self):
        super(Plot_Controller,self).__init__()
        self.show_pController()

    def show_pController(self):
        QWidget.__init__(self)
        global plot_num
        self.setGeometry(900, 300, 350, 350)
        self.setWindowTitle('Plot controller title check')

        layout = QGridLayout()

        QToolTip.setFont(QFont('SansSerif', 10))


        # line input that only allows for integer inputs 
        self.line_edit = QLineEdit() 
        self.onlyInt = QIntValidator()
        self.line_edit.setValidator(self.onlyInt)
        self.line_edit.setToolTip('Input number you want to start incrementor at')
        layout.addWidget(self.line_edit)
        
        # pushbutton to save number typed into line
        self.lbtn = QPushButton('save inputed number', self)
        self.lbtn.clicked.connect(self.on_click_input)
        layout.addWidget(self.lbtn)  

        # pushbutton that shows what our values for our plot is
        self.vbtn = QPushButton('preview inputed values', self)
        self.vbtn.clicked.connect(self.show_preview)
        layout.addWidget(self.vbtn)

        # set all the buttons in a nice layout
        self.setLayout(layout)

    # function that takes in the line input
    def on_click_input(self):
        global plot_num
        # case where nothing is typed into the line but user still presses the button
        if (self.line_edit.text() == ''):
            plot_num.append(0)
            print(plot_num)
        # case where user does type store the number
        else:
            plot_num.append(int(self.line_edit.text()))
            print(plot_num)

    def show_preview(self):
        self.preview_Controller = Preview_Window()
        self.preview_Controller.show()

# Preview window that lets user see what they have inputed in the line inputs
class Preview_Window(QWidget):
    def __init__(self):
        super(Preview_Window,self).__init__()
        self.show_Preview()
    
    def show_Preview(self):
        QWidget.__init__(self)
        global plot_num
        
        self.setGeometry(1400, 300, 350, 350)
        self.setWindowTitle('Current input values')

        layout = QVBoxLayout()
        self.list_label = QLabel(self)
        self.list_label.setText(str(plot_num))

        # refreshbtn that refreshes the onscreen number in the case where a user inputs another number into the line
        self.refreshbtn = QPushButton('refresh display number',self)
        self.refreshbtn.clicked.connect(lambda: self.on_click_refresh())
        self.refreshbtn.resize(self.refreshbtn.sizeHint())
        layout.addWidget(self.refreshbtn)

        # graph btn that graphs the inputed numbers
        self.graphbtn = QPushButton('graph current inputed numbers', self)
        self.graphbtn.clicked.connect(lambda: self.on_click_graph())
        self.graphbtn.resize(self.graphbtn.sizeHint())
        layout.addWidget(self.graphbtn)

        self.setLayout(layout)

    # function that refreshes the screen if another input is added while preview window open
    @pyqtSlot()
    def on_click_refresh(self):
        global plot_num
        self.list_label.setText(str(plot_num))
        self.list_label.adjustSize()
        
    @pyqtSlot()
    def on_click_graph(self):
        global plot_num
        global plot_x_axis

        # try making graph does nothing if no values inputed
        if not plot_num:
            print("empty list")
        else:
            # reset the x axis incase user wants to open another graph
            plot_x_axis = list()
            # start by building the x axis for graph
            for i in range(len(plot_num)):
                plot_x_axis.append(i+1)
            print(plot_x_axis)
            print(plot_num)
            self.pWindow = Plot_Window()
            self.pWindow.show()

# class that plots the graph
class Plot_Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Plot_Window,self).__init__(*args, **kwargs)
        self.show_plot_window()
    
    def show_plot_window(self):
        global plot_num
        global plot_x_axis
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        # plot data: x,y values,circles for points
        self.graphWidget.plot(plot_x_axis, plot_num, symbol='o')

          
# Incrementor window class that allows the user to increment a number on the screen and then another button that
# saves the number into a seperate txt file
class Incrementor(QWidget):
    def __init__(self):
        super(Incrementor,self).__init__()
        self.show_Incrementor()

        
    def show_Incrementor(self):
        QWidget.__init__(self)
        print('show_inc')
        global display_num

        self.setGeometry(900, 300, 350, 350)
        self.setWindowTitle('Increment window title check')

        layout = QVBoxLayout()
        
        self.num_label = QLabel(self)
        self.num_label.setText(str(display_num))
        # TODO: find a way to set Alignment of 
        # self.num_label.setAlignment(Qt.AlignCenter)

        # addbtn that adds one to the number on screen
        self.addbtn = QPushButton('add 1 to number', self)
        self.addbtn.clicked.connect(lambda: self.on_click()) 
        self.addbtn.resize(self.addbtn.sizeHint())
        layout.addWidget(self.addbtn)
        
        # textfilebtn that creates a text file of the number currently on the screen
        self.textfilebtn = QPushButton('make text file of current number', self)
        self.textfilebtn.clicked.connect(lambda: self.on_click_new_txt_file())
        self.textfilebtn.resize(self.textfilebtn.sizeHint())
        layout.addWidget(self.textfilebtn)

        # reset btn that resets the on screen number to 0
        self.resetbtn = QPushButton('reset display number',self)
        self.resetbtn.clicked.connect(lambda: self.on_click_reset())
        self.resetbtn.resize(self.resetbtn.sizeHint())
        layout.addWidget(self.resetbtn)

        # refreshbtn that refreshes the onscreen number in the case where a user inputs another number into the line
        self.refreshbtn = QPushButton('refresh display number',self)
        self.refreshbtn.clicked.connect(lambda: self.on_click_refresh())
        self.refreshbtn.resize(self.refreshbtn.sizeHint())
        layout.addWidget(self.refreshbtn)

        # readfilebtn reads a previous save file
        self.readfilebtn = QPushButton('read previous save file', self)
        self.readfilebtn.clicked.connect(lambda: self.on_click_read_txt_file())
        self.readfilebtn.resize(self.readfilebtn.sizeHint())
        layout.addWidget(self.readfilebtn)

        self.setLayout(layout)

    # function that changes the display number
    @pyqtSlot()    
    def on_click(self):
        val = self.current_num()
        self.num_label.setText(str(val))
        self.num_label.adjustSize()

    # function that adds one to the stored value in memory
    def current_num(self):
        global display_num
        display_num = display_num + 1
        return display_num

    # function that writes the current data into a text file
    @pyqtSlot()   
    def on_click_new_txt_file(self):
        global display_num
        file = open("number.txt" , "w")
        file.write("number is " + str(display_num))
        print("file made")
        file.close()
    
    # reset the data to 0 and display it
    @pyqtSlot()
    def on_click_reset(self):
        global display_num
        display_num = 0
        self.num_label.setText(str(display_num))
        self.num_label.adjustSize()
    
    # refresh the displayed value
    @pyqtSlot()
    def on_click_refresh(self):
        global display_num
        self.num_label.setText(str(display_num))
        self.num_label.adjustSize()

    # function that reads the text file data 
    @pyqtSlot()
    def on_click_read_txt_file(self):
        global display_num
        # try to read the txt file using regex to find just the data
        try:
            file = open("number.txt" , "r")
            text = file.read()
            number_list = re.findall(r"[-+]?\d*\.\d+|\d+", text)
            number = number_list[0]
            display_num = int(number)
            self.num_label.setText(str(display_num))
            self.num_label.adjustSize()
            file.close()
        # if it tried and failed nothing happens to avoid errors
        except:
            print("no previous save data")

        

# constructor for Child widget
class Child(QWidget):
    def __init__(self):
        super().__init__()

# class Controller that controlls which window to show currently not used but will be integrated into code
class Controller:

    def __init__(self):
        pass

    def show_main(self):
        self.window = MainWindow()
        self.window.show()

    def show_increment(self):
        self.window_two = Incrementor()
        self.window_two.show()

    def show_plottings(self):
        self.window_three = Plot_Window()
        self.window_three.show()

# main program
def main():	
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
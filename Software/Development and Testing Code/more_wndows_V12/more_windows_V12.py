# ---------------------------------------------------------------------------------
#    GUI prototype
# 
# Current features:
# - Incrementor             : Program that allows user to input, save, load , reset, refresh, increment numbers
# - Multiple Windows test   : Button that allows multiple instances of same program.
# - Graph Plot              : Program that allows user to graph in real time their integer inputs
# 
# ---------------------------------------------------------------------------------
# BEFORE YOU RUN:
# python3 -m pip install matplotlib
# python3 -m pip install PyQt5
# python3 -m pip install pyqtgraph
# 
# ---------------------------------------------------------------------------------
#    Written by: Ricky Au, Adam Czarnecki
# ---------------------------------------------------------------------------------
#    Version:    12 - August 7, 2020
#    By:         Ricky Au
#    Notes:      Check V10.5 for most comments
#                Added Qpaint_Test.py to more_windows program
#                Program runs but visually broken "QPaintDevice: Cannot destroy paint device that is being painted"
#                
# 
# ---------------------------------------------------------------------------------
#    Version:    11.5 - July 14, 2020
#    By:         Ricky Au
#    Notes:      Check V10.5 for most comments
#                Added V10.5 changes to V11 (needs testing)
#                
# ---------------------------------------------------------------------------------
#    Version:    11 - July 8, 2020
#    By:         Adam Czarnecki
#    Notes:      Added AIOUSB functionality
#                Modified code so that plot takes in values from AIOUSB board
#                Submitting values in edit box sends value to AIOUSB board
#
# ---------------------------------------------------------------------------------
#    Version:    10.5 - July 7, 2020
#    By:         Ricky Au
#    Notes:      Most Stable version
#                Fixed X-axis of graph to show correct time intervals
#                Added save graph inputs to text file button.
# 
# ---------------------------------------------------------------------------------
#    Version:    10 - July 3, 2020
#    By:         Ricky Au
#    Notes:      Added Real time plot with user inputs
#                Removed preview window since it was pointless in real time plot
#    Sources:    https://stackoverflow.com/questions/57891219/how-to-make-a-fast-matplotlib-live-plot-in-a-pyqt5-gui
#                Example 2 of link
# 
# ---------------------------------------------------------------------------------
#    Version:    9.5 - June 30, 2020
#    By:         Ricky Au
#    Notes:      infinite scrolling plot added(just random plot that scrolls)
#                likely best version to work off of if reading values from hardware 
#                
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

# for plot window (future has to be at front)
from __future__ import annotations

# import system and regex 
import sys, re, optparse, os
# this import seems redundent but without the graph plot won't execute properly
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout, QLabel, QGridLayout, QLineEdit, QMessageBox, QToolTip
# from PyQt5.QtCore import pyqtSlot, Qt
# from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import datetime

# for plot window 
from typing import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib as mpl
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim
# import numpy as np

display_num = 0
plot_num = list()
time_of_input = list()
plot_val = None


# Main GUI that has buttons that connect to other functions
class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()


    def initUI(self):
        QWidget.__init__(self) 
        global display_num
        
        self.setGeometry(100, 300, 500, 500)
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

        self.pltbtn = QPushButton('Plot a graph (incomplete one)', self)
        self.pltbtn.clicked.connect(self.show_plt)
        self.pltbtn.resize(self.pltbtn.sizeHint())
        layout.addWidget(self.pltbtn)

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

    def show_plt(self):
        self.pltController = Plt_Controller()
        self.pltController.show()

class Plt_Controller(QtWidgets.QMainWindow):
    def __init__(self):
        super(Plt_Controller,self).__init__()
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 400)
        self.pts = [[80, 55], [90, 90], [280, 300], [430, 220], [580, 200], [680, 300], [780, 55]]
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.draw_graph()
    
    # convert to PolygonF
    def poly(self, pts):
        return QPolygonF(map(lambda p: QPointF(*p), pts))

    def draw_graph(self):
        painter = QtGui.QPainter(self.label.pixmap())
        # initialize instance of pen for axis
        axis = QtGui.QPen()
        axis.setColor(QtGui.QColor('white'))
        painter.setPen(axis)
        painter.setOpacity(1)
        # draw x axis
        painter.drawLine(50, 350, 750, 350)
        # draw y axis
        painter.drawLine(50, 10, 50, 350)

        # draw opacity tick marker for x axis
        tick = QtGui.QPen()
        tick.setColor(QtGui.QColor('white'))
        painter.setPen(tick)
        painter.setOpacity(0.25)
        painter.drawLine(650, 10, 650, 350)
        painter.drawLine(550, 10, 550, 350)
        painter.drawLine(450, 10, 450, 350)
        painter.drawLine(350, 10, 350, 350)
        painter.drawLine(250, 10, 250, 350)
        painter.drawLine(150, 10, 150, 350)
        
        # draw text
        x_label = QtGui.QPen()
        x_label.setColor(QtGui.QColor('white'))
        painter.setPen(x_label)
        painter.setOpacity(1)
        font = QtGui.QFont()

        # font.setFamily('Times')
        # font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)

        painter.drawText(650, 360, '0')
        painter.drawText(550, 360, '-10')
        painter.drawText(450, 360, '-20')
        painter.drawText(350, 360, '-30')
        painter.drawText(250, 360, '-40')
        painter.drawText(150, 360, '-50')
        painter.drawText(50, 360, '-60')

        # polyline test
        # pts = [[80, 490], [180, 0], [280, 0], [430, 0], [580, 0], [680, 0], [780, 0]]
        pts = self.pts[:]
        points = QtGui.QPen()
        points.setColor(QtGui.QColor('blue'))
        painter.setPen(points)
        painter.drawPolyline(self.poly(pts))


        painter.end()


# controller window that opens alongside plots
class Plot_Controller(QWidget):
    def __init__(self):
        super(Plot_Controller,self).__init__()
        self.show_pController()
        self.show_plot_window()

    def show_pController(self):
        QWidget.__init__(self)
        self.setGeometry(700, 300, 350, 350)
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

        self.textfilebtn = QPushButton('make text file of inputs', self)
        self.textfilebtn.clicked.connect(lambda: self.on_click_new_txt_file())
        layout.addWidget(self.textfilebtn)

        # # pushbutton that shows what our values for our plot is
        # self.vbtn = QPushButton('preview inputed values', self)
        # self.vbtn.clicked.connect(self.show_preview)
        # layout.addWidget(self.vbtn)

        # set all the buttons in a nice layout
        self.setLayout(layout)

    # function that takes in the line input
    def on_click_input(self):
        global plot_num
        global plot_val
        global time_of_input

        current_time = datetime.datetime.now()
        print(current_time)
        time_of_input.append(current_time)
        print(time_of_input)
        # case where nothing is typed into the line but user still presses the button
        # treat as if user types 0
        if (self.line_edit.text() == ''):
            plot_num.append(0)
            print(plot_num)
            plot_val = int(self.line_edit.text())
        # case where user does type store the number
        else:
            plot_num.append(int(self.line_edit.text()))
            print(plot_num)
            plot_val = int(self.line_edit.text())
    
    def show_plot_window(self):
        self.pWindow = Plot_Window()
        self.pWindow.show()

    @pyqtSlot()
    def on_click_new_txt_file(self):
        global plot_num
        global time_of_input
        file = open("graph_inputs.txt", "w")
        for value,time in zip(plot_num,time_of_input):
            file.write("%s  %s \n" % (value,time))
        print("graph input file made")
        file.close()

    # def show_preview(self):
    #     self.preview_Controller = Preview_Window()
    #     self.preview_Controller.show()

# # Preview window that lets user see what they have inputed in the line inputs
# class Preview_Window(QWidget):
#     def __init__(self):
#         super(Preview_Window,self).__init__()
#         self.show_Preview()
    
#     def show_Preview(self):
#         QWidget.__init__(self)
#         global plot_num
        
#         self.setGeometry(1400, 300, 350, 350)
#         self.setWindowTitle('Current input values')

#         layout = QVBoxLayout()
#         self.list_label = QLabel(self)
#         self.list_label.setText(str(plot_num))

#         # refreshbtn that refreshes the onscreen number in the case where a user inputs another number into the line
#         self.refreshbtn = QPushButton('refresh display number',self)
#         self.refreshbtn.clicked.connect(lambda: self.on_click_refresh())
#         self.refreshbtn.resize(self.refreshbtn.sizeHint())
#         layout.addWidget(self.refreshbtn)

#         # graph btn that graphs the inputed numbers
#         self.graphbtn = QPushButton('graph current inputed numbers', self)
#         self.graphbtn.clicked.connect(lambda: self.on_click_graph())
#         self.graphbtn.resize(self.graphbtn.sizeHint())
#         layout.addWidget(self.graphbtn)

#         self.setLayout(layout)

#     # function that refreshes the screen if another input is added while preview window open
#     @pyqtSlot()
#     def on_click_refresh(self):
#         global plot_num
#         self.list_label.setText(str(plot_num))
#         self.list_label.adjustSize()
        
#     @pyqtSlot()
#     def on_click_graph(self):

#         self.pWindow = Plot_Window()
#         self.pWindow.show()

# class that plots the graph
class Plot_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Plot_Window,self).__init__()
        self.show_plot_window()
    
    def show_plot_window(self):
        # 1. Window settings
        self.setGeometry(1200, 300, 800, 400)
        self.setWindowTitle("live plot test")
        self.frm = QtWidgets.QFrame(self)
        self.frm.setStyleSheet("QWidget { background-color: #eeeeec; }")
        self.lyt = QtWidgets.QVBoxLayout()
        self.frm.setLayout(self.lyt)
        self.setCentralWidget(self.frm)

        # 2. Place the matplotlib figure
        self.myFig = MyFigureCanvas(x_range=[-59,1], y_range=[0, 100], interval=1000)
        self.lyt.addWidget(self.myFig)

        # 3. Show the graph window
        self.show()

# refer to source in Notes of Version 10
class MyFigureCanvas(FigureCanvas, anim.FuncAnimation):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self, x_range:List, y_range:List, interval:int) -> None:
        '''
        :param x_len:       The nr of data points shown in one plot.
        :param y_range:     Range on y-axis.
        :param interval:    Get a new datapoint every .. milliseconds.

        '''
        global plot_num
        
        FigureCanvas.__init__(self, mpl_fig.Figure())
        # Range settings
        x_len = 60
        self._x_len_ = x_len
        print(self._x_len_)
        self._y_range_ = y_range

        # Store two lists _x_ and _y_
        x = list(range(x_range[0],x_range[1]))
        # x = np.array([-60,-55,-50,-45,-40,-35,-30,-25,-20,-15,-10,-5,0]) # trying to set x axis but get error "ValueError: x and y must have same first dimension, but have shapes (13,) and (60,)"
        # y = np.array([0] * x)
        y = [0] * x_len

        # Store a figure and ax
        self._ax_  = self.figure.subplots()

        # self._ax_.set_xlim(xmin=-60, xmax=0) # this changes the x axis numbers but it sets actual limits on the x axis
        self._ax_.set_ylim(ymin=self._y_range_[0], ymax=self._y_range_[1])
        self._ax_.set_xlabel('time (s)')
        self._ax_.set_ylabel('values (int)')
        self._line_, = self._ax_.plot(x, y)

        # Call superclass constructors
        anim.FuncAnimation.__init__(self, self.figure, self._update_canvas_, fargs=(y,), interval=interval, blit=True)
        return

    def _update_canvas_(self, i, y) -> None:
        '''
        This function gets called regularly by the timer.

        '''
        y.append(round(self.get_next_datapoint(), 2))     # Add new datapoint
        y = y[-self._x_len_:]                        # Truncate list _y_ (get last element and push to left)
        self._line_.set_ydata(y)
        return self._line_,
    
    def get_next_datapoint(self):
        global plot_val
        # if nothing is inputed set graph to display 0
        if (plot_val == None):
            val = 0
        else:
            val = plot_val
            plot_val = None # after a value is inputed set the plot value back to nothing is inputed
        return val

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
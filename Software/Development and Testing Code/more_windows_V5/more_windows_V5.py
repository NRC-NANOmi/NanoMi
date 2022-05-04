# ---------------------------------------------------------------------------------
#    GUI prototype
# 
# A script to save data created from the program sending the data to text file 
# and test the functionality of multiple different windows under one main gui.

#    Written by: Ricky Au

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

import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout, QLabel, QGridLayout, QLineEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator


display_num = 0

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

        self.qbtn = QPushButton('Quit', self)
        self.qbtn.clicked.connect(QApplication.instance().quit)
        self.qbtn.resize(self.qbtn.sizeHint())
        self.qbtn.move(20,20)
        layout.addWidget(self.qbtn)
        self.setLayout(layout)

        self.IncBtn = QPushButton('Increment-Window', self)
        self.IncBtn.clicked.connect(self.incrementWind)
        self.IncBtn.resize(self.IncBtn.sizeHint())
        self.IncBtn.move(20,60)

        self.mbtn = QPushButton('Multi-Window', self)
        self.mbtn.clicked.connect(self.show_child)
        self.children = []             # place to save child window references

    def show_child(self):
        child = Child() 
        child.setWindowTitle('test if title works for child')
        child.show() 
        self.children.append(child)    # save new window ref in list

    def incrementWind(self):
        self.iWindow = Incrementor()
        self.iWindow.show()
        
    
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


        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Increment window title check')

        self.layout = QVBoxLayout()
        self.label = QLabel('press button to increment ')
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.addbtn = QPushButton('add 1 to number', self)


        self.num_label = QLabel(self)
        self.num_label.setText(str(display_num))

        
        self.addbtn.clicked.connect(lambda: self.on_click()) 
        self.addbtn.resize(self.addbtn.sizeHint())
        self.addbtn.move(0,50)


        self.textfilebtn = QPushButton('make text file of current number', self)
        self.textfilebtn.clicked.connect(lambda: self.on_click_new_txt_file())
        self.textfilebtn.resize(self.textfilebtn.sizeHint())
        self.textfilebtn.move(20,90)


    @pyqtSlot()    
    def on_click(self):
        val = self.current_num()
        self.num_label.setText(str(val))
        self.num_label.adjustSize()

    def current_num(self):
        global display_num
        # print('add 1')
        display_num = display_num + 1
        # print(number)
        return display_num

    @pyqtSlot()   
    def on_click_new_txt_file(self):
        global display_num
        file = open("number.txt" , "w")
        file.write("number is " + str(display_num))
        print("file made")
        file.close()
        


class Child(QWidget):
    def __init__(self):
        super().__init__()

class Controller:

    def __init__(self):
        pass

    def show_main(self):
        self.window = MainWindow()
        self.window.show()

    def show_increment(self):
        self.window_two = Incrementor()
        self.window_two.show()

def main():	
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


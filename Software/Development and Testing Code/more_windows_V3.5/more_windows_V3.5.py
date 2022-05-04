# shift to have all on initUI() then have the defs be on click of each button
# get number to show and allow user to input number to start incrementing from there
import sys
# from   PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout, QLabel, QGridLayout, QLineEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator

#global variable
display_num = 0

class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow,self).__init__()# if we don't include we get RuntimeError: super-class __init__() of type MainWindow was never called
        self.initUI()


    def initUI(self):
        QWidget.__init__(self) # if we don't include we get RuntimeError: super-class __init__() of type MainWindow was never called
        global display_num
        
        # X, Y , WIDTH, HEIGHT of the whole object(window)
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Main Window')

        layout = QGridLayout()

        # these lines allow user to input only numbers any non numbers don't show
        self.line_edit = QLineEdit() 
        self.onlyInt = QIntValidator()
        self.line_edit.setValidator(self.onlyInt)
        layout.addWidget(self.line_edit)
        display_num = self.line_edit

        # line edit button that saves what is in lineedit when pressed
        self.lbtn = QPushButton('input number', self)
        self.lbtn.clicked.connect(self.on_click_input)
        self.lbtn.move(20,40)


        # pushbutton function with name quit displayed
        self.qbtn = QPushButton('Quit', self)
        # what happens to the button if clicked
        self.qbtn.clicked.connect(QApplication.instance().quit)
        # QApplication.instance() calls QCoreApplication which containcs the main event loop 
        # THAT MEANS it processes and dispatches all events.
        self.qbtn.resize(self.qbtn.sizeHint())
        self.qbtn.move(20,20)
        layout.addWidget(self.qbtn)
        self.setLayout(layout)

        self.IncBtn = QPushButton('Increment-Window', self)
        # box = QVBoxLayout() # if we comment these 3 out we don't get the error where MainWindow says layout is trying to occur twice
        # box.addWidget(IncBtn)
        # self.setLayout(box)
        self.IncBtn.clicked.connect(self.incrementWind)
        self.IncBtn.resize(self.IncBtn.sizeHint())
        self.IncBtn.move(20,60)
        # self.increment = []  # place to save incrementor window ref DONT NEED SINCE ONLY WANT 1


        self.mbtn = QPushButton('Multi-Window', self)
        self.mbtn.clicked.connect(self.show_child)
        self.children = []             # place to save child window refs

    def show_child(self):
        child = Child() #calls the class child below
        # child.setGeometry(300, 300, 250, 150) # this line makes it so everything is placed on same spot 
        child.setWindowTitle('test if title works for child')
        child.show() 
        self.children.append(child)    # save new window ref in list

    def incrementWind(self):
        self.iWindow = Incrementor()
        self.iWindow.show()
        
    def on_click_input(self):
        global display_num
        print(self.line_edit.text())
        display_num = int(self.line_edit.text())

class Incrementor(QWidget):
    def __init__(self):
        super(Incrementor,self).__init__()# if we don't include we get RuntimeError: super-class __init__() of type MainWindow was never called
        print('initiation')
        self.show_Incrementor()

        

    def show_Incrementor(self):
        QWidget.__init__(self)
        print('show_inc')
        global display_num

        # val = display_num 

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Increment window title check')

        self.layout = QVBoxLayout()
        self.label = QLabel('press button to increment ')
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.addbtn = QPushButton('add 1 to number', self)

        # display_num = self.current_num()
        self.num_label = QLabel(self)
        self.num_label.setText(str(display_num))

        # self.addbtn.clicked.connect(lambda: self.current_num(display_num))
        self.addbtn.clicked.connect(lambda: self.on_click()) # uses lambda since connect expects callable function
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

# class Increment(QWidget):
#     def __init__(self):
#         super().__init__()

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


# PLAN TMR ADD Another window that opens from main one and that window will have a button that increments by 1 when pressed
# if they ask what you are up to. tell them ran into issue where if you run in super user get error code and beforehand we got that error if we didn't run it in su
# ask if they will be using opensuse and 
import sys
# from   PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout

class Parent(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.initIncrement()
        self.initMultiWindowStorage() # doing this is way more cleaner then the commented out area

        

        
        # button = QPushButton()
        # vbox = QVBoxLayout()
        # vbox.addWidget(button)
        # self.setLayout(vbox)
        # button.clicked.connect(self.show_child)
        # self.children = []             # place to save child window refs

    def initUI(self):

        # pushbutton function with name quit displayed
        qbtn = QPushButton('Quit', self)
        # what happens to the button if clicked
        qbtn.clicked.connect(QApplication.instance().quit)
        # QApplication.instance() calls QCoreApplication which containcs the main event loop 
        # THAT MEANS it processes and dispatches all events.
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50,20)
        
        # X, Y , WIDTH, HEIGHT of the whole object(window)
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Main Window')
        self.show()


    def initMultiWindowStorage(self): 
        button = QPushButton('Multi-Window', self)
        vbox = QVBoxLayout()
        vbox.addWidget(button)
        self.setLayout(vbox)
        button.clicked.connect(self.show_child)
        self.children = []             # place to save child window refs

    def initIncrement(self):
        IncBtn = QPushButton('Increment-Window', self)

        box = QVBoxLayout()
        box.addWidget(IncBtn)
        self.setLayout(box)

        IncBtn.clicked.connect(self.show_Incrementor)
        IncBtn.resize(IncBtn.sizeHint())
        IncBtn.move(20,20)


    def show_child(self):
        child = Child() #calls the class child below
        # child.setGeometry(300, 300, 250, 150) # this line makes it so everything is placed on same spot 
        child.setWindowTitle('test if title works for child')
        child.show()
        self.children.append(child)    # save new window ref in list
    
    def show_Incrementor(self):
        incrementor = Increment()
        incrementor.setGeometry(300, 300, 250, 150)
        incrementor.setWindowTitle('Increment window title check')
        incrementor.show()


class Child(QWidget):
    def __init__(self):
        super().__init__()

class Increment(QWidget):
    def __init__(self):
        super().__init__()
    		
app = QApplication(sys.argv)
screen = Parent()
screen.show()
sys.exit(app.exec_())



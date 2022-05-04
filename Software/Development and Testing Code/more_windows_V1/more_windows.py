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
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Quit Button')
        self.show()

    def initMultiWindowStorage(self): 
        button = QPushButton('Multi-Window', self)
        vbox = QVBoxLayout()
        vbox.addWidget(button)
        self.setLayout(vbox)
        button.clicked.connect(self.show_child)
        self.children = []             # place to save child window refs

        

    def show_child(self):
        child = Child() #calls the class shild below
        child.show()
        self.children.append(child)    # save new window ref in list

class Child(QWidget):
    def __init__(self):
        super().__init__()
    		
app = QApplication(sys.argv)
screen = Parent()
screen.show()
sys.exit(app.exec_())



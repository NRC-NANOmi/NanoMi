# shift to have all on initUI() then have the defs be on click of each button

import sys
# from   PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        # self.initMultiWindowStorage() # doing this is way more cleaner then the commented out area

        # self.initIncrement()   # don't really need this since it can jsut be part of initUI()

        
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

        IncBtn = QPushButton('Increment-Window', self)
        # box = QVBoxLayout() # if we comment these 3 out we don't get the error where MainWindow says layout is trying to occur twice
        # box.addWidget(IncBtn)
        # self.setLayout(box)
        IncBtn.clicked.connect(self.show_Incrementor)
        IncBtn.resize(IncBtn.sizeHint())
        IncBtn.move(20,60)
        self.increment = []  # place to save incrementor window ref


        button = QPushButton('Multi-Window', self)
        vbox = QVBoxLayout() # for some reason these three is fine 
        vbox.addWidget(button)
        self.setLayout(vbox)
        button.clicked.connect(self.show_child)
        self.children = []             # place to save child window refs
        
        
        
        
        # X, Y , WIDTH, HEIGHT of the whole object(window)
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Main Window')
        self.show()


    # def initMultiWindowStorage(self): 
    #     button = QPushButton('Multi-Window', self)
    #     vbox = QVBoxLayout()
    #     vbox.addWidget(button)
    #     self.setLayout(vbox)
    #     button.clicked.connect(self.show_child)
    #     self.children = []             # place to save child window refs

    # def initIncrement(self):
    #     # IncBtn = QPushButton('Increment-Window', self)

    #     # box = QVBoxLayout()
    #     # box.addWidget(IncBtn)
    #     # self.setLayout(box)

    #     # IncBtn.clicked.connect(self.show_Incrementor)
    #     # IncBtn.resize(IncBtn.sizeHint())
    #     # IncBtn.move(20,20)

    #     IncBtn = QPushButton('Increment-Window', self)
    #     # box = QVBoxLayout() # if we comment these 3 out we don't get the error where MainWindow says layout is trying to occur twice
    #     # box.addWidget(IncBtn)
    #     # self.setLayout(box)
    #     IncBtn.clicked.connect(self.show_Incrementor)
    #     IncBtn.resize(IncBtn.sizeHint())
    #     IncBtn.move(20,60)
        

    def show_Incrementor(self):

        incrementor = Increment()
        incrementor.setGeometry(300, 300, 250, 150)
        incrementor.setWindowTitle('Increment window title check')

        incrementor.layout = QVBoxLayout()
        incrementor.label = QLabel('press button to increment ')
        incrementor.layout.addWidget(incrementor.label)
        incrementor.setLayout(incrementor.layout)

        incrementor.addbtn = QPushButton('add 1 to number', self)

        # btn = incrementor.addbtn

        # qvbox = QVBoxLayout() # these three give warnign about layout already made in MainWindow
        # qvbox.addWidget(addbtn)
        # self.setLayout(qvbox)

        # btn.clicked.connect(self.show_child)
        # btn.resize(btn.sizeHint())
        # btn.move(50,50)
        
        incrementor.addbtn.clicked.connect(self.show_child)
        incrementor.addbtn.resize(incrementor.addbtn.sizeHint())
        incrementor.addbtn.move(50,50)

        # addbtn.show() #doing this will make it so it shows on main screen not what i want

        # self.show() # will not show anything when incrementor clicked
        incrementor.show()
        self.increment.append(incrementor)
        

    def show_child(self):
        child = Child() #calls the class child below
        # child.setGeometry(300, 300, 250, 150) # this line makes it so everything is placed on same spot 
        child.setWindowTitle('test if title works for child')
        child.show()
        self.children.append(child)    # save new window ref in list
    
    


class Child(QWidget):
    def __init__(self):
        super().__init__()

class Increment(QWidget):
    def __init__(self):
        super().__init__()

def main():	
    app = QApplication(sys.argv)
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


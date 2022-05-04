import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from time import sleep
x1 = 600
x2 = 650

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.draw_graph()

    # convert to PolygonF
    def poly(self, pts):
        return QPolygonF(map(lambda p: QPointF(*p), pts))
    
    def update_plot(self):
        print("in update_plot")
        global x1
        global x2
        sleep(1)
        x1 = x1 - 50
        x2 = x2 - 50 
        self.draw_graph()

    def draw_graph(self):
        global x1
        global x2
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 400)
        p1 = [x1, 55]
        p2 = [x2, 90]
        self.pts = [p1, p2]
        # self.pts = [[80, 55], [90, 90], [280, 300], [430, 220], [580, 200], [680, 300], [780, 55]]
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

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


        pts = self.pts[:]
        points = QtGui.QPen()
        points.setColor(QtGui.QColor('blue'))
        painter.setPen(points)
        painter.drawPolyline(self.poly(pts))

        # while True:
        #     print("in loop")
        #     # polyline test
        #     x1 = x1 - 50
        #     x2 = x2 - 50 
        #     sleep(1)
        #     pts = self.pts[:]
        #     painter.drawPolyline(self.poly(pts))
            


        # # polyline test
        # pts = self.pts[:]
        # points = QtGui.QPen()
        # points.setColor(QtGui.QColor('blue'))
        # painter.setPen(points)
        # painter.drawPolyline(self.poly(pts))
        self.update_plot()
        painter.end()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
'''

NANOmi Electron Microscope Time plotter Module

This code acts provides an interface that gives users visual feedback on the changes they make to the microscope, in the form of a scrolling time-based plot.

Initial Code:       Ricky Au
Initial Date:       August 31, 2020
*****************************************************************************************************************
Version:            2.0 - October 6, 2020
By:                 Darren Homeniuk, P. Eng.
Notes:              Worked on the entire interface, allowed some variables to be set externally like axis names, 
                    plot names and the like.
*****************************************************************************************************************
Version:            1.0 - August 31, 2020
By:                 Ricky Au
Notes:              Bare-bones basics provided to Darren.
*****************************************************************************************************************
'''
import sys, random, datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGridLayout, QCheckBox, QLineEdit
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPolygonF
import math
        
#a class to simply fill in the background
class _Title(QtWidgets.QWidget):
    #initializations
    plotTitle = 'Plot Title'
    
    def paintEvent(self, e):
        #define the painter
        painter = QPainter(self)
        
        #define a brush for the background of the axis area
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        
        #define a rectangle to fill the axis area background
        rect = QtCore.QRect(0,0,painter.device().width(),painter.device().height())
        painter.fillRect(rect,brush)
        
        #define width and height for centering
        w = self.width()
        h = self.height()
        
        title = QtGui.QPen()
        title.setColor(QtGui.QColor('white'))
        painter.setPen(title)
        painter.setOpacity(1)
        font = QtGui.QFont()

        #set up the text labels
        font.setBold(True)
        font.setPointSize(18)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, w, h), Qt.AlignCenter|Qt.AlignCenter, self.plotTitle)
    
    #initialization sets the size policy to a fixed height and flexible width
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)

    #this function is internally linked to setSizePolicy, and suggests an initial size for this object    
    def sizeHint(self):
        return QtCore.QSize(0, 30)
    
#a class for the horizontal axes of the plot - only needs update infrequently, on size changes
class _HorizontalAxes(QtWidgets.QWidget):
    #initialization sets the size policy to a fixed height and flexible width
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
    
    #this function is internally linked to setSizePolicy, and suggests an initial size for this object
    def sizeHint(self):
        return QtCore.QSize(0, 40)
    
    #paint event runs when the window is resized or the class' "update" routine is called
    def paintEvent(self, e):
        #define the painter
        painter = QPainter(self)
        
        #define a brush for the background of the axis area
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        
        #define a rectangle to fill the axis area background
        rect = QtCore.QRect(0,0,painter.device().width(),painter.device().height())
        painter.fillRect(rect,brush)
        
        #define the height and width of the area to be able to divide the ticks properly
        w = rect.width()
        h = rect.height()
        
        # draw opacity tick marker for x axis
        tick = QtGui.QPen()
        tick.setColor(QtGui.QColor('white'))
        painter.setPen(tick)
        painter.setOpacity(1)
        painter.drawLine(6*w/6, 0, 6*w/6, 5)
        painter.drawLine(5*w/6, 0, 5*w/6, 5)
        painter.drawLine(4*w/6, 0, 4*w/6, 5)
        painter.drawLine(3*w/6, 0, 3*w/6, 5)
        painter.drawLine(2*w/6, 0, 2*w/6, 5)
        painter.drawLine(1*w/6, 0, 1*w/6, 5)
        painter.drawLine(0*w/6, 0, 0*w/6, 5)
        #draw horizontal axis marker line
        painter.drawLine(0, 0, w, 0)
        
        # draw text
        x_label = QtGui.QPen()
        x_label.setColor(QtGui.QColor('white'))
        painter.setPen(x_label)
        painter.setOpacity(1)
        font = QtGui.QFont()

        #set up the text labels
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(6*w/6-9, 20, '0')
        painter.drawText(5*w/6-7, 20, '10')
        painter.drawText(4*w/6-7, 20, '20')
        painter.drawText(3*w/6-7, 20, '30')
        painter.drawText(2*w/6-7, 20, '40')
        painter.drawText(1*w/6-7, 20, '50')
        painter.drawText(0*w/6-0, 20, '60')
        painter.drawText(QRect(0, 0, w, h), Qt.AlignCenter|Qt.AlignBottom, 'Time [seconds past]')
        
#a class for the vertical axes of the plot - only needs update infrequently, on size changes
class _VerticalAxes(QtWidgets.QWidget):
    #initializations
    axisLabel = 'Values [au]'
    vertAxisMax = 100
    vertAxisMin = 0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Ignored)
    
    #this function is internally linked to setSizePolicy, and suggests an initial size for this object
    def sizeHint(self):
        return QtCore.QSize(60, 0)
    
    def paintEvent(self, e):
        #define the painter
        painter = QPainter(self)
        
        #define a brush for the background of the axis area
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        
        #define a rectangle to fill the axis area background
        rect = QtCore.QRect(0,0,painter.device().width(),painter.device().height())
        painter.fillRect(rect,brush)
        
        #define the height and width of the area to be able to divide the ticks properly
        w = rect.width()
        h = rect.height()
        
        # draw opacity tick marker for x axis
        tick = QtGui.QPen()
        tick.setColor(QtGui.QColor('white'))
        painter.setPen(tick)
        painter.setOpacity(1)
        painter.drawLine(w, 5*h/5-1, w-5, 5*h/5-1)
        painter.drawLine(w, 4*h/5, w-5, 4*h/5)
        painter.drawLine(w, 3*h/5, w-5, 3*h/5)
        painter.drawLine(w, 2*h/5, w-5, 2*h/5)
        painter.drawLine(w, 1*h/5, w-5, 1*h/5)
        painter.drawLine(w, 0*h/5, w-5, 0*h/5)
        #draw vertical axis marker line
        painter.drawLine(w-1, 0, w-1, h)
        
        # draw text
        x_label = QtGui.QPen()
        x_label.setColor(QtGui.QColor('white'))
        painter.setPen(x_label)
        painter.setOpacity(1)
        font = QtGui.QFont()

        #set up the text labels
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        #use the externally set maximum and minimum values
        t0 = str(self.vertAxisMin)
        t1 = str(self.vertAxisMin + (self.vertAxisMax-self.vertAxisMin)*1/5)
        t2 = str(self.vertAxisMin + (self.vertAxisMax-self.vertAxisMin)*2/5)
        t3 = str(self.vertAxisMin + (self.vertAxisMax-self.vertAxisMin)*3/5)
        t4 = str(self.vertAxisMin + (self.vertAxisMax-self.vertAxisMin)*4/5)
        t5 = str(self.vertAxisMin + (self.vertAxisMax-self.vertAxisMin)*5/5)
        painter.drawText(QRect(w-45, 5*h/5-16, 40, 20), Qt.AlignRight|Qt.AlignVCenter, t0)
        painter.drawText(QRect(w-45, 4*h/5-10, 40, 20), Qt.AlignRight|Qt.AlignVCenter, t1)
        painter.drawText(QRect(w-45, 3*h/5-10, 40, 20), Qt.AlignRight|Qt.AlignVCenter, t2)
        painter.drawText(QRect(w-45, 2*h/5-10, 40, 20), Qt.AlignRight|Qt.AlignVCenter, t3)
        painter.drawText(QRect(w-45, 1*h/5-10, 40, 20), Qt.AlignRight|Qt.AlignVCenter, t4)
        painter.drawText(QRect(w-45, 0*h/5 -4, 40, 20), Qt.AlignRight|Qt.AlignVCenter, t5)
        painter.translate(0, h)
        painter.rotate(-90.0)
        
        #pull in the axis label from outside the class
        painter.drawText(QRect(0, 0, h, w/2), Qt.AlignCenter|Qt.AlignTop, self.axisLabel)

#a class to simply fill in the background
class _Filler(QtWidgets.QWidget):
    def paintEvent(self, e):
        #define the painter
        painter = QPainter(self)
        
        #define a brush for the background of the axis area
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        
        #define a rectangle to fill the axis area background
        rect = QtCore.QRect(0,0,painter.device().width(),painter.device().height())
        painter.fillRect(rect,brush)
    
    #initialization sets the size policy to a fixed height and flexible width
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

    #this function is internally linked to setSizePolicy, and suggests an initial size for this object    
    def sizeHint(self):
        return QtCore.QSize(60, 40)
    
#a class for the canvas that holds the actual plot data
class _Canvas(QtWidgets.QWidget):
    #initializations
    valuesA = []
    valuesB = []
    valuesC = []
    valuesD = []
    times = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        
    def sizeHint(self):
        return QtCore.QSize(600, 400)
    
    def paintEvent(self, e):
        #define the painter
        painter = QPainter(self)
        
        #define a brush for the rectangle to fill in the background
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        
        #fill in the background of the canvas area
        rect = QtCore.QRect(0,0,painter.device().width(),painter.device().height())
        painter.fillRect(rect,brush)
        
        #define the height and width of the area to be able to divide the ticks properly
        w = rect.width()
        h = rect.height()
        
        # draw opacity tick marker for x axis
        tick = QtGui.QPen()
        tick.setColor(QtGui.QColor('white'))
        
        painter.setPen(tick)
        painter.setOpacity(1)
        
        #draw the top and right lines
        painter.drawLine(w-1, 0, w-1, h)
        painter.drawLine(  0, 0, w-1, 0)
        
        #draw on-canvas lines, dashed, to help see values
        painter.setOpacity(0.2)
        tick.setStyle(Qt.DashLine)
        painter.setPen(tick)
        
        #horizontal lines
        painter.drawLine(0, 4*h/5,   w, 4*h/5)
        painter.drawLine(0, 3*h/5,   w, 3*h/5)
        painter.drawLine(0, 2*h/5,   w, 2*h/5)
        painter.drawLine(0, 1*h/5,   w, 1*h/5)
        
        #vertical lines
        painter.drawLine(5*w/6, 0, 5*w/6, h)
        painter.drawLine(4*w/6, 0, 4*w/6, h)
        painter.drawLine(3*w/6, 0, 3*w/6, h)
        painter.drawLine(2*w/6, 0, 2*w/6, h)
        painter.drawLine(1*w/6, 0, 1*w/6, h)
        
        #define scale values for plot
        mx = (0-w)/(60-0)
        bx = w
        my = (0-h)/(self.parent()._VAxes.vertAxisMax - self.parent()._VAxes.vertAxisMin)
        by = h - my * self.parent()._VAxes.vertAxisMin
        
        #define pens for plots
        painter.setOpacity(1)
        colorA = QtGui.QPen()
        colorA.setColor(QtGui.QColor('red'))
        colorB = QtGui.QPen()
        colorB.setColor(QtGui.QColor('blue'))
        colorC = QtGui.QPen()
        colorC.setColor(QtGui.QColor('green'))
        colorD = QtGui.QPen()
        colorD.setColor(QtGui.QColor('yellow'))
        
        showA = self.parent().enables[0] == True and self.parent().display[0] == True
        showB = self.parent().enables[1] == True and self.parent().display[1] == True
        showC = self.parent().enables[2] == True and self.parent().display[2] == True
        showD = self.parent().enables[3] == True and self.parent().display[3] == True
        
        for i in range(len(self.valuesA)-1):
            xPt1 = self.times[i]
            xPt2 = self.times[i+1]
            
            if showA:
                yPt1 = self.valuesA[i]
                yPt2 = self.valuesA[i+1]
                painter.setPen(colorA)
                painter.drawLine(mx*xPt1+bx, my*yPt1+by, mx*xPt2+bx, my*yPt2+by)
            
            if showB:
                yPt1 = self.valuesB[i]
                yPt2 = self.valuesB[i+1]
                painter.setPen(colorB)
                painter.drawLine(mx*xPt1+bx, my*yPt1+by, mx*xPt2+bx, my*yPt2+by)
            
            if showC:
                yPt1 = self.valuesC[i]
                yPt2 = self.valuesC[i+1]
                painter.setPen(colorC)
                painter.drawLine(mx*xPt1+bx, my*yPt1+by, mx*xPt2+bx, my*yPt2+by)
                
            if showD:
                yPt1 = self.valuesD[i]
                yPt2 = self.valuesD[i+1]
                painter.setPen(colorD)
                painter.drawLine(mx*xPt1+bx, my*yPt1+by, mx*xPt2+bx, my*yPt2+by)
            
#main class that is imported into any other module
class timePlot(QtWidgets.QWidget):
    #initializations
    valuesA = []
    valuesB = []
    valuesC = []
    valuesD = []
    times = []
    display = [True, True, True, True]
    enables = [True, True, True, True]
    plotColors = ['red', 'blue', 'green', 'yellow']
    
    x = 0
        
    def setupPlot(self, numPlots, plotTitle, verticalName, plotNames):
        #establish the grid layout
        grid = QGridLayout()
        grid.setSpacing(0)
        
        #add an empty filler spot in the bottom left
        self._FillBottomLeft = _Filler()
        grid.addWidget(self._FillBottomLeft, 11, 1, 1, 1)
        
        #add an empty filler spot on the left, over which the plot enables will be placed
        self._FillLeft = _Filler()
        grid.addWidget(self._FillLeft, 0, 0, 12, 2)
        
        #add an empty filler spot on the far right which gives space for the canvas plot
        self._FillRight = _Filler()
        grid.addWidget(self._FillRight, 0, 10, 12, 10)
        
        #add a title bar across the entire plot
        self._title = _Title()
        self._title.plotTitle = plotTitle
        grid.addWidget(self._title, 0, 1, 1, 12)
        
        #add a horizontal axis, which marks the time passed
        self._HAxes = _HorizontalAxes()
        grid.addWidget(self._HAxes, 11, 2, 1, 11)
        
        #add a vertical axis, which marks the values of the plot
        self._VAxes = _VerticalAxes()
        self._VAxes.axisLabel = verticalName
        grid.addWidget(self._VAxes, 1, 1, 10, 1)
        
        #add a canvas area, which shows the time progression of the values
        self._canvas = _Canvas()
        grid.addWidget(self._canvas, 1, 2, 10, 11)
        
        #define a title font
        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(12)
        
        editBoxWidth = 100
        
        #add a checkbox for the first plot
        self._plotCheckA = QCheckBox(plotNames[0])
        self._plotCheckA.setChecked(True)
        self._plotCheckA.setStyleSheet('color: ' + self.plotColors[0] + ';')
        self._plotCheckA.setFont(titleFont)
        self._plotCheckA.stateChanged.connect(lambda: self.toggleStatus(self._plotCheckA.isChecked(), 0))
        grid.addWidget(self._plotCheckA, 1, 0, 1, 1)
        
        #add a line edit for the first plot
        self._plotValueA = QLineEdit()
        self._plotValueA.setFixedWidth(editBoxWidth)
        self._plotValueA.setAlignment(QtCore.Qt.AlignCenter)
        self._plotValueA.setReadOnly(True)
        self._plotValueA.setStyleSheet('color: ' + self.plotColors[0] + ';')
        self._plotValueA.setFont(titleFont)
        grid.addWidget(self._plotValueA, 2, 0, 1, 1)
        
        if numPlots > 1:
            #add a checkbox for the second plot
            self._plotCheckB = QCheckBox(plotNames[1])
            self._plotCheckB.setStyleSheet('color: ' + self.plotColors[1] + ';')
            self._plotCheckB.setFont(titleFont)
            self._plotCheckB.setChecked(True)
            self._plotCheckB.stateChanged.connect(lambda: self.toggleStatus(self._plotCheckB.isChecked(), 1))
            grid.addWidget(self._plotCheckB, 4, 0, 1, 1)
            
            #add a line edit for the second plot
            self._plotValueB = QLineEdit()
            self._plotValueB.setFixedWidth(editBoxWidth)
            self._plotValueB.setAlignment(QtCore.Qt.AlignCenter)
            self._plotValueB.setReadOnly(True)
            self._plotValueB.setStyleSheet('color: ' + self.plotColors[1] + ';')
            self._plotValueB.setFont(titleFont)
            grid.addWidget(self._plotValueB, 5, 0, 1, 1)
        else:
            self.enables[1] = False
            self.display[1] = False
        
        if numPlots > 2:
            #add a checkbox for the third plot
            self._plotCheckC = QCheckBox(plotNames[2])
            self._plotCheckC.setStyleSheet('color: ' + self.plotColors[2] + ';')
            self._plotCheckC.setFont(titleFont)
            self._plotCheckC.setChecked(True)
            self._plotCheckC.stateChanged.connect(lambda: self.toggleStatus(self._plotCheckC.isChecked(), 2))
            grid.addWidget(self._plotCheckC, 7, 0, 1, 1)
            
            #add a line edit for the third plot
            self._plotValueC = QLineEdit()
            self._plotValueC.setFixedWidth(editBoxWidth)
            self._plotValueC.setAlignment(QtCore.Qt.AlignCenter)
            self._plotValueC.setReadOnly(True)
            self._plotValueC.setStyleSheet('color: ' + self.plotColors[2] + ';')
            self._plotValueC.setFont(titleFont)
            grid.addWidget(self._plotValueC, 8, 0, 1, 1)
        else:
            self.enables[2] = False
            self.display[2] = False
        
        if numPlots > 3:
            #add a checkbox for the fourth plot
            self._plotCheckD = QCheckBox(plotNames[3])
            self._plotCheckD.setStyleSheet('color: ' + self.plotColors[3] + ';')
            self._plotCheckD.setFont(titleFont)
            self._plotCheckD.setChecked(True)
            self._plotCheckD.stateChanged.connect(lambda: self.toggleStatus(self._plotCheckD.isChecked(), 3))
            grid.addWidget(self._plotCheckD, 10, 0, 1, 1)
            
            #add a line edit for the fourth plot
            self._plotValueD = QLineEdit()
            self._plotValueD.setFixedWidth(editBoxWidth)
            self._plotValueD.setAlignment(QtCore.Qt.AlignCenter)
            self._plotValueD.setReadOnly(True)
            self._plotValueD.setStyleSheet('color: ' + self.plotColors[3] + ';')
            self._plotValueD.setFont(titleFont)
            grid.addWidget(self._plotValueD, 11, 0, 1, 1)
        else:
            self.enables[3] = False
            self.display[3] = False
        
        self.setLayout(grid)
        self.show()
        
    #toggles the status of the checkbox that was clicked, from off to on (or on to off)
    def toggleStatus(self, status, plot):
        #"status" is a boolean, "plot" is a number 0-3
        self.display[plot] = status
        
    def addPoints(self, valueList):
        #add new points
        index = 0
        #fire through the inputted list, and update the plot and current value indicator
        for value in valueList:
            if index == 0:
                self.valuesA.append(value)
                self._plotValueA.setText(str(round(value,2)))
            elif index == 1:
                self.valuesB.append(value)
                self._plotValueB.setText(str(round(value,2)))
            elif index == 2:
                self.valuesC.append(value)
                self._plotValueC.setText(str(round(value,2)))
            elif index == 3:
                self.valuesD.append(value)
                self._plotValueD.setText(str(round(value,2)))
            index = index + 1
        
        #update the time
        self.currentTime = datetime.datetime.now()
        self.times.append(self.currentTime)
        
        #flag any old points for removal
        removes = []
        index = 0
        for t in self.times:
            diff = (self.currentTime - t).total_seconds()
            if diff > 60:
                removes.append(index)
            index = index + 1
        
        #sort list in reverse to remove points properly
        removes.sort(reverse=True)
        
        #remove any old points
        for i in removes:
            if len(self.valuesA) > 0:
                del self.valuesA[i]
                
            if len(self.valuesB) > 0:
                del self.valuesB[i]
                
            if len(self.valuesC) > 0:
                del self.valuesC[i]
                
            if len(self.valuesD) > 0:
                del self.valuesD[i]
                
            del self.times[i]
        
        #determine maximum and minimum values of the lists that are displayed
        maxMinList = []
        if self.display[0] == True:
            maxMinList.extend(self.valuesA)
        if self.display[1] == True:
            maxMinList.extend(self.valuesB)
        if self.display[2] == True:
            maxMinList.extend(self.valuesC)
        if self.display[3] == True:
            maxMinList.extend(self.valuesD)
        
        #if list is not empty, do things
        if maxMinList:
            maxVal = max(maxMinList)
            minVal = min(maxMinList)
            
            if maxVal == minVal:
                maxVal = maxVal + 1
                minVal = minVal - 1
            
            self._VAxes.vertAxisMax = math.ceil(maxVal)
            self._VAxes.vertAxisMin = math.floor(minVal)
            self._VAxes.update()
        
        #trigger a graph refresh
        self.drawGraph()
        
    #handles the math before calling self.update(), which calls paintEvent()
    def drawGraph(self):
        self.deltaTimes = []
        for t in self.times:
            self.deltaTimes.append((self.currentTime - t).total_seconds())
            
        self._canvas.valuesA = self.valuesA
        self._canvas.valuesB = self.valuesB
        self._canvas.valuesC = self.valuesC
        self._canvas.valuesD = self.valuesD
        self._canvas.times = self.deltaTimes
        
        self._canvas.update()

def main():
    plot = timePlot()
    return plot
    
if __name__ == '__main__':
    main()

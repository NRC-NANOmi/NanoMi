'''

NANOmi Electron Microscope Data Sets Module

This code handles the saving and loading of all values the microscope has to offer.

Initial Code:       Ricky Au
                    Adam Czarnecki
                    Darren Homeniuk, P.Eng.
Initial Date:       May 27, 2020
*****************************************************************************************************************
Version:            3.0 - September 18, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Modified the entire setup so it's a first draft of a functioning system.
                    -Load tab used to load previous saves into the microscope.
                        -Selecting a save will display all of the values that would be loaded, and on loading the values will be pushed to the interface's appropriate edit boxes, and then to the hardware
                    -Save tab used to create new data sets
                        -Changing to this tab will load the microscope's current status so you can see what you would be saving.
                        -Enter a save name, and press save to record the data in the dataSets.xml file; if the save name already exists, the UI will prompt about overwriting
*****************************************************************************************************************
Version:            2.0 - Aug 21, 2020
By:                 Ricky Au
Notes:              Added naming system that doesn't allow for duplicate names on saving.
                    Added loading tab that displays all possible load paths and allows the user to type load file   
                    to check if possible load file.

Current issues:     Data set file can't access other files in AddOnModules since main file is in NANOmi.py
                    Load tab can only check load files in NANOmi.py directory
                    Testing of reading from other files required camera module to be in same directory as NANOmi.py
*****************************************************************************************************************
Version:            1.0 - May 27, 2020
By:                 Darren Homeniuk, P.Eng.
Notes:              Set up the initial module for creating the user interface.
*****************************************************************************************************************
'''

import sys                              #import sys module for system-level functions
import glob, os                         # allow us to access other files
#import the necessary aspects of PyQt5 for this user interface window
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QListWidget, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets

import datetime
import importlib
import xml.etree.ElementTree as ET
from xml.dom import minidom

buttonName = 'Data Sets'                #name of the button on the main window that links to this code
windowHandle = None                     #a handle to the window on a global scope

#this class handles the main window interactions, mainly initialization
class popWindow(QWidget):

#****************************************************************************************************************
#BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
#****************************************************************************************************************

    #a function that users can modify to create their user interface
    def initUI(self):
        QWidget.__init__(self)
        #set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 800
        windowHeight = 800
        self.setGeometry(350, 50, windowWidth, windowHeight)
        
        #define a font for the title of the UI
        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(12)
        
        #define a font for the buttons of the UI
        buttonFont = QtGui.QFont()
        buttonFont.setBold(False)
        buttonFont.setPointSize(10)
        
        #name the window
        self.setWindowTitle('Save/Load Data Sets')
        
        mainGrid = QGridLayout()
        self.setLayout(mainGrid)
        
        #create a label at the top of the window so we know what the window does
        topTextLabel = QLabel('Saving and Loading of Data Sets', self)
        topTextLabel.setAlignment(QtCore.Qt.AlignCenter)
        topTextLabel.setFixedWidth(windowWidth-10)
        topTextLabel.setWordWrap(True)
        topTextLabel.setFont(titleFont)
        mainGrid.addWidget(topTextLabel, 0, 0)
        
        #define a tab control with two tabs - Load & Save - underneath the top text
        tabs = QTabWidget()
        saveTab = QWidget()
        loadTab = QWidget()
        tabs.addTab(loadTab, 'Load Data Sets')
        tabs.addTab(saveTab, 'Save Data Sets')
        tabs.currentChanged.connect(lambda: self.refreshDataSets())
        
        #import all other UI modules
        global modules
        modules = []
        modulePath = os.getcwd() + '/AddOnModules/'
        
        #if the AddOnModules directory exists, carry on
        if os.path.isdir(modulePath):
            
            #pull out the files in the directory AddOnModules, sort them alphabetically (this is why microscope module names start with "UI_x_" where 'x' is any letter A-Z. The letter given will define where the button shows up on the main screen)
            addOnFiles = os.listdir(modulePath)
            addOnFiles.sort()
            
            #for each file in the AddOnModules directory, see if it is a proper microscope module
            for filename in addOnFiles:
                #continue if the name is a file, and not if it is a directory
                if os.path.isfile(modulePath + filename):
                    #handle case of special files like __init__ that shouldn't be loaded
                    if (not filename[0] == '_') and (filename[-3:] == '.py'):
                        
                        #remove the extension from the filename
                        module_name = filename[:-3]
                        #don't load yourself, the data sets module; otherwise load everything UI related
                        if module_name in __name__:
                            continue
                        #also don't load the hardware module, as there is no settings there to save
                        if 'hardware' in module_name.lower():
                            continue
                        #don't load camera module, same reason as hardware
                        if 'camera' in module_name.lower():
                            continue
                        #attempt to read in the module
                        try:
                            modules.append(importlib.import_module('.'+module_name, package='AddOnModules'))
                        except ImportError as err:
                            print('Error:',err)
        
        
        #load tab
        
        # set up grid layout for load tab
        loadGrid = QGridLayout()
        loadGrid.setSpacing(10)
        
        #label for data sets that can be loaded
        loadLabel = QLabel("Loadable Data Sets:")
        loadLabel.setFont(titleFont)
        loadGrid.addWidget(loadLabel, 0, 0, 1, 1)
        
        dataSets = self.readDataFile()
        
        #list view to display all of the sets that can be loaded
        global dataSetDisplay
        dataSetDisplay = QListWidget()
        
        #fire through each data set and plunk the name into the set display list
        for child in dataSets:
            dataSetDisplay.addItem(''.join(child.attrib.values()))
        
        #add the set display to the grid
        loadGrid.addWidget(dataSetDisplay, 1, 0, 3, 1)
        
        #set up the data value list - this shows the individual values inside of each data set selected
        #will update when you click on one of the sets with all of the data inside of it
        dataValueDisplay = QTableWidget()
        dataValueDisplay.setColumnCount(4)
        dataValueDisplay.setHorizontalHeaderItem(0, QTableWidgetItem('Microscope Module:'))
        dataValueDisplay.setHorizontalHeaderItem(1, QTableWidgetItem('Setting Name:'))
        dataValueDisplay.setHorizontalHeaderItem(2, QTableWidgetItem('Value:'))
        dataValueDisplay.setHorizontalHeaderItem(3, QTableWidgetItem('Load Button'))
        dataValueDisplay.setRowCount(0)
        dataValueDisplay.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        dataValueDisplay.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        dataValueDisplay.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        dataValueDisplay.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        
        #add the data value list to the grid
        loadGrid.addWidget(dataValueDisplay, 4, 0, 1, 1)
        
        #set up a linkage so when the data set list changes it's selection, it automatically updates the data value list
        dataSetDisplay.itemSelectionChanged.connect(lambda: self.showDataValues(dataSetDisplay.currentRow(), dataValueDisplay))
        
        #once loaded, force the current selection of the set to the first one - this will also update the data value list
        dataSetDisplay.setCurrentRow(0)
        
        #create a pushbutton to load the selected data set to the microscope's hardware AND software
        loadBtn = QPushButton('Load Selected Data Set')
        loadBtn.setFont(titleFont)
        loadBtn.clicked.connect(lambda: self.loadDataValues(dataSetDisplay.currentRow()))
        loadGrid.addWidget(loadBtn, 5, 0, 3, 1)

        delBtb = QPushButton('Delete Selected Data Set')
        delBtb.setFont(titleFont)
        delBtb.clicked.connect(lambda: self.deleteData(dataSetDisplay.currentRow()))
        loadGrid.addWidget(delBtb, 8,0,3,1)
        
        #set the layout to the actual tab, only once it's complete
        loadTab.setLayout(loadGrid)


        #save tab

        #set up a grid layout inside the save tab
        saveGrid = QGridLayout()
        saveGrid.setSpacing(10)
        
        #add a label
        label = QLabel('Save file name:')
        label.setFont(titleFont)
        saveGrid.addWidget(label, 0, 0, 1, 1)
        
        #add an edit box to the right of the label
        self.edit = QLineEdit()
        self.edit.setText(datetime.datetime.now().strftime('%Y-%m-%d_%H%M'))
        saveGrid.addWidget(self.edit, 0, 1, 1, 1)
        
        #label for the current values table
        tableLabel = QLabel('Current microscope state:')
        tableLabel.setFont(titleFont)
        saveGrid.addWidget(tableLabel, 1, 0, 3, 1)
        
        #set up the data value list - this shows the current status of the microscope that would be saved to file.
        global currentValues
        currentValues = QTableWidget()
        currentValues.setColumnCount(3)
        currentValues.setHorizontalHeaderItem(0, QTableWidgetItem('Microscope Module:'))
        currentValues.setHorizontalHeaderItem(1, QTableWidgetItem('Setting Name:'))
        currentValues.setHorizontalHeaderItem(2, QTableWidgetItem('Value:'))
        currentValues.setRowCount(0)
        currentValues.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        currentValues.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        currentValues.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        #add it to the grid
        saveGrid.addWidget(currentValues, 4, 0, 1, 2)
        
        #add a sample button to the first save tab
        pb = QPushButton('Save to file')
        pb.setFont(titleFont)
        pb.clicked.connect(self.saveButton)
        #function inputs: object, row, column, rowspan, columnspan
        saveGrid.addWidget(pb, 5, 0, 3, 2)
        
        #set the layout to the actual tab, only once it's complete
        saveTab.setLayout(saveGrid)
        
        
        
        #actually add the main overall grid to the popup window
        mainGrid.addWidget(tabs, 1, 0)
        self.setLayout(mainGrid)
        
    #this function will initially set up the load tab, and can be called later as a refresh
    def readDataFile(self):
        #check to see if the user data set file is present
        cwd = os.getcwd() + '/AddOnModules/SaveFiles'  # Get the current working directory (cwd)
        files = os.listdir(cwd)  # Get all the files in that directory
        if not 'DataSets.xml' in files:
            print('Could not find user data file for data file sets.')
            return
        
        #pull out the xml structure from the user data sets file
        tree = ET.parse(cwd + '/DataSets.xml')
        
        #get the root xml structure
        dataSets = tree.getroot()
        
        return dataSets
        
    #this function will refresh the load and save tabs
    def refreshDataSets(self):
        global dataSets
        dataSets = self.readDataFile()
        
        #update the list of possible sets to load in case they've changed since startup
        global dataSetDisplay
        dataSetDisplay.clear()
        for child in dataSets:
            dataSetDisplay.addItem(''.join(child.attrib.values()))
        
        #update the current microscope status so users can see what they would be saving
        global currentValues, modules
        currentValues.setRowCount(0)
        row = 0
        #sift through all modules, entering the variables in the 'data' structure in each module
        for subMod in modules:
            #pull a dictionary holding all name-value pairs for this module
            varDictionary = subMod.windowHandle.getValues()
            for varName in varDictionary:
                # if the value isn't 0 or empty, then load it
                if varDictionary[varName] != '0' and varDictionary[varName] != '':
                    #find the sub-module name in short human-readable form
                    subModName = ' '.join(subMod.__name__.split('_')[2:])
                    #find the value of the variable
                    varVal = varDictionary[varName]

                    #insert a new row in the table
                    currentValues.insertRow(row)

                    #set up the module, name and value cells
                    module = QTableWidgetItem(subModName)
                    module.setFlags(QtCore.Qt.ItemIsEnabled)
                    name = QTableWidgetItem(varName)
                    name.setFlags(QtCore.Qt.ItemIsEnabled)
                    value = QTableWidgetItem(varVal)
                    value.setFlags(QtCore.Qt.ItemIsEnabled)

                    #actually set the module, name and value cells into the table
                    currentValues.setItem(row, 0, module)
                    currentValues.setItem(row, 1, name)
                    currentValues.setItem(row, 2, value)
                    row = row + 1
                    
    #this function will update the data value display with a selected data set's values so users can see what they will be setting
    def showDataValues(self, index, display):
        #reset the row count to 0 to refresh all data in the data value display
        global dataSets
        dataSets = self.readDataFile()
        data = dataSets[index]
        display.setRowCount(0)
        row = 0
        #for each attribute in the data set, show it's name and value in the data value display
        for child in data:
            
            #pull out the actual attributes from the data child
            attributes = child.attrib
            
            #insert a new row in the table
            display.insertRow(row)
            
            #set up the module, name and value cells
            module = QTableWidgetItem(attributes['module'])
            module.setFlags(QtCore.Qt.ItemIsEnabled)
            name = QTableWidgetItem(attributes['name'])
            name.setFlags(QtCore.Qt.ItemIsEnabled)
            value = QTableWidgetItem(attributes['value'])
            value.setFlags(QtCore.Qt.ItemIsEnabled)
            button = QPushButton("Load")
            button.clicked.connect(lambda: self.loadSingleSetting(index, display.currentRow()))
            #actually set the module, name and value cells into the table
            display.setItem(row, 0, module)
            display.setItem(row, 1, name)
            display.setItem(row, 2, value)
            display.setCellWidget(row, 3, button)
            row = row + 1
        
    #this function will actually load the data set values to the microscope
    def loadDataValues(self, index):
        global dataSets
        dataSets = self.readDataFile()
        data = dataSets[index]
        #pull in all imported UI modules
        global modules
        
        fails = 0
        
        print('Starting to load data set "' + data.attrib['name'] + '".')
        
        #sift through all modules one at a time, loading all data to each one
        for subModule in modules:
            #sift through all values to be loaded in "data", send the ones for the chosen module
            for child in data:
                #pull out this piece of data's attributes
                attributes = child.attrib
                #if the module is a match for the subModule, load the data to it - module name matches don't have to be exact, because real module names can be super long and I don't want users to have to deal with that kinda stuff if they don't have to
                if attributes['module'] == (' '.join(subModule.__name__.split('_')[2:])):
                    modName = attributes['module']
                    name = attributes['name']
                    value = attributes['value']
                    returnValue = subModule.windowHandle.setValue(name, value)
                    if returnValue != 0:
                        fails = fails + 1
                        print('Failed loading variable ' + name + ' from module ' + modName + '.')
                    else:
                        print('Changed variable ' + name + ' in the ' + modName + ' module changed to a value of ' + value + '.')
        #if no failures during the load, send the 'all clear' message
        if fails == 0:
            print('Loading of data set "' + data.attrib['name'] + '" is complete.')
            QMessageBox.question(self,'Loading complete', 'Loading of data set "' + data.attrib['name'] + '" is complete.', QMessageBox.Ok, QMessageBox.Ok)
        #if there were failures, list them out so the user can know what wasn't loaded properly.
        else:
            print('Loading of data set "' + data.attrib['name'] + '" is done, though ' + str(fails) + ' variables could not be loaded.')
            QMessageBox.question(self,'Loading errors', 'Loading of data set "' + data.attrib['name'] + '" is done, though ' + str(fails) + ' variables could not be loaded.', QMessageBox.Ok, QMessageBox.Ok)
        
        #add a newline character to differentiate all of the text lines apart.
        print('\n')
        
    #function to save the microscope current state in the xml user data file
    def saveButton(self):
        #import the links to other modules
        global modules
        
        #variable to flag if the entered name exists in the file structure already
        sameName = False
        copy = None
        
        #pull the tree from the file
        tree = self.readDataFile()
        print(tree)
        #pull the entered new filename
        setName = self.edit.text()
        
        #compare the entered name vs all other saved names
        for otherSaves in tree:
            if ''.join(otherSaves.attrib.values()) == setName:
                sameName = True
                copy = otherSaves
                break
        
        #if the name has been entered before ask the user if they want to overwrite the data
        if sameName == True:
            print(setName + ' already exists.')
            reply = QMessageBox.question(self,'Specified set name exists', setName + ' already exists. Overwrite?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            #if not overwriting, end the process
            if reply == QMessageBox.No:
                print('Saving cancelled.')
                QMessageBox.question(self,'Cancelled save.','Saving has been cancelled.', QMessageBox.Ok, QMessageBox.Ok)
            #if overwriting, modify the variables
            else:
                print('Overwriting the save entry "' + setName + '".')
                tree.remove(copy)
                
        #if the setName is unique, or overwriting is permitted and the original is gone, go ahead and tack it on
        #add a new element under "dataSets" root in parallel with the other "set" children
        newStruct = ET.SubElement(tree, 'set')
        #modify the name to be the chosen name
        newStruct.set('name', setName)
        #sift through all modules, entering the variables in the 'data' structure in each module
        for subMod in modules:
            print(subMod.__name__)
            #pull a dictionary holding all name-value pairs for this module
            varDictionary = subMod.windowHandle.getValues()
            for varName in varDictionary:
                #find the sub-module name in short human-readable form
                subModName = ' '.join(subMod.__name__.split('_')[2:])
                #find the value of the variable
                varVal = varDictionary[varName]
                #add all new required save variables one at a time
                #check if variable value is 0
                if varVal != '0' and varVal != '':
                    ET.SubElement(newStruct, 'setting', {'module':subModName, 'name':varName, 'value':varVal})
        
        #format the entire xml file nicely so it is human readable and indented - encode it to a byte-string
        xmlString = ET.tostring(tree, 'utf-8', method='xml')
        #now decode it to an actual string
        xmlString = xmlString.decode()
        #remove all newlines because new additions don't have newlines
        xmlString = xmlString.replace('\n','')
        #remove all double-spaces (aka portions of tabs) because new additions don't have spaces
        xmlString = xmlString.replace('  ','')
        #use minidom (instead of elementTree) to parse in the string back into xml
        domTree = minidom.parseString(xmlString)
        #write to file
        with open(os.getcwd() + '/AddOnModules/SaveFiles/DataSets.xml', 'w') as pid:
            domTree.writexml(pid, encoding='utf-8', indent='', addindent='    ', nepasswl='\n')


    # function that used to delete a dataset from xml
    def deleteData(self, index):
        tree = self.readDataFile()
        #remove the data that want to be deleted from dataSets
        tree.remove(tree[index])
        #format the entire xml file nicely so it is human readable and indented - encode it to a byte-string
        xmlString = ET.tostring(tree, 'utf-8', method='xml')
        #now decode it to an actual string
        xmlString = xmlString.decode()
        #remove all newlines because new additions don't have newlines
        xmlString = xmlString.replace('\n','')
        #remove all double-spaces (aka portions of tabs) because new additions don't have spaces
        xmlString = xmlString.replace('  ','')
        #use minidom (instead of elementTree) to parse in the string back into xml
        domTree = minidom.parseString(xmlString)
        #write to file
        with open(os.getcwd() + '/AddOnModules/SaveFiles/DataSets.xml', 'w') as pid:
            domTree.writexml(pid, encoding='utf-8', indent='', addindent='    ', newl='\n')
        self.refreshDataSets()

    def loadSingleSetting(self, treeIndex, settingIndex):
        print("indexes are", treeIndex, "and", settingIndex)
        global dataSets
        dataSets = self.readDataFile()
        data = dataSets[treeIndex][settingIndex]
        global modules

        attributes = data.attrib
        modName = attributes['module']
        name = attributes['name']
        value = attributes['value']

        print("Started to loading", name, "to", modName)
        #sift through all modules one at a time, loading all data to each one
        for subModule in modules:
                #pull out this piece of data's attributes
            #if the module is a match for the subModule, load the data to it - module name matches don't have to be exact, because real module names can be super long and I don't want users to have to deal with that kinda stuff if they don't have to
            if modName ==  (' '.join(subModule.__name__.split('_')[2:])):
                returnValue = subModule.windowHandle.setValue(name, value)
                if returnValue != 0:
                    fails = fails + 1
                    print('Failed loading variable ' + name + ' from module ' + modName + '.')
                else:
                    print('Changed variable ' + name + ' in the ' + modName + ' module changed to a value of ' + value + '.')


#****************************************************************************************************************
#BREAK - DO NOT MODIFY CODE BELOW HERE OR MAIN WINDOW'S EXECUTION MAY CRASH
#****************************************************************************************************************
    #function to handle initialization - mainly calls a subfunction to create the user interface
    def __init__(self):
        super().__init__()
        self.initUI()
        
    #this function handles the closing of the pop-up window - it doesn't actually close, simply hides visibility. 
    #this functionality allows for permanance of objects in the background
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        
    #this function is called on main window shutdown, and it forces the popup to close
    def shutdown():
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

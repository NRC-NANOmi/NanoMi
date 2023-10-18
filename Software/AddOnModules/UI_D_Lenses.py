import os
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtCore import *
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg 
from AddOnModules.OpticalModules.engine.lens import Lens
from AddOnModules.OpticalModules.engine.optimization import optimize_focal_length
from AddOnModules import Hardware, UI_U_DataSets
import sys
import sympy as sp
import xml.etree.ElementTree as ET

LAMBDA_ELECTRON = 0.0112e-6

# LENS_BORE = 25.4*0.1/2

# # diameter of condensor aperature
# CA_DIAMETER = 0.01

# # stores info for the anode
# ANODE = [39.1, 31.75, 31.75, 1.5, [0.5, 0, 0.3], 'Anode', 25.4*0.1/2]

# # stores info for the sample
# # SAMPLE = [528.9, 1.5, -1, [1, 0.7, 0], 'Sample']
# SAMPLE = [528.9, 11.6, 52.2, 1.5 , [1, 0.7, 0], 'Sample']

# # stores info for the scintillator
# # SCINTILLATOR = [972.7, 1.5, 1, [0.3, 0.75, 0.75], 'Scintillator']
# SCINTILLATOR = [972.7, 52.2, 11.6, 1.5, [0.3, 0.75, 0.75], 'Scintillator', 25.4*0.1/2]

# # stores info for the condensor aperature
# # CONDENSOR_APERATURE = [192.4, 1.5, 1, [0, 0, 0], 'Cond. Apert']
# CONDENSOR_APERATURE = [192.4, 52.2, 11.6, 1.5, [0, 0, 0], 'Cond. Apert']

# # add color of each ray in same order as rays
# # red, green, blue, gold
RAY_COLORS = [[1.0, 0, 0], [0.0, 1.0, 0], [0.0, 0.2, 1.0], [0.7, 0.4, 0]]

# # pin condenser aperture angle limited as per location and diameter
# RAYS = [
#     np.array(
#         [[1.5e-2], [(CA_DIAMETER/2 - 1.5e-2) / CONDENSOR_APERATURE[0]]]
#     ),
#     # 2nd ray, at r = 0, angle limited by CA
#     np.array(
#         [[0], [(CA_DIAMETER/2) / CONDENSOR_APERATURE[0]]]
#     ),
#     # 3rd ray, at r = tip edge, parallel to opt. axis
#     np.array(
#         [[1.5e-2], [0]]
#     ),
#     # 4th ray, at -rG, angle up to +CA edge CRAZY BEAM
#     np.array(
#         [[-1*1.5e-2], [(CA_DIAMETER/2 + 1.5e-2) / CONDENSOR_APERATURE[0]]]
#     )
# ]


# stores info for the lower lenses
# LOWER_LENSES = [
#     [551.6, 1.5, -1, [0.3, 0.75, 0.75], 'Objective'],
#     [706.4, 1.5, 1, [0.3, 0.75, 0.75], 'Intermediate'],
#     [826.9, 1.5, 1, [0.3, 0.75, 0.75], 'Projective']
# ]
# LOWER_LENSES = [
#     [551.6, 11.6, 52.2, 1.5, [0.3, 0.75, 0.75], 'Objective', 25.4*0.1/2],
#     [706.4, 52.2, 11.6, 1.5, [0.3, 0.75, 0.75], 'Intermediate', 25.4*0.1/2],
#     [826.9, 52.2, 11.6, 1.5, [0.3, 0.75, 0.75], 'Projective', 25.4*0.1/2]
# ]
# stores info for the upper lenses
# UPPER_LENSES = [
#     [257.03, 63.5, 1.5, [0.3, 0.9, 0.65], 'C1'],
#     [349, 1.5, 1, [0.3, 0.75, 0.75], 'C2'],
#     [517, 1.5, 1, [0.3, 0.75, 0.75], 'C3']
# ]
# UPPER_LENSES = [
#     [257.03, 31.75, 31.75, 1.5, [0.3, 0.9, 0.65], 'C1', 25.4*0.1/2],
#     [349, 52.2, 11.6, 1.5, [0.3, 0.75, 0.75], 'C2', 25.4*0.1/2],
#     [517, 52.2, 11.6, 1.5, [0.3, 0.75, 0.75], 'C3', 25.4*0.1/2]
# ]
buttonName = 'Lens'
windowHandle = None  # a handle to the window on a global scope
class popWindow(QWidget):

    # ****************************************************************************************************************
    # BELOW HERE AND BEFORE NEXT BREAK IS MODIFYABLE CODE - SET UP USER INTERFACE HERE
    # ****************************************************************************************************************

    # a function that users can modify to create their user interface
    def initUI(self):
        QWidget.__init__(self)
        # set width of main window (X, Y , WIDTH, HEIGHT)
        windowWidth = 1000
        windowHeight = 900
        self.setGeometry(350, 50, windowWidth, windowHeight)

        # name the window
        self.setWindowTitle('Lens')
        self.mainGrid = QGridLayout()
        self.setLayout(self.mainGrid)
    # ****************************************************************************************************************
    # Controls Block
    # ****************************************************************************************************************
        self.groupBoxs = []
        self.upperGroupBox = QGroupBox("Upper Lenses")
        self.upperLenLayout = QVBoxLayout()
        self.upperGroupBox.setLayout(self.upperLenLayout)
        self.lowerGroupBox = QGroupBox("Lower Lenses")
        self.lowerLenLayout = QVBoxLayout()
        self.lowerGroupBox.setLayout(self.lowerLenLayout)
        self.anodeVoltageLabel = QLabel("Anode Voltage (U0):")
        self.anodeVoltageSpinbox = QDoubleSpinBox()
        self.anodeVoltageSpinbox.setMinimum(1)
        self.anodeVoltageSpinbox.setSingleStep(1)
        self.anodeVoltageSpinbox.valueChanged.connect(self.updateAnodeVoltage)
        self.mainGrid.addWidget(self.anodeVoltageLabel,1,0)
        self.mainGrid.addWidget(self.anodeVoltageSpinbox,1,1)
        self.mainGrid.addWidget(self.upperGroupBox,2,0,1,10)
        self.mainGrid.addWidget(self.lowerGroupBox,2,10,1,10)
        self.boxLayouts = []

        self.voltageSpinBoxs = []
        self.excitationSpinBoxs = []
        self.focalLengthSpinBoxs = []

        self.voltageIncrements = []
        self.excitationIncrements= []
        self.focalLengthIncrements= []

        self.readDataFile()

    # ****************************************************************************************************************
    # Figure block
    # ****************************************************************************************************************
 
        # create figure
        self.figure = Figure(figsize=(10, 10))
        self.axis = self.figure.add_subplot()
        self.axis.text(
            275, -2.1, 'X [mm]', color=[0, 0, 0], fontsize=6
        )
        self.axis.set_ylabel(
            'Z [mm]', color=[0, 0, 0], fontsize=6
        )

        # put the figure in a widget on the tk window
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.mainGrid.addWidget(self.canvas,0,0,1,20)
        self.redraw()

        self.x_min, self. x_max, self.y_min, self.y_max = 0, 0, 0, 0

        # list for active lenses
        self.active_ll = [True, True, True]

        # sample rays variables and initialization for lower lenses
        self.distance_from_optical = 0.00001
        self.scattering_angle = 0
        self.last_mag = 0
        self.sample_rays = []
        self.update_l_rays()

        # draws anode
        # self.symmetrical_box(*ANODE)
        self.len_box(*self.ANODE)
        # draws sample
        # self.sample_aperature_box(*SAMPLE)
        self.len_box(*self.SAMPLE)

        # draws condensor aperature
        # self.sample_aperature_box(*CONDENSOR_APERATURE)
        self.len_box(*self.CONDENSOR_APERATURE)

        # draws scintillator
        # self.asymmetrical_box(*SCINTILLATOR)
        self.len_box(*self.SCINTILLATOR)

        # draw red dashed line on x-axis
        self.axis.axhline(0, 0, 1, color='red', linestyle='--')

        # list of points to plot rays
        self.drawn_rays_c, self.drawn_rays_b = [], []

        # list of lenses magnification and plots
        self.mag_lower, self.mag_upper = [], []
        self.mag_u_plot, self.mag_l_plot = [], []

        # crossover points arrays
        self.crossover_points_c, self.crossover_points_b = [], []

        # takes in list of lens info, draws upper lenses
        # and setup magnification plots
        for i, row in enumerate(self.UPPER_LENSES):
            # draw C1 lens
            # if i == 0:
            #     self.symmetrical_box(*row)
            # # draw C2, C3 lens
            # else:
            #     self.asymmetrical_box(*row)
            self.len_box(*row)
            # set up magnification plot
            self.mag_u_plot.append(
                self.axis.text(
                    self.UPPER_LENSES[i][0] + 5,
                    0.5, '', color='k', fontsize=8,
                    rotation='vertical',
                    backgroundcolor=[0.8, 1.0, 1.0]
                )
            )
            # green circle to mark the crossover point of each lens
            self.crossover_points_c.append(self.axis.plot([], 'go')[0])

        # takes in list of lens info, draws lower lenses
        # and set up crossover points
        for i, row in enumerate(self.LOWER_LENSES):
            # draw lens
            # self.asymmetrical_box(*row)
            self.len_box(*row)
            # set up magnification plot
            self.mag_l_plot.append(
                self.axis.text(
                    self.LOWER_LENSES[i][0] + 5,
                    0.5, '', color='k', fontsize=8,
                    rotation='vertical',
                    backgroundcolor=[0.8, 1, 1]
                )
            )
            # green circle to mark the crossover point of each lens
            self.crossover_points_b.append(self.axis.plot([], 'go')[0])

        # set up lines representing the ray path for upper lenses
        for i in range(len(self.RAYS)):
            for j in range(len(self.UPPER_LENSES)):
                self.drawn_rays_c.append(
                    self.axis.plot(
                        [], lw=1, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_c.append(
                    self.axis.plot(
                        [], lw=3, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_c.append(
                    self.axis.plot(
                        [], lw=1, color="r"
                    )[0]
                )

        # set up lines representing the ray path for lower lenses
        for i in range(len(self.sample_rays)):
            for j in range(len(self.LOWER_LENSES)):
                self.drawn_rays_b.append(
                    self.axis.plot(
                        [], lw=1, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_b.append(
                    self.axis.plot(
                        [], lw=3, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_b.append(
                    self.axis.plot(
                        [], lw=1, color="r"
                    )[0]
                )

        # text to display extreme info
        self.extreme_info = self.axis.text(
            300, 1.64, '', color=[0, 0, 0],
            fontsize='large', ha='center'
        )

        # initialize arrays with points info
        self.lines_u, self.lines_l = [], []
        self.display_u_rays()
        self.display_l_rays()
        
        for i in range(len(self.cf_u)):
            self.focalLengthSpinBoxs[i].setValue(self.cf_u[i])
        for i in range(len(self.cf_l)):
            self.focalLengthSpinBoxs[i+self.lowerIndex].setValue(self.cf_l[i])


    def len_box(self, x, l, r, h, colour, name, bore=None):
        """ draws box represents lens in diagram

        Args:
            x (float): box location
            l (float): box left side distance to centre of the mid electeode
            r (float): box right side distance to centre of the mid electeode
            h (float): box height
            colour (list): RGB colors
            name (str): lens name
        """
        # x = location of centre point of box along x-axis
        # w = width, h = height, colour = color

        # rectangle box
        self.axis.add_patch(
            Rectangle(
                (x-l, -h), l+r, h*2, edgecolor=colour,
                facecolor='none', lw=1
            )
        )
        if bore != None:
            # top lens bore (horizontal line)
            self.axis.hlines(bore, x-l, x+r, colors=colour)
            # bottom lens bore (horizontal line)
            self.axis.hlines(-bore, x-l, x+r, colors=colour)
        # electrode location in lens
        self.axis.vlines(x, -h, h, colors=colour, linestyles='--')

        self.axis.text(
            x, -h+0.05, name, fontsize=8,
            rotation='vertical', ha='center'
        )
        return 

    def display_ray_path(self, rays, lenses, l_plot, m_plot, upper):
        """get all ray paths through each lens

        Args:
            rays (list): contains all rays properties
            lenses (list): contains all lens objects
            l_plot (list): lens plots
            m_plot (list): magnification plots
            upper (bool): is it upper lenses
        """
        num_l = len(lenses)
        for i in range(len(rays)):
            for j, lens in enumerate(lenses):
                if j != 0 or upper:
                    lens.update_output_plane_location()
                sl, el, li, mag = lens.ray_path(
                    rays[i] if j == 0 else
                    lenses[j - 1].ray_out_lens
                )
                sl = ([x for x, y in sl], [y for x, y in sl])
                li = ([x for x, y in li], [y for x, y in li])
                el = ([x for x, y in el], [y for x, y in el])

                l_plot.append(
                    self.axis.plot(sl[0], sl[1],  lw=1, color=RAY_COLORS[i])
                )
                l_plot.append(
                    self.axis.plot(li[0], li[1],  lw=2, color=RAY_COLORS[i])
                )
                l_plot.append(
                    self.axis.plot(el[0], el[1],  lw=1, color="k")
                )
                if mag is not None and i == 0:
                    if upper:
                        self.mag_upper.append(mag)
                        m_plot[j].set_text(f"{mag:.2E}x")
                    elif not upper:
                        self.mag_lower.append(mag)
                        m_plot[j].set_text(f"{mag:.2E}x")
                if not upper and i == 1 and j == (num_l - 1):
                    self.last_mag = abs(
                        lens.ray_in_vac[0][0] / self.distance_from_optical
                    )

    def display_u_rays(self):
        """creates upper lenses that will be part of the ray paths"""
        self.mag_upper = []
        upper_lenses_obj = []
        # creates a lens object for all active lenses
        # and set ups crossover points plots
        for index in range(len(self.UPPER_LENSES)):
            upper_lenses_obj.append(
                Lens(
                    self.UPPER_LENSES[index][0],
                    self.cf_u[index],
                    None if index == 0 else
                    upper_lenses_obj[index - 1],
                    3
                )
            )
            self.crossover_points_c[index].set_data(
                upper_lenses_obj[index].crossover_point_location()
            )
            self.crossover_points_c[index].set_visible(True)
        # initialize ray path last lens
        if len(upper_lenses_obj) > 0:
            upper_lenses_obj.append(
                Lens(
                    self.SAMPLE[0],
                    0,
                    upper_lenses_obj[-1],
                    1
                )
            )

        # plot ray path
        self.display_ray_path(
            self.RAYS, upper_lenses_obj, self.lines_u, self.mag_u_plot, True
        )

    def update_u_lenses(self):
        """update upper lenses settings"""
        for line in self.lines_u:
            line.pop(0).remove()
        self.lines_u = []

        self.display_u_rays()
        self.redraw()
        self.canvas.flush_events()

    def update_l_rays(self):
        self.scattering_angle = LAMBDA_ELECTRON / self.distance_from_optical
        self.sample_rays = [
            np.array([[0], [self.scattering_angle]]),
            np.array([[self.distance_from_optical], [self.scattering_angle]]),
            np.array([[self.distance_from_optical], [0]])
        ]

    def display_l_rays(self):
        """creates lower lenses that will be part of the ray paths"""
        self.mag_lower = []
        lower_lenses_obj = []
        sample = Lens(self.SAMPLE[0], None, None, None)
        # creates a lens object for all active lenses
        # and set ups crossover points plots
        for index in range(len(self.LOWER_LENSES)):
            lower_lenses_obj.append(
                Lens(
                    self.LOWER_LENSES[index][0],
                    self.cf_l[index],
                    sample if index == 0 else
                    lower_lenses_obj[index - 1],
                    3
                )
            )
            self.crossover_points_b[index].set_data(
                lower_lenses_obj[index].crossover_point_location()
            )
            self.crossover_points_b[index].set_visible(True)

        # initialize ray path last lens
        if len(lower_lenses_obj):
            lower_lenses_obj.append(
                Lens(
                    self.SCINTILLATOR[0],
                    0,
                    lower_lenses_obj[index],
                    1
                )
            )

        # plot ray path
        self.display_ray_path(
            self.sample_rays, lower_lenses_obj, self.lines_l,
            self.mag_l_plot, False
        )

    def update_l_lenses(self):
        for line in self.lines_l:
            line.pop(0).remove()
        self.lines_l = []

        self.update_l_rays()
        self.display_l_rays()
        self.redraw()
        self.canvas.flush_events()

    def redraw(self):
        """redraw diagram"""
        self.axis.relim()
        self.axis.autoscale_view()
        self.canvas.draw()

    def excitationToFocalLength(self, formula, x):
        expr = sp.sympify(formula)
        result = expr.subs('x', x)
        return round(result, 2)
    
    def focalLengthToExcitation(self, formula, y):
        expr = sp.sympify(formula)
        eq = sp.Eq(expr, y)
        print(eq)
        ans = sp.solve(eq, 'x', n=1, simplify=False, rational=False)
        return round(ans[0], 2)
    
    def readDataFile(self):
        # check to see if the user data set file is present
        # Get the current working directory (cwd)
        cwd = os.getcwd() + '/AddOnModules/SaveFiles'
        tree = ET.parse(cwd + '/LenSettings.xml')

        # get the root xml structure
        self.settings = tree.getroot()
        self.lenSetting = self.settings.find("Lens")
        self.loadLens()
    
    def loadLens(self):
        anode = self.settings.find("Anode")
        self.ANODE = [float(anode.find("location").text), float(anode.find("left").text), float(anode.find("right").text),\
                 float(anode.find("height").text), [float(anode.find("colour").find("r").text), float(anode.find("colour").find("g").text),float(anode.find("colour").find("b").text)],\
                    anode.tag, float(anode.find("lore").text)]
        
        self.anodeVoltage = float(anode.find("voltage").text)
        self.anodeVoltageSpinbox.setValue(self.anodeVoltage)

        condensor_aperature = self.settings.find("Cond.Apert")
        self.CONDENSOR_APERATURE = [float(condensor_aperature.find("location").text), float(condensor_aperature.find("left").text), float(condensor_aperature.find("right").text),\
                 float(condensor_aperature.find("height").text), [float(condensor_aperature.find("colour").find("r").text), float(condensor_aperature.find("colour").find("g").text),float(condensor_aperature.find("colour").find("b").text)],\
                    condensor_aperature.tag, float(condensor_aperature.find("lore").text)]
        CA_DIAMETER = float(condensor_aperature.find("diameter").text)
        sample = self.settings.find("Sample")
        self.SAMPLE = [float(sample.find("location").text), float(sample.find("left").text), float(sample.find("right").text),\
                 float(sample.find("height").text), [float(sample.find("colour").find("r").text), float(sample.find("colour").find("g").text),float(sample.find("colour").find("b").text)],\
                    sample.tag]
        
        scintillator = self.settings.find("Scintillator")
        self.SCINTILLATOR = [float(scintillator.find("location").text), float(scintillator.find("left").text), float(scintillator.find("right").text),\
                 float(scintillator.find("height").text), [float(scintillator.find("colour").find("r").text), float(scintillator.find("colour").find("g").text),float(scintillator.find("colour").find("b").text)],\
                    scintillator.tag, float(scintillator.find("lore").text)]
        tempLen = []
        for i in range(len(self.lenSetting)):
            tempLen.append([float(self.lenSetting[i].find("location").text), float(self.lenSetting[i].find("left").text), float(self.lenSetting[i].find("right").text),\
                 float(self.lenSetting[i].find("height").text), [float(self.lenSetting[i].find("colour").find("r").text), float(self.lenSetting[i].find("colour").find("g").text),float(self.lenSetting[i].find("colour").find("b").text)],\
                    self.lenSetting[i].tag, float(self.lenSetting[i].find("lore").text)])
        tempLen = sorted(list(enumerate(tempLen)), key=lambda x: x[1][0])

        self.lowerIndex = len(tempLen)
        for i in range(len(tempLen)):
            if tempLen[i][1][0] > self.SAMPLE[0]:
                self.lowerIndex = i
                break
        self.UPPER_LENSES = []
        self.LOWER_LENSES = []
        self.cf_u = []
        self.cf_l = []
        self.voltageTrigger = []
        self.excitationTrigger = []
        self.focalLengthTrigger =  []
        self.voltageUpdateFunctions = []
        for i in range(len(tempLen)):
            isUpper = i < self.lowerIndex
            settingIndex = tempLen[i][0]
            if isUpper:
                self.UPPER_LENSES.append(tempLen[i][1])
            else:
                self.LOWER_LENSES.append(tempLen[i][1])
            nameLabel = QLabel(self.lenSetting[settingIndex].tag)
            voltageLabel = QLabel("Voltage: ")
            self.voltageSpinBoxs.append(QDoubleSpinBox())
            v = float(self.lenSetting[i].find("voltage").text)
            self.voltageSpinBoxs[i].setMinimum(0)
            self.voltageSpinBoxs[i].setMaximum(v)
            self.voltageSpinBoxs[i].setSingleStep(0.01)
            self.voltageUpdateFunctions.append(self.lambdaGenerator(self.updateVoltage, settingIndex, isUpper, i))
            self.voltageSpinBoxs[i].valueChanged.connect(self.voltageUpdateFunctions[i])
            self.voltageIncrements.append(QComboBox())
            self.voltageIncrements[i].addItems(
                ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
            self.voltageIncrements[i].setCurrentIndex(0)
            self.voltageIncrements[i].currentIndexChanged.connect(self.lambdaGenerator(self.voltageIncrementChange, i))
            self.voltageTrigger.append(False)

            maxExcitation = v/self.anodeVoltage
            print("max excitation", maxExcitation)
            excitationLabel = QLabel("Excitation: ")
            self.excitationSpinBoxs.append(QDoubleSpinBox())
            self.excitationSpinBoxs[i].setMinimum(0.01)
            self.excitationSpinBoxs[i].setMaximum(maxExcitation)
            self.excitationSpinBoxs[i].setSingleStep(0.01)
            self.excitationSpinBoxs[i].valueChanged.connect(self.lambdaGenerator(self.updateExcitation,settingIndex, isUpper, i))
            self.excitationIncrements.append(QComboBox())
            self.excitationIncrements[i].addItems(
                ['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5'])
            self.excitationIncrements[i].setCurrentIndex(0)
            self.excitationIncrements[i].currentIndexChanged.connect(self.lambdaGenerator(self.excitationIncrementChange, i))
            self.excitationTrigger.append(False)

            formula = self.lenSetting[i].find("formula").text
            minEXFL = self.excitationToFocalLength(formula, 0.01)
            maxEXFL = self.excitationToFocalLength(formula, maxExcitation)
            focalLengthLabel = QLabel("Focal Length: ")
            self.focalLengthSpinBoxs.append(QDoubleSpinBox())
            self.focalLengthSpinBoxs[i].setMinimum(min(minEXFL, maxEXFL))
            self.focalLengthSpinBoxs[i].setMaximum(max(minEXFL, maxEXFL))
            self.focalLengthSpinBoxs[i].setSingleStep(0.2)
            self.focalLengthSpinBoxs[i].valueChanged.connect(self.lambdaGenerator(self.updateFocalLength, settingIndex, isUpper, i))
            self.focalLengthIncrements.append(QComboBox())
            self.focalLengthIncrements[i].addItems(
                ['0.2', '0.5', '1', '2', '5', '10', '15', '20'])
            self.focalLengthIncrements[i].setCurrentIndex(0)
            self.focalLengthIncrements[i].currentIndexChanged.connect(self.lambdaGenerator(self.focalLengthIncrementChange, i))
            self.focalLengthTrigger.append(False)
            self.boxLayouts.append(QHBoxLayout())
            self.boxLayouts[i].addWidget(nameLabel)
            self.boxLayouts[i].addStretch()
            self.boxLayouts[i].addWidget(voltageLabel)
            self.boxLayouts[i].addWidget(self.voltageSpinBoxs[i])
            self.boxLayouts[i].addWidget(self.voltageIncrements[i])
            self.boxLayouts[i].addStretch()
            self.boxLayouts[i].addWidget(excitationLabel)
            self.boxLayouts[i].addWidget(self.excitationSpinBoxs[i])
            self.boxLayouts[i].addWidget(self.excitationIncrements[i])
            self.boxLayouts[i].addStretch()
            self.boxLayouts[i].addWidget(focalLengthLabel) 
            self.boxLayouts[i].addWidget(self.focalLengthSpinBoxs[i])
            self.boxLayouts[i].addWidget(self.focalLengthIncrements[i])
            self.groupBoxs.append(QGroupBox())
            self.groupBoxs[i].setLayout(self.boxLayouts[i])
            default = float(self.lenSetting[settingIndex].find("default").text) 
            if isUpper:
                self.cf_u.append(default)
                self.upperLenLayout.addWidget(self.groupBoxs[i])
            else:
                self.cf_l.append(default)
                self.lowerLenLayout.addWidget(self.groupBoxs[i])
            
        RAY_COLORS = [[1.0, 0, 0], [0.0, 1.0, 0], [0.0, 0.2, 1.0], [0.7, 0.4, 0]]

        # pin condenser aperture angle limited as per location and diameter
        self.RAYS = [
            np.array(
                [[1.5e-2], [(CA_DIAMETER/2 - 1.5e-2) / self.CONDENSOR_APERATURE[0]]]
            ),
            # 2nd ray, at r = 0, angle limited by CA
            np.array(
                [[0], [(CA_DIAMETER/2) / self.CONDENSOR_APERATURE[0]]]
            ),
            # 3rd ray, at r = tip edge, parallel to opt. axis
            np.array(
                [[1.5e-2], [0]]
            ),
            # 4th ray, at -rG, angle up to +CA edge CRAZY BEAM
            np.array(
                [[-1*1.5e-2], [(CA_DIAMETER/2 + 1.5e-2) / self.CONDENSOR_APERATURE[0]]]
            )
        ]
    
    def lambdaGenerator(self, function, *args):
        return lambda: function(*args)


    def updateVoltage(self, settingIndex, isUpper, uiIndex):
        if not self.voltageTrigger[uiIndex]:
            if not (self.excitationTrigger[uiIndex] or self.focalLengthTrigger[uiIndex]):
                self.voltageTrigger[uiIndex] = True
            v = round(self.voltageSpinBoxs[uiIndex].value(),2)
            excitation = round(v/self.anodeVoltage,2)
            self.excitationSpinBoxs[uiIndex].setValue(excitation)
            output = round(5/float(self.lenSetting[settingIndex].find("voltage").text) * v,2)
            Hardware.IO.setAnalog( 
                self.lenSetting[settingIndex].find("pin").text, output)
        else:
            self.voltageTrigger[uiIndex] = False

    def voltageIncrementChange(self, index):
        self.voltageSpinBoxs[index].setSingleStep(
            float(self.voltageIncrements[index].currentText()))
        
    def updateExcitation(self, settingIndex, isUpper, uiIndex):
        if not self.excitationTrigger[uiIndex]:
            if not (self.voltageTrigger[uiIndex] or self.focalLengthTrigger[uiIndex]):
                self.excitationTrigger[uiIndex] = True
            excitation = round(self.excitationSpinBoxs[uiIndex].value(),2)
            formula = self.lenSetting[settingIndex].find("formula").text
            focalLength = round(self.excitationToFocalLength(formula, excitation),2)
            self.focalLengthSpinBoxs[uiIndex].setValue(focalLength)
        else:
            self.excitationTrigger[uiIndex] = False

    def excitationIncrementChange(self, index):
        self.excitationSpinBoxs[index].setSingleStep(
            float(self.excitationIncrements[index].currentText()))
        
    def updateFocalLength(self, settingIndex, isUpper, uiIndex):
        if not self.focalLengthTrigger[uiIndex]:
            focalLength = round(self.focalLengthSpinBoxs[uiIndex].value(),2)
            formula = self.lenSetting[settingIndex].find("formula").text
            excitation = self.focalLengthToExcitation(formula, focalLength)
            v = round(excitation * self.anodeVoltage,2)
            if not self.voltageTrigger[uiIndex]:
                if not self.excitationTrigger[uiIndex]:
                    self.focalLengthTrigger[uiIndex] = True
                self.voltageSpinBoxs[uiIndex].setValue(v)
            else:
                self.voltageTrigger[uiIndex] = False
            if isUpper:
                self.cf_u[uiIndex] = focalLength
                self.update_u_lenses()
            else:
                self.cf_l[uiIndex-self.lowerIndex] = focalLength
                self.update_l_lenses()
        else:
            self.focalLengthTrigger[uiIndex] = False

    def focalLengthIncrementChange(self, index):
        self.focalLengthSpinBoxs[index].setSingleStep(
            float(self.focalLengthIncrements[index].currentText()))
        
    def updateAnodeVoltage(self):
        self.anodeVoltage = self.anodeVoltageSpinbox.value()
        for i in self.voltageUpdateFunctions:
            i()



    def __init__(self):
        super().__init__()
        self.initUI()

    # this function handles the closing of the pop-up window - it doesn't actually close, simply hides visibility.
    # this functionality allows for permanance of objects in the background

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # this function is called on main window shutdown, and it forces the popup to close+
    def shutdown():
        return sys.exit(True)
# the main program will instantiate the window once
# if it has been instantiated, it simply puts focus on the window instead of making a second window
# modifying this function can break the main window functionality


def main():
    global windowHandle
    windowHandle = popWindow()
    return windowHandle


# the showPopUp program will show the instantiated window (which was either hidden or visible)


def showPopUp():
    windowHandle.show()


if __name__ == '__main__':
    main()

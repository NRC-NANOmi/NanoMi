# -*- coding: utf-8 -*-

"""

@author: Suliat

kohler_probe_diameter.py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kohler_probe_diameter.py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kohler_probe_diameter.py.  If not, see <https://www.gnu.org/licenses/>.

See also https://github.com/NRC-NANOmi/NANOmi / nanomi.org

"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.colors import  Normalize

class ProbeSizeParameters:

    """
   Gives the diameter of probe achieved using Kohler illumination, based on the following formula by Zuo and Spence in
   Advanced Transmission Electron Microscopy: Imaging and Diffraction in Nanoscience (2017) (eq 10.1, pg 234):
         d = alpha * f_opl/ (M_C1 * M_C2),  where alpha is the angle subtended by the condenser aperture and M is the
         magnification of the respective lenses.
     Assumes a 3 lens condenser lens system, with an aperture placed just after 
     C1, between C1 and C2. Outputs a 3-D plot of the resulting probe size of each configuration. Uses the thin
     lens approximation. To use, after opening a python shell and importing the module:
        obj = ProbeSizeParameters(object_distance=a, aperture=b, s1=c, s2=d, fl1=e, fl2=f, step_size=g)
        obj.get_plot() #This gives the plot of the probe sizes
        obj.get_probe() # This gives the value of the probe size for a single point on x and y
        obj.get_variables() # This gives the value of the x and y for a given probe size or fl3, to a sensitivity of 1e-1

    Important: 2 of the following 4 variables must be tuples of equal length, containing the ranges to plot over:
            s1, s2, fl1, fl2
    The two values that are given as a tuple as opposed to a value will form the x and y axis, and probe size is
    plotted on z.

   Note: The value at fl1, fl2= zero is untrustworthy
   Note2: It is crucial that there are two ranges given, as this only outputs a 3d plot
   Note3: The upper bound of the range is excluded from the axis.
    """

    def __init__(self, object_distance,aperture, s1, s2, fl1, fl2, step_size):
        """
        Initializing this class creates an object that takes the following:
        object_distance (float): Object distance from the first lens, assumed to be the distance to the aperture. Units: Millimeters
        Aperture (float): The diameter of the aperture condenser lens system. In this case, the aperture is assumed to be
            placed after the first lens. Units: Micrometers
        s1 (float): Distance between the first and second lens. Units: Millimeters
        s2 (float): Distance between the second and third lens. Units: Millimeters
        fl1 (tuple): The focal length of the first lens. Units: Millimeters
        fl2 (tuple): The focal length of the second lens. Units: Millimeters
        step_size(float): The spacing between values

        Important: 2 of the following 5 must be tuples of equal length, containing the variable ranges to plot over:
        s1, s2, fl1, fl2, fl3
        Note that the upper bound of the range is excluded from the calculated focal lengths.
        """
        self.do1 = object_distance
        self.aperture = aperture
        self.step = step_size

        self.s1 = None
        self.s2 = None
        self.fl1 = None
        self.fl2 = None
        self.var1_range = None
        self.var2_range = None
        self.var1_name = None
        self.var2_name = None

        self._set_variables(s1, s2, fl1, fl2)

        self.var1_values_mesh = None
        self.var2_values_mesh = None
        self.probe_array = None
        self.fl3_array = None

    def _set_variables(self, s1, s2, fl1, fl2):
        """Set the field in the object, if the variable is not a tuple."""
        if not self._determine_range(s1):
            self.s1 = s1
        if not self._determine_range(s2):
            self.s2 = s2
        if not self._determine_range(fl1):
            self.fl1 = fl1
        if not self._determine_range(fl2):
            self.fl2 = fl2

    def _determine_range(self, variable):
        """Determine which variable to put on the x and y axis, based on the type of entry for the variable"""
        if type(variable) is tuple and self.var1_range is None:
            self.var1_range = variable
            return True
        elif type(variable) is tuple and self.var2_range is None:
            self.var2_range = variable
            return True
        else:
            return False


    def probe_calc(self):
        """
        Calculates the probe size after being demagnified through a series of lenses, in Kohler illumination. Assumes
        thin lens conditions. Also calculates the probe size, as well as the angle of the probe from the normal.
        """
        ##To calculate the magnification, the product of the magnification of the individual lenses is used, where the
        ##magnification of an individual lens is M = -(di/do)

        ## The probe size is calculated according to the following formula by Zuo and Spence in Advanced Transmission
        ## Electron Microscopy: Imaging and Diffraction in Nanoscience (2017):
        ## d = alpha * f_opl/ (M_C1 * M_C2) where alpha is the angle subtended by the condenser aperture and M is the
        ## magnification of the respective lenses.
        ## Alpha is calculated assuming that crossover takes place behind the image. As the probesize approaches zero,
        ## The probe crossover position moves closer to the image distance.

        #Convert the focal length and lens distances to millimetres
        do1 = self.do1*1e3
        s1 = self.s1*1e3
        s2 = self.s2*1e3
        fl2 = self.fl2*1e3
        fl1 = self.fl1*1e3

        di1 = ((1/fl1) - (1/do1))**(-1)
        mag_lens1 = -(di1/do1)

        do2 = s1 - di1
        di2 = ((1 / fl2) - (1 / do2))**(-1)
        mag_lens2 = -(di2/do2)

        fl3 = s2 - di2
        opp = self.aperture/2
        angle_alpha = np.arctan(opp*(1-mag_lens1)/di1)

        probe_size = (2 * angle_alpha * fl3)/(mag_lens1 * mag_lens2)
        return probe_size, fl3*1e-3

    def focal_array(self):
        """
        Calculate the probe size for the range of the inputs given on the x and y, where x and y refer to the axis'
        of the plot. Creates a 2d array of x values, y values, and a 2d array of probe sizes values to plot on the z
        axis
        """
        start1, stop1 = self.var1_range
        start2, stop2 = self.var2_range
        var1_values = np.arange(start1, stop1, self.step)
        var2_values= np.arange(start2, stop2, self.step)
        self.var1_values_mesh, self.var2_values_mesh = np.meshgrid(var1_values, var2_values)

        ranged_var1 = self._determine_ranged()
        ranged_var2 = self._determine_ranged()
        probe_list = []
        fl3_list = []

        for value1 in var1_values:
            self._set_value(ranged_var1, value1)
            var2_list = []
            fl3l = []
            for value2 in var2_values:
                self._set_value(ranged_var2, value2)
                probe, fl3 = self.probe_calc()
                var2_list.append(probe)
                fl3l.append(fl3)
            probe_list.append(var2_list)
            fl3_list.append(fl3l)
        self.probe_array = np.array(probe_list)
        self.fl3_array = np.array(fl3_list)

    def _determine_ranged(self):
        """
        Determine which variables are currently none- those are the variables on the x and y axis
        :return: the variable which is none
        """
        ##A weakness in the private methods is that it relies HEAVILY on the order that these if statements are executed
        ##to assign the correct range to the correct variable. I don't know how to make a more robust linker between the two.

        if self.s1 is None:
            self.s1 = 'determined'
            if self.var1_name is None:
                self.var1_name = 'distance between lens 1 and 2'
            elif self.var2_name is None:
                self.var2_name = 'distance between lens 1 and 2'
            return 's1'
        elif self.s2 is None:
            self.s2 = 'determined'
            if self.var1_name is None:
                self.var1_name = 'distance between lens 2 and 3'
            elif self.var2_name is None:
                self.var2_name = 'distance between lens 2 and 3'
            return 's2'
        elif self.fl1 is None:
            self.fl1 = 'determined'
            if self.var1_name is None:
                self.var1_name = 'focal_length_1'
            elif self.var2_name is None:
                self.var2_name = 'focal_length_1'
            return 'fl1'
        elif self.fl2 is None:
            self.fl2 = 'determined'
            if self.var1_name is None:
                self.var1_name = 'focal_length_2'
            elif self.var2_name is None:
                self.var2_name = 'focal_length_2'
            return 'fl2'
        else:
            raise ValueError('There was an issue assigning the ranged variables')

    def _set_value(self, var, value):
        """
        Set the variable being looped over so that it can be calculated in probe_calc
        :param var: (string) the variable that is either on the x or y axis
        :param value: (float) the current value that the probe size is being calculated for
        """
        if var is 's1':
            self.s1 = value
        elif var is 's2':
            self.s2 = value
        elif var is 'fl1':
            self.fl1 = value
        elif var is 'fl2':
            self.fl2 = value
        else:
            raise ValueError('There was an issue assigning the ranged variables')

    def plot_focal(self):
        """
        plot the probe size. the x and y axis variables depend on which variables were given as ranges, and the z
        axis is the probe size at that point
        """
        x = self.var1_values_mesh.T
        y = self.var2_values_mesh.T
        z = self.probe_array

        fig = plt.figure()
        ax = fig.gca(projection = '3d')
        ax.plot_surface(x,y,z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        plt.xlabel(self.var1_name)
        plt.ylabel(self.var2_name)
        ax.set_zlabel('Probe Size (um)')
        plt.show()

    def get_fl3(self, var1, var2):
        """Get the focal length of the third condenser lens for an x and y that has been computed given the range of
        inputs and the step size of the range."""
        x1, x2 = np.where(np.isclose(self.var1_values_mesh, var1))
        y1, y2 = np.where(np.isclose(self.var2_values_mesh, var2))
        var1_index = x2[0]
        var2_index = y1[0]
        fl3 = self.fl3_array[var1_index, var2_index]
        return fl3

    def get_probe(self, var1, var2):
        """Get probe size generated by the condenser for an x and y that has been computed given the range of
        inputs and the step size of the range."""
        x1, x2 = np.where(np.isclose(self.var1_values_mesh, var1))
        y1, y2 = np.where(np.isclose(self.var2_values_mesh, var2))
        var1_index = x2[0]
        var2_index = y1[0]
        probe = self.probe_array[var1_index, var2_index]
        return probe

    def get_variables(self, parameter, param_name='probe'):
        """
        Get the x and y coordinates for a given probe size or C3 focal length that has been computed.
        :param parameter: (float) The probe size or the C3 focal length for which the x and y coordinates has to be retrieved
        :param param_name: (string) The parameter type that is entered. Can be 'probe' or 'fl3'
        :return: Returns the potential x and y values that return the desired parameter
        """
        if param_name is 'fl3':
            x1, x2 = np.where(np.isclose(self.fl3_array, parameter, atol=1e-1))
        elif param_name is 'probe':
            x1, x2 = np.where(np.isclose(self.probe_array, parameter, atol=1e-1))
        else:
            raise ValueError('Parameter name is not supported')

        var1_list = self.var1_values_mesh[0][x1]
        var2_list = self.var2_values_mesh.T
        var2_list = var2_list[0][x2]

        coord_list = []
        for i in range(len(x1)):
            coord = (var1_list[i], var2_list[i])
            coord_list.append(coord)
        return coord_list

    def get_value_between(self, range, param_name='probe'):
        """
        Finds either the probe sizes or the C3 focal lengths computed and available within the given range.
        :param range: (tuple) The lowest and highest value to be considered.
        :param param_name: (string) The parameter type that is returned. Can be 'probe' or 'fl3'
        :return: A list of probe sizes or C3 focal lengths with value within range. Empty if no such value was computed.
        """
        if param_name is 'fl3':
            obj_array = self.fl3_array
        elif param_name is 'probe':
            obj_array = self.probe_array
        else:
            raise ValueError('Parameter name is not supported')

        begin, end = range
        less_than = obj_array[obj_array >= begin]
        between = less_than[less_than <= end]
        return between


    def acceptable_fl3(self, range, min_fl):
        """ Outputs a list of coordinates which give rise to a probe size within the range specified, such that the
        focal length of the third lens is greater than a given minimum focal length.

        :param min_fl: (float) The minimum focal length of lens 3
        :param range: (tuple of floats) The range of desired probe sizes
        :return:A list of tuples containing the coordinates which give the desired probe size and satisfy the minimum fl3
        """
        value_list= self.get_value_between(range, param_name='probe')
        coord_list = []

        for value in value_list:
            var_list=self.get_variables(value, param_name='probe')
            for variable in var_list:
                var1, var2 = variable
                fl3=self.get_fl3(var1, var2)
                if fl3 >= min_fl:
                    coord_list.append(variable)
        return coord_list


    def get_plot(self):
        if self.var1_values_mesh is None:
            self.focal_array()
        self.plot_focal()

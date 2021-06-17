# -*- coding: utf-8 -*-

"""

@author: Suliat

TEM_imaging_column.py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TEM_imaging_column.py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TEM_imaging_column.py.  If not, see <https://www.gnu.org/licenses/>.

See also https://github.com/NRC-NANOmi/NANOmi / nanomi.org

"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
from matplotlib import cm
from scipy import optimize
from matplotlib.widgets import Slider, Button, RadioButtons

class ImagingColumnParameters:

    """
   Works according to a n-lens optical system. Outputs a 3-D plot of the system magnification. Uses the thin lens
   approximation. To use, after opening a python shell and importing the module:
        obj = ImagingColumnParameters(fl2_gap=a, fln_gap=b, fl2=c, fln=d, step_size=e)
        obj.get_plot() #This gives the plot of the magnifications
        obj.get_magsys() # This gives the value of the magnification for a single point on x and y
        obj.get_syscoords() # Gives the x coordinates of each lens in succession, with the stage at x=0
        obj.get_variables() # This gives the value of the x and y for a given magnification, to a sensitivity of 1e-1

    Important: 2 of the following 4 must be tuples of equal length, containing the variable ranges to plot over:
        fl2_gap, fln_gap, fl2, fln
    The two values that are given as a tuple as opposed to a value will form the x and y axis, and magnification is
    plotted on z.

   Note: The value at fl2, fln= zero is untrustworthy
   Note2: It is crucial that there are two ranges given, as this only outputs a 3d plot
   Note3: The upper bound of the range is excluded from the axis. So if the range given is from (1,5), with a step size
   of 0.1, then values for up to 4.9 will be calculated. 5 is out of bounds.
    """
    SYS_HEIGHT = 600
    STAGE_DISTANCE = 20
    DISTANCE_BW_LENSES = 50

    def __init__(self, fl2_gap, fln_gap, fl2, fln, step_size):
        """
        Initializing this class creates an object that takes the following:
        fl2_gap (tuple or float): Difference between the object distance and the focal length of the second lens(in millimeters)
        fln_gap (tuple or float): Difference between the object distance and the focal length of the 3...n lenses (in millimeters)
        fl2 (tuple or float): The focal length of the second lens
        fln (tuple or float): The focal length third, fourth,...nth lens in the system. Note that all those lenses have
        the same focal length
        step_size(float): The spacing between values.

        Important: 2 of the following 4 must be tuples of equal length, containing the variable ranges to plot over:
            fl2_gap, fln_gap, fl2, fln
        Note that the upper bound of the range is excluded from the calculated focal lengths.
        """
        self.step = step_size

        self.fl2_gap = None
        self.fln_gap = None
        self.fl2 = None
        self.fln = None
        self.var1_range = None
        self.var2_range = None
        self.var1_name = None
        self.var2_name = None

        self._set_variables(fl2_gap, fln_gap, fl2, fln)

        self.var1_values_mesh = None
        self.var2_values_mesh = None
        self.mag_sys_array = None
        self.sys_coord_array = None

    def _set_variables(self, fl2_gap, fln_gap, fl2, fln):
        """Set the field with the appropriate constant in the object, if the variable is not a tuple. If the variable is
            a tuple, enters that value into either var1 or var2 (the x and y axis, not respectively). Order dependent-
            the first of the above listed variables that is a tuple will be var1, and the second will be var2."""
        if not self._determine_range(fl2_gap):
            self.fl2_gap = fl2_gap
        if not self._determine_range(fln_gap):
            self.fln_gap = fln_gap
        if not self._determine_range(fl2):
            self.fl2 = fl2
        if not self._determine_range(fln):
            self.fln = fln

    def _determine_range(self, variable):
        """Determine which variable is placed on the x and y axis. The fields corresponding to x and y are var1 and var2"""
        if type(variable) is tuple and self.var1_range is None:
            self.var1_range = variable
            return True
        elif type(variable) is tuple and self.var2_range is None:
            self.var2_range = variable
            return True
        else:
            return False

    def sys_calc(self):
        """ Calculates the coordinates of the lenses in a system, as well as the magnification for a system with the
        specifications entered.
        """
        #Calculating the magnification of the first lens in the system
        mag1= -(self.DISTANCE_BW_LENSES - self.fl2_gap - self.fl2)/self.STAGE_DISTANCE

        #Calculating the magnfication of the second lens in the system
        di2 = (1 / self.fl2 - 1 /(self.fl2 + self.fl2_gap)) ** (-1)
        mag2 = -di2/(self.fl2 + self.fl2_gap)

        #Calculating the space left in the column after the stage image has been magnified by the first two lenses
        B = self.SYS_HEIGHT - di2 - self.fln - self.fln_gap - (self.DISTANCE_BW_LENSES + self.STAGE_DISTANCE)

        #Calculating the space between the remaining lenses
        diN = (1 / self.fln - 1 / (self.fln + self.fln_gap)) ** (-1)
        A = self.fln + self.fln_gap + diN

        #Finding the number of lenses in the system, excluding the first two
        numN = (B//A)

        #Computing the magnification of the lenses3...n
        magN= -(((self.fln + self.fln_gap)/self.fln)-1)**(-1)

        #Calculating the total magnification of the system
        mag_sys = mag1* mag2*(magN**numN)

        #Calculating the x coordinates of each lens, with the stage at x=0
        xlens1 = self.STAGE_DISTANCE
        xlens2 = xlens1 + self.DISTANCE_BW_LENSES
        xlens3 = xlens2 + di2 + self.fln + self.fln_gap
        sys_coords = [xlens1, xlens2, xlens3]

        for i in range(int(numN-1)):
            xlens = sys_coords[-1] + A
            sys_coords.append(xlens)

        return mag_sys, tuple(sys_coords)

    def calc_array(self):
        """
        Calculate the magnification and system coordinates for the range of the inputs given on the x and y, where x and
        y refer to the axes of the plot. Creates a 2d array of x values, y values, and a 2d array of magnification
        values to plot on the z axis
        """
        start1, stop1 = self.var1_range
        start2, stop2 = self.var2_range
        var1_values = np.arange(start1, stop1, self.step)
        var2_values = np.arange(start2, stop2, self.step)
        self.var1_values_mesh, self.var2_values_mesh = np.meshgrid(var1_values, var2_values)

        ranged_var1 = self._determine_ranged()
        ranged_var2 = self._determine_ranged()
        mag_syslist = []
        sys_coordlist = []

        for value1 in var1_values:
            self._set_value(ranged_var1, value1)
            var2_list = []
            coord_list = []
            for value2 in var2_values:
                self._set_value(ranged_var2, value2)
                mag_sys, sys_coord=self.sys_calc()
                var2_list.append(mag_sys)
                coord_list.append(sys_coord)
            mag_syslist.append(var2_list)
            sys_coordlist.append(coord_list)
        self.mag_sys_array = np.array(mag_syslist)
        self.sys_coord_array = np.array(sys_coordlist)

    def _determine_ranged(self):
        """
        Determine which variables are currently none- those are the variables on the x and y axis
        :return: the variable which is none
        """
        ##A weakness in the private methods is that they rely HEAVILY on the order that these if statements are executed
        ##to assign the correct range to the correct variable. I don't know how to make a more robust linker between the two.

        if self.fl2_gap is None:
            self.fl2_gap = 'determined'
            if self.var1_name is None:
                self.var1_name = 'focal_length_gap2 (mm)'
            elif self.var2_name is None:
                self.var2_name = 'focal_length_gap2 (mm)'
            return 'fl2_gap'
        elif self.fln_gap is None:
            self.fln_gap = 'determined'
            if self.var1_name is None:
                self.var1_name = 'focal_length_gapN (mm)'
            elif self.var2_name is None:
                self.var2_name = 'focal_length_gapN (mm)'
            return 'fln_gap'
        elif self.fl2 is None:
            self.fl2 = 'determined'
            if self.var1_name is None:
                self.var1_name = 'focal_length_lens2 (mm)'
            elif self.var2_name is None:
                self.var2_name = 'focal_length_lens2 (mm)'
            return 'fl2'
        elif self.fln is None:
            self.fln = 'determined'
            if self.var1_name is None:
                self.var1_name = 'focal_length_N (mm)'
            elif self.var2_name is None:
                self.var2_name = 'focal_length_N (mm)'
            return 'fll_rest'
        else:
            ##Throw an exception
            return 'there was an issue assigning the variables. Ranged'

    def _set_value(self, var, value):
        """
        Set the variable being looped over so that it can be calculated in the magnification
        :param var: (string) the variable that is either on the x or y axis
        :param value: (float) the current value that the magnification is being calculated for
        """
        if var is 'fl2_gap':
            self.fl2_gap = value
        elif var is 'fln_gap':
            self.fln_gap = value
        elif var is 'fl2':
            self.fl2 = value
        elif var is 'fln':
            self.fln = value
        else:
            ##Throw an exception
            print('there was an issue assigning the variables.Set_value')

    def plot_calc(self):
        """
        Plot the magnification. the x and y axis variables depend on which variables were given as ranges, and the z
        axis is the magnification at that point
        """
        x = self.var1_values_mesh.T
        y = self.var2_values_mesh.T
        z = self.mag_sys_array

        fig = plt.figure()
        ax = fig.gca(projection = '3d')
        ax.plot_surface(x,y,z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        ax.set_xlabel(self.var1_name)
        ax.set_ylabel(self.var2_name)
        ax.set_zlabel('Magnification')
        plt.show()

    def get_magsys(self, var1, var2):
        """
        Get magnification of the system at a given point- for a x and y that has been computed given the range of
        inputs and the step size of the range.
        """
        x1, x2 = np.where(np.isclose(self.var1_values_mesh, var1))
        y1, y2 = np.where(np.isclose(self.var2_values_mesh, var2))
        var1_index = x2[0]
        var2_index = y1[0]
        mag = self.mag_sys_array[var1_index, var2_index]
        return mag

    def get_syscoords(self, var1, var2):
        """
        Get x coordinates of the system for an x and y that has been computed given the range of inputs and the step
        size of the range. x = 0 is the position of the microscope, the source to be magnified.
        """
        x1, x2 = np.where(np.isclose(self.var1_values_mesh, var1))
        y1, y2 = np.where(np.isclose(self.var2_values_mesh, var2))
        var1_index = x2[0]
        var2_index = y1[0]
        coords = self.sys_coord_array[var1_index, var2_index]
        return coords

    def get_variables(self, mag_sys):
        """Get the x and y coordinates for a given magnification that has been computed"""
        x1, x2 = np.where(np.isclose(self.mag_sys_array, mag_sys, atol=1e-1))

        var1_list = self.var1_values_mesh[0][x1]
        var2_list = self.var2_values_mesh.T
        var2_list = var2_list[0][x2]

        coord_list = []
        for i in range(len(x1)):
            coord = (var1_list[i], var2_list[i])
            coord_list.append(coord)
        return coord_list

    def get_plot(self):
        if self.var1_values_mesh is None:
            self.calc_array()
        self.plot_calc()

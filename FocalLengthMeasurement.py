'''
 FocalLengthMeasurement.py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    FocalLengthMeasurement.py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
'''
This code is used for estimating the focal length of the electrostatic lens shown in Fig.2 of Rempfer's 1985 paper on electrostatic lenses.
The calculation uses the formulas derived in Rempfer's 1985 paper to estimate the focal length. It requires a spreadsheet of measurements
of images of shadows of the second grid on the screen. This script only works for the case where the beam intersects the optical axis before it
hits the second lens. If the beam intersects the optical axis after the second lens, modifications need to be made to the equations.
The spreadsheet should be in the format as shown in TopGridMeasurements.csv. 
Unfortunately, this script currently does not provide accurate results with the data we have taken.

'''
#constants
#Variables named after Rempfer's 1985 paper
top_grid_fname="TopGridMeasurements.csv" #csv file containing measurements of the top mesh grid
top_grid_data=np.loadtxt(top_grid_fname, delimiter=',', skiprows=1)

'''Column dimensions taken fron CAD files, lengths are expressed in meters'''
a =4.245*(2.54/100) #distance from source to front grating
d = 663/1000 #distance from back grating to screen
e2 = 120e-6 # spacing of back grating, labelled as e' in Rempfer's paper
z= 9.131*(2.54/100)  #distance from source to lens 
b= 12.903*(2.54/100)-z #distance from lens to back grating


E2 = (2.54/100)*top_grid_data[:,6] #  array of back shadow length, converted to meters 

V_gun = top_grid_data[:,1] # Array of gun voltage in V
V_lens = top_grid_data[:,3]# Array of lens voltage in V
V_ratio = np.divide(V_lens,V_gun) # array of voltage ratio


def find_e1(E): #Finds what e1 is in terms of the shadow spacing measured on the screen
    z_prime=image_source(E)
    tan_alpha_prime=E/((b-z_prime)+d)
    e1=a*z_prime*tan_alpha_prime/z
    return e1

def image_source(E): #determines the location of the image source given , labelled as z' in Rempfer's paper
    M_prime = E/e2 # back grating magnification
    z_prime = b - (d/(M_prime-1))
    return z_prime
    

# function for finding image magnification m

def image_magnification(E, image): #finds the image magnification given the spacing of the image of the front and back grid
    e1=find_e1(E)
    M = E/e1 #front magnification
    M_prime = E/e2 #back magnification
   
    m = (M/M_prime)*((b-image)/a)
    return m


def focal_length(image,mag): #calculates focal length using the values for image location and magnification
    F = (z-image)/((1/mag)-mag)
    return F


#Curve Fitting (currently not used)
guesses = (0,1,1,1,1) #Initial guesses for fitting parameters
def fit_function(x, c0, c1, c2,c3,c4): #Fit function we will be using to approximate the measured data
    return  c0+c1*x+c2*x**2+c3*x**3+c4*x**4


z_prime=image_source(E2)
m=image_magnification(E2,image_source(E2))
x_data=V_ratio #The values for the lens voltage from our measured datapoints
y_data=focal_length(z_prime,m) #Focal length values from our measured datapoints

fit_params,fit_cov = curve_fit(fit_function,x_data,y_data,p0=guesses,maxfev=10**5)
x_fit=np.linspace(np.min(V_ratio),1,num=50)
y_fit= fit_function(x_fit,*fit_params)

param_names = ['c0','c1','c2','c3','c4']
print ("Fit parameters:")
for i in range(len(fit_params)):
    print ('{} = {:.3e}'.format(param_names[i],fit_params[i]))

#Plotting
   
plt.figure()
plt.plot(x_data,y_data, 'bo') # Plots focal length vs voltage ratio
#plt.plot(x_fit,y_fit,'r-') #Plots the best fit plot (in case it ever becomes useful)

plt.ylabel("focal length (m)")
plt.xlabel("voltage ratio")
plt.title("Focal length vs Voltage ratio")

plt.show()




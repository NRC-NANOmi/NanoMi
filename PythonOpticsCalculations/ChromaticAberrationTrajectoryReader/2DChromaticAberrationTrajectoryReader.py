"""
 2DChromaticAberrationTrajectoryReader.py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
"""
'''
This code is used to calculate the chromatic aberration coefficient and paraxial focal length of the data by performing calculations on text files exported from 
the 2D axial-symmetric ray tracing simulations in COMSOL (The COMSOL simulations involves shooting paraxial rays at different accelerating voltages). 
The exact procedures used to extract the data from COMSOL and format it properly in Excel are listed in the "COMSOL Simulation Instructions" in the NanoMi Google Drive. 
This python file must be at the top of the folder, alphabetically, and requires multiple csv files within the folder to calculate the chromatic aberration. 
Make sure to correctly modify the path where this file is placed.
'''
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#Lens dimensions

Outer_electrode_thickness_scale=1
Electrode_gap_scale=1
Center_electrode_thickness_scale=1
Center_electrode_aperture_radius_scale=1
Outer_electrode_aperture_radius_scale=1
max_allowed_angle=1

Electrode_1_start_pos=5.08e-3 #17.4625e-3
Outer_electrode_thickness=Outer_electrode_thickness_scale*3.96875e-3
Outer_electrode_aperture_radius=(Outer_electrode_aperture_radius_scale*2.54e-3)/2
Electrode_gap=Electrode_gap_scale*4.445e-3
Center_electrode_start_pos=Electrode_1_start_pos+Outer_electrode_thickness+Electrode_gap
Center_electrode_thickness=Center_electrode_thickness_scale*5.08e-3
Lens_center_position=Center_electrode_start_pos+Center_electrode_thickness/2
Center_electrode_aperture_radius=(Center_electrode_aperture_radius_scale*6.35e-3)/2
Electrode_3_start_pos=Center_electrode_start_pos+Center_electrode_thickness+Electrode_gap
Lens_length=0.05 #Length of the einzel lens

#Cropping a specific part of the E field array
x_min=0 #These four variables determine the x,y range that is being cropped from original potential/Efield plot (in m)
x_max=Center_electrode_aperture_radius
y_min=0
y_max=3.4e-2


list_of_trajectory=[]
convergence_angle_list=[]
electron_energy_array=np.linspace(49900,50100,num=20) #These are the accelerating voltages that are used in COMSOL simulations.
electron_energy_spread_array=np.subtract(electron_energy_array,50000)

path='D:\\Sean\\NINT\\COMSOL\\RayTracing\\COMSOL_Ray_Tracing\\Files\\ChromaticAberration\\Config1CcTrajectories' #This is the file path where this file and the csv files from COMSOL simulations are to be placed

for i in range(1,len(os.listdir(os.getcwd()))): #Loops over all files in the directory
    fname=(os.listdir(os.getcwd()))[i] #The csv file containing info on the electric field
    data=np.float64(np.loadtxt(fname, delimiter=',', skiprows=9, usecols=(0,1,2,4,5))) #Opens the csv file and converts it into an array
    data[:,0]=data[:,0]*(2.54/100) #converts length measurements from inches to meters
    data[:,1]=data[:,1]*(2.54/100)
    filtered_data=data[(data[:,0]>=x_min) & (data[:,0]<=x_max) & (data[:,1]>=y_min) & (data[:,1]<=y_max)] #Crops the array

    N_particles=len(os.listdir(os.getcwd())) #The number of different energies that the paraxial ray electron has. It is just the number of files in the current folder

    convergence_angle=np.arctan(np.divide(filtered_data[(filtered_data[:,2]==0)][:,3][-1],filtered_data[(filtered_data[:,2]==0)][:,4][-1]))
    list_of_trajectory.append(filtered_data)
    convergence_angle_list.append(np.abs(np.arctan(np.divide(filtered_data[(filtered_data[:,2]==0)][:,3][-1],filtered_data[(filtered_data[:,2]==0)][:,4][-1]))))
    
N_paraxial_ray=int(N_particles*0.5)-1
Intersection_with_original_ray=list_of_trajectory[N_paraxial_ray][np.abs(list_of_trajectory[N_paraxial_ray][:,0]).argmin()][1]-(list_of_trajectory[N_paraxial_ray][0,0]/np.tan(convergence_angle_list[N_paraxial_ray]))
paraxial_focal_length=list_of_trajectory[N_paraxial_ray][np.abs(list_of_trajectory[N_paraxial_ray][:,0]).argmin()][1]-Intersection_with_original_ray

x_data=np.divide(electron_energy_spread_array,electron_energy_array)

axial_shift_list=[]
    
for i in range(len(list_of_trajectory)):
    marginal_focal_length=list_of_trajectory[i][np.abs(list_of_trajectory[i][:,0]).argmin()][1]-Intersection_with_original_ray
    axial_shift_list.append(paraxial_focal_length-marginal_focal_length)
    
y_data=axial_shift_list
    
#Electrode positions displayed in plotting
electrode_1_x=np.linspace(Outer_electrode_aperture_radius,Outer_electrode_aperture_radius,num=100)
electrode_1_y=np.linspace(Electrode_1_start_pos, Electrode_1_start_pos+Outer_electrode_thickness,num=100)
electrode_2_x=np.linspace(Center_electrode_aperture_radius,Center_electrode_aperture_radius,num=100)
electrode_2_y=np.linspace(Center_electrode_start_pos,Center_electrode_start_pos+Center_electrode_thickness,num=100)
electrode_3_x=np.linspace(Outer_electrode_aperture_radius,Outer_electrode_aperture_radius,num=100)
electrode_3_y=np.linspace(Electrode_3_start_pos,Electrode_3_start_pos+Outer_electrode_thickness,num=100)  

plt.figure()
plt.subplot(221)
plt.plot(electrode_1_x,electrode_1_y,'r-') #plots the edges of electrode 1
plt.plot(electrode_2_x,electrode_2_y,'r-') #plots the edges of electrode 2
plt.plot(electrode_3_x,electrode_3_y,'r-') #plots the edges of electrode 3
for i in range(len(list_of_trajectory)):
    plt.plot(list_of_trajectory[i][:,0],list_of_trajectory[i][:,1],'b-')
    
plt.xlabel('Radial distance(m)')
plt.ylabel('Axial distance(m)')
plt.title('Trajectory plot for trajectories with Alpha<='+str(max_allowed_angle)+'rad')

#Curve Fitting
guesses = (1, 0) #Initial guesses for fitting parameters
def fit_function(x, m, b):
    return  m*x+b



fit_params,fit_cov = curve_fit(fit_function,x_data,y_data,p0=guesses,maxfev=10**5)
y_fit= fit_function(x_data,*fit_params)
plt.subplot(222)
plt.plot(x_data,y_data, 'bo')
plt.plot(x_data,y_fit,'r-') #Plots the fitted curve
plt.xlabel("Energy spread/Energy")
plt.ylabel("Axial shift(m)")
plt.title("Axial shift vs (Energy spread/Energy)")

param_names = ['Chromatic aberration coefficient(m)','y intercept(m)']
print ("Fit parameters:")
for i in range(len(fit_params)):
    print ('{} = {:.3e}'.format(param_names[i],fit_params[i]))
print("Paraxial focal length (m)= "+str(paraxial_focal_length))
plt.show()

